import re
import sys
from pathlib import Path
from types import SimpleNamespace

import hydra
import omegaconf as omgcf


_STEP_RE = re.compile(r"_step_(\d+)\.pt$")


def _extract_cli_args(argv: list[str]) -> SimpleNamespace:
    """Accept small play-script args while still allowing Hydra-style overrides."""
    cleaned = [argv[0]]
    hydra_overrides: list[str] = []
    run_dir = None
    model_step = None
    replay_buffer_step = None

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in ("--run-dir", "--path"):
            run_dir = argv[i + 1]
            i += 2
        elif arg.startswith("--run-dir="):
            run_dir = arg.split("=", 1)[1]
            i += 1
        elif arg.startswith("--path="):
            run_dir = arg.split("=", 1)[1]
            i += 1
        elif arg == "--model-step":
            model_step = argv[i + 1]
            i += 2
        elif arg.startswith("--model-step="):
            model_step = arg.split("=", 1)[1]
            i += 1
        elif arg == "--replay-buffer-step":
            replay_buffer_step = argv[i + 1]
            i += 2
        elif arg.startswith("--replay-buffer-step="):
            replay_buffer_step = arg.split("=", 1)[1]
            i += 1
        elif "=" in arg and not arg.startswith("--"):
            hydra_overrides.append(arg)
            i += 1
        else:
            cleaned.append(arg)
            i += 1

    sys.argv[:] = cleaned
    return SimpleNamespace(
        hydra_overrides=hydra_overrides,
        run_dir=run_dir,
        model_step=model_step,
        replay_buffer_step=replay_buffer_step,
    )


def _looks_unset(path_value: object) -> bool:
    if path_value is None:
        return True
    path_text = str(path_value).strip()
    if not path_text or path_text.lower() in ("latest", "auto"):
        return True
    lowered = path_text.lower()
    return "path to your" in lowered or ".. directory" in lowered


def _artifact_step(path: Path) -> int:
    match = _STEP_RE.search(path.name)
    if match is None:
        raise ValueError(f"Cannot parse training step from {path}")
    return int(match.group(1))


def _find_latest_run(repo_root: Path) -> Path:
    candidates: list[tuple[float, Path]] = []
    exp_roots = sorted({path for path in repo_root.glob("exp_*") if path.is_dir()})

    for exp_root in exp_roots:
        for hydra_config in exp_root.rglob("hydra_config.yaml"):
            run_dir = hydra_config.parent
            model_files = list((run_dir / "models").glob("model_step_*.pt"))
            if model_files:
                latest_model = max(model_files, key=_artifact_step)
                candidates.append((latest_model.stat().st_mtime, run_dir))

    if not candidates:
        raise FileNotFoundError(
            "No trained FB run found under exp_*/. Pass one explicitly with "
            "`--run-dir /path/to/run`."
        )

    return max(candidates, key=lambda item: item[0])[1]


def _resolve_run_dir(path_value: object, repo_root: Path) -> Path:
    if _looks_unset(path_value):
        return _find_latest_run(repo_root)

    path = Path(str(path_value)).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    path = path.resolve()

    if path.is_file() and path.name.startswith("model_step_"):
        return path.parent.parent
    if path.is_file() and path.name == "hydra_config.yaml":
        return path.parent
    if path.name == "models" and (path.parent / "hydra_config.yaml").is_file():
        return path.parent
    if (path / "hydra_config.yaml").is_file() and (path / "models").is_dir():
        return path

    raise FileNotFoundError(
        f"Could not resolve FB run directory from `{path}`. Expected a run directory "
        "containing `hydra_config.yaml` and `models/`, or a `model_step_*.pt` file."
    )


def _step_value(value: object, fallback: object = "latest") -> object:
    if value is None:
        return fallback
    if isinstance(value, str) and value.strip().lower() in ("", "latest", "none"):
        return "latest"
    return value


def _select_artifact(models_dir: Path, prefix: str, step: object) -> Path:
    artifacts = list(models_dir.glob(f"{prefix}_step_*.pt"))
    if not artifacts:
        raise FileNotFoundError(f"No `{prefix}_step_*.pt` files found in {models_dir}")

    step = _step_value(step)
    if step == "latest":
        return max(artifacts, key=_artifact_step)

    step_int = int(step)
    artifact = models_dir / f"{prefix}_step_{step_int}.pt"
    if not artifact.is_file():
        available = ", ".join(str(_artifact_step(path)) for path in sorted(artifacts, key=_artifact_step))
        raise FileNotFoundError(
            f"Missing `{artifact.name}`. Available {prefix} steps: {available}"
        )
    return artifact


def load_play_configs(
    config_dir: str | Path,
    config_name: str = "Isaaclab_fb_play_config_base",
    *,
    require_replay_buffer: bool = True,
):
    cli_args = _extract_cli_args(sys.argv)
    config_dir = Path(config_dir).resolve()
    repo_root = config_dir.parents[3]

    with hydra.initialize_config_dir(config_dir=str(config_dir), version_base="1.1"):
        play_cfg = hydra.compose(config_name=config_name, overrides=cli_args.hydra_overrides)

    if cli_args.run_dir is not None:
        play_cfg.path = cli_args.run_dir
    if cli_args.model_step is not None:
        play_cfg.model_step = cli_args.model_step
    if cli_args.replay_buffer_step is not None:
        play_cfg.replay_buffer_step = cli_args.replay_buffer_step

    run_dir = _resolve_run_dir(getattr(play_cfg, "path", None), repo_root)
    play_cfg.path = str(run_dir)

    hydra_cfg = omgcf.OmegaConf.load(run_dir / "hydra_config.yaml")
    device_override = getattr(play_cfg.env, "device", None)
    if device_override not in (None, "", "training"):
        hydra_cfg.env.device = device_override
    omgcf.OmegaConf.resolve(hydra_cfg)

    models_dir = run_dir / "models"
    model_step = _step_value(getattr(play_cfg, "model_step", None))
    model_path = _select_artifact(models_dir, "model", model_step)

    replay_buffer_path = None
    if require_replay_buffer:
        replay_step = _step_value(getattr(play_cfg, "replay_buffer_step", None), _artifact_step(model_path))
        replay_buffer_path = _select_artifact(models_dir, "replay_buffer", replay_step)

    print(f"[FB play] run directory: {run_dir}", flush=True)
    print(f"[FB play] model: {model_path.name}", flush=True)
    if replay_buffer_path is not None:
        print(f"[FB play] replay buffer: {replay_buffer_path.name}", flush=True)

    return play_cfg, hydra_cfg, model_path, replay_buffer_path
