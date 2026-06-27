# FB-MEBE Development Notes

This document is for maintainers and future coding agents changing this repository.

## Ground Rules For Changes

- Treat generated training output as disposable unless the user explicitly asks to preserve it.
- Do not commit real W&B API keys or cluster credentials. `docker/cluster/.env.cluster` contains placeholders and is the only checked-in cluster env file.
- Keep FB training changes grounded in the existing flow: Hydra config, Isaac Lab task config, `FB_VecEnvWrapper`, `DictBuffer`, FB agent, checkpoint loader.
- Prefer adding config fields over hard-coded local paths when changing run-time behavior.
- Do not weaken validation by skipping assertions or swallowing errors unless the user explicitly asks for a temporary diagnostic patch.

## Environment

The project conda environment is `fb-mebe`:

```bash
conda activate fb-mebe
```

The repository does not include a full lockfile. Setup information is split across:

| File | What it verifies |
| --- | --- |
| `README.md` | Current project install sequence and Torch workaround. |
| `source/isaaclab/setup.py` | `isaaclab` package dependencies and Python `>=3.10`. |
| `source/isaaclab_tasks/setup.py` | `isaaclab_tasks` dependencies. |
| `source/isaaclab_rl/setup.py` | RL dependencies and extras such as `rsl-rl`. |
| `docker/.env.base` | Docker Isaac Sim version `4.5.0`. |

Needs verification: the exact package set in the local `fb-mebe` environment cannot be reconstructed from checked-in files alone.

## Formatting And Linting

The repo uses pre-commit hooks configured in `.pre-commit-config.yaml`:

```bash
./isaaclab.sh --format
```

Equivalent direct command:

```bash
pre-commit run --all-files
```

Configured hooks include Black, Flake8, isort, pyupgrade, codespell, license insertion, and RST checks. `.flake8` sets max line length to `120`, max complexity to `30`, and ignores `E402`, `E501`, `W503`, `E203`, `D401`, `R504`, `R505`, `SIM102`, `SIM117`, and `SIM118`.

First-time pre-commit runs may need network access to install hook environments.

## Tests

Most tests launch Isaac Sim and are not lightweight unit tests. Run them from an environment that can import Isaac Sim and access the requested device.

Examples:

```bash
python source/isaaclab_tasks/test/test_environments.py
python source/isaaclab_tasks/test/test_environment_determinism.py
python source/isaaclab_tasks/test/test_record_video.py
python source/isaaclab_assets/test/test_valid_configs.py
python source/isaaclab/test/controllers/test_differential_ik.py
```

Needs verification: `./isaaclab.sh --test` currently references `tools/run_all_tests.py`, but no top-level `tools/` directory exists. Until that helper is restored, run individual test files directly.

## Documentation Checks

This documentation is plain Markdown. There is no checked-in Markdown linter.

Before claiming docs are complete, verify:

```bash
test -f README.md
test -f docs/architecture.md
test -f docs/usage.md
test -f docs/development.md
```

Also check every documented path that was added or changed.

Needs verification: `.github/workflows/docs.yaml` is an upstream Sphinx workflow. It expects `docs/requirements.txt` and `make current-docs`, but this checkout did not contain a top-level Sphinx docs tree before this documentation pass.

## Safe Edit Map

| Change type | Primary files |
| --- | --- |
| Add or rename Go2 task IDs | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` |
| Change Go2 base observation/action/reward behavior | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py` |
| Change Go2 randomization or dimensions | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py`, `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_rnd_full.py`, `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_inc/go2_cfg_rnd_full_incremental.py`, `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_KAIST_abs/go2_cfg_KAIST.py` |
| Change incremental control | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_inc/go2_env_incremental.py` |
| Change KAIST gait/barrier variant | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_KAIST_abs/go2_env_KAIST.py` |
| Change FB train defaults | `scripts/reinforcement_learning/fb_mod/configs/*.yaml` |
| Change FB network defaults | `scripts/reinforcement_learning/fb_mod/configs/agent/FBAgent.yaml` |
| Change online training loop | `scripts/reinforcement_learning/fb_mod/pretrain.py` |
| Change offline-data collection | `scripts/reinforcement_learning/fb_mod/play_collect.py` |
| Change offline pretraining | `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` |
| Change checkpoint loading/playback | `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py`, `scripts/reinforcement_learning/fb_mod/play.py`, `scripts/reinforcement_learning/fb_mod/play_xbox.py` |
| Change FB transition storage | `scripts/reinforcement_learning/fb_mod/buffer.py` |
| Change command/reward inference | `scripts/reinforcement_learning/toolbox/config_task.py`, `scripts/reinforcement_learning/toolbox/functions_reward.py` |
| Change cluster launch defaults | `docker/cluster/.env.cluster`, `docker/cluster/*.sh`, `bash/euler/*.sh` |

## Invariants To Preserve

The training loop, agent updates, reward inference, and playback scripts rely on these contracts:

- `pretrain.py` must launch Isaac Lab before importing modules that require the simulator runtime.
- `hydra_cfg.agent.model.policy_dim`, `obs_dim`, `goal_dim`, `critic_dim`, and `action_dim` are filled from the environment config before constructing the agent.
- `hydra_cfg.train.replay_buffer_capacity` is derived from `env.num_envs * train.replay_buffer_N`.
- `FB_VecEnvWrapper.reset()` and `step()` return transition dictionaries with `obs`, `time`, `done`, `reward_task`, and `reward_reg`.
- Replay-buffer transitions have `observation`, `action`, and nested `next` keys.
- Raw Go2 observations include the names required by `RewardFunction`: `vx`, `vy`, `vz`, `wz`, `gx`, `gy`, `gz`, and `base_height`.
- `FBPolicyLoader` expects `hydra_config.yaml` two directories above the model checkpoint file.
- Saved FB checkpoints contain `actor`, `policy_normalizer`, `B`, and `B_normalizer`.
- `play.py`, `play_xbox.py`, and `play_collect.py` assume fixed checkpoint step names unless edited.
- `FB_VecEnvWrapper.eval_task()` expects a command tensor shaped like `[num_envs, 3]` for `vx`, `vy`, and `wz`.

## Known Technical Debt

These issues are verified from source inspection, not fixed here:

- `pretrain_offline.py` has a hard-coded absolute `offline_data_path`.
- `Isaaclab_fb_play_config_base.yaml` ships with a placeholder `path`.
- `Isaaclab_pretrain_config_base.yaml` uses `Isaac-Flat-Unitree-Go2-Rnd-full-FB-v0`, which does not match the registered Go2 IDs.
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` registers `Isaac-Flat-Unitree-Go2-FB-v0` to module paths that are not present.
- `isaaclab.sh --test` references missing `tools/run_all_tests.py`.
- `docker/docker-compose.yaml` bind-mounts missing `../tools`.
- `play_xbox.py` and `play.py` disagree on the replay-buffer checkpoint step they load.
- Needs verification: `Go2NormEnv.__init__` compares policy observation shape to `cfg.observation_space`, while `Go2_Base_Cfg` separately defines `policy_space`.

## Release Or PR Checklist

Before opening a PR or claiming a change is complete:

1. State which workflow changed: FB train, FB play, Go2 env, RSL-RL, Docker, cluster, docs, or tests.
2. Run the narrowest relevant validation command that exercises that workflow.
3. Include any failed or skipped validation explicitly.
4. Check `git status --short` for generated outputs under `exp_*`, `logs/`, `wandb/`, `videos/`, and Docker artifacts.
5. If public behavior, config fields, task IDs, generated artifact names, or commands changed, update `README.md` or `docs/`.
