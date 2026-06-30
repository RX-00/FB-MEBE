# FB-MEBE Usage

This guide gives copy-pastable commands for the workflows that are present in the repository. Commands assume the repository root is the current directory.

## Environment Setup

The project conda environment is `fb-mebe`. A checked-in environment snapshot exists at `environment.yml`.

```bash
conda env create -f environment.yml
conda activate fb-mebe
```

If the environment already exists, update it from the snapshot:

```bash
conda env update -f environment.yml --prune
conda activate fb-mebe
```

The manual install sequence from the README is still useful when rebuilding the environment from a minimal Python env:

```bash
conda create -n fb-mebe python=3.10 -y
conda activate fb-mebe
pip install --upgrade pip
pip install "isaacsim[all,extscache]==4.5.0" --extra-index-url https://pypi.nvidia.com
pip install -U torch==2.7.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128
./isaaclab.sh --install
pip install -U torch==2.7.0+cu128 torchvision==0.22.0+cu128 torchaudio==2.7.0+cu128 --index-url https://download.pytorch.org/whl/cu128
pip install hydra-core
```

Do not install the unrelated PyPI package named `hydra`; the scripts import Facebook Hydra through `hydra-core`.

`environment.yml` is an exported environment snapshot, not a solver lockfile. Exact reproduction can still depend on conda channels, pip indexes, CUDA drivers, and platform.

## Isaac Lab Utility Commands

`./isaaclab.sh` is inherited from upstream Isaac Lab. It is useful for selected setup and simulator operations, but it also reports upstream options that reference files removed from this FB-MEBE checkout.

| Command | Purpose |
| --- | --- |
| `./isaaclab.sh --install` | Install packages under `source/` and extra RL framework dependencies. |
| `./isaaclab.sh --format` | Run pre-commit hooks over the repository. |
| `./isaaclab.sh --python <args>` | Run Python from the active conda env or Isaac Sim Python. |
| `./isaaclab.sh --sim <args>` | Launch Isaac Sim. |
| `./isaaclab.sh --conda fb-mebe` | Create a conda env and install Isaac Lab activation hooks. |

Ignore `./isaaclab.sh --test`, `./isaaclab.sh --docs`, and `./isaaclab.sh --docker` unless their upstream helper paths are restored. This checkout does not include top-level `tools/`, Sphinx docs build files, or `docker/`.

## List Registered Environments

This launches Isaac Sim headless before printing the Gymnasium registry table:

```bash
python scripts/environments/list_envs.py
```

Useful Go2 task IDs observed in `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py`:

```text
Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0
Isaac-Flat-Unitree-Go2-Rnd-Full-FB-INC-v0
Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-KAIST-v0
```

## Train FB On Go2

Default shell entry point:

```bash
./bash/fb_pretrain.sh
```

`bash/fb_pretrain.sh` does not forward additional arguments. Use the Python entry point when passing Hydra overrides:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py --config-name=Isaaclab_pretrain_config_go2
```

Small smoke-style configuration for local debugging:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    env.num_envs=64 \
    env.video_train=False \
    env.video_eval=False \
    train.num_train_steps=1000 \
    train.interval_eval=1000 \
    train.interval_save_model=1000 \
    wandb.use_wandb=False
```

Hydra overrides are passed as bare `key=value` arguments after the optional `--config-name=...`.

The Go2 config in `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml` defaults to:

| Setting | Default |
| --- | --- |
| `env.device` | `cuda:0` |
| `env.task` | `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0` |
| `env.num_envs` | `2048` |
| `env.video_train` | `true` |
| `env.video_eval` | `false` |
| `wandb.use_wandb` | `true` in the checked-in Go2 YAML |
| `train.agent` | `meta` |
| `train.num_train_steps` | `150_000` |
| `train.interval_save_model` | `50000` |
| `train.interval_eval` | `20000` |

The observed local run from `./bash/fb_pretrain.sh` resolved `wandb.use_wandb: false` in its saved `hydra_config.yaml`. For a no-W&B local run through `pretrain.py`, pass `wandb.use_wandb=False` explicitly unless the checked-in config has already been changed.

Training writes under:

```text
exp_<train.machine>/fb_mod/<env.task>/<wandb.group>/<timestamp>/
```

Expected files include:

```text
hydra_config.yaml
models/model_step_<t>.pt
models/replay_buffer_step_<t>.pt
videos_pretrain/
videos_eval/
```

Video directories only appear when the matching video flag is enabled.

Observed local training output from the June 26, 2026 run:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46/
```

That run contains:

```text
hydra_config.yaml
models/model_step_50000.pt
models/model_step_100000.pt
models/model_step_150000.pt
models/replay_buffer_step_50000.pt
models/replay_buffer_step_100000.pt
models/replay_buffer_step_150000.pt
videos_pretrain/pretrain-step-150000.mp4
```

Use the 150k policy and matching replay buffer explicitly:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir "exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46" \
    --model-step 150000 \
    --replay-buffer-step 150000
```

## Run Multiple FB Seeds

Local multi-seed script:

```bash
./bash/fb_pretrain_multi.sh
```

The script runs seeds `0`, `42`, `17`, `5`, and `24`, disables train/eval video, uses `cuda:0`, sets `env.num_envs=2048`, and sets `train.num_train_steps=300000`.

## Enable W&B

The current checked-in Go2 config enables W&B by default. To use it for one run, log in and set a workspace you can access:

```bash
wandb login
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    wandb.use_wandb=True \
    wandb.entity=<your-entity> \
    wandb.project=<your-project> \
    wandb.group=<group-name>
```

To force a local no-W&B run:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    wandb.use_wandb=False
```

README notes a workaround if W&B `0.12.x` crashes online in this FB script:

```bash
pip uninstall rl-games
pip install "wandb==0.17.9" "protobuf<5,>=3.20.3"
```

## Play Or Evaluate A Saved FB Run

`scripts/reinforcement_learning/fb_mod/configs/Isaaclab_fb_play_config_base.yaml` defaults to automatic selection:

```yaml
path: latest
model_step: latest
replay_buffer_step: latest
```

With those defaults, `play_config.py` searches `exp_*/` for run directories containing `hydra_config.yaml` and `models/model_step_*.pt`, then chooses the run whose latest model artifact has the newest modification time.

Explicit run selection is safer when multiple runs exist:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir exp_local/fb_mod/<task>/<group>/<timestamp>
```

Select specific artifact steps when needed:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir exp_local/fb_mod/<task>/<group>/<timestamp> \
    --model-step 150000 \
    --replay-buffer-step 150000
```

`--path` is accepted as an alias for `--run-dir`. The path may point at a run directory, that run's `hydra_config.yaml`, its `models/` directory, or a `models/model_step_<t>.pt` file.

`play.py` needs both a model checkpoint and replay-buffer checkpoint. The model supplies the actor and backward map through `FBPolicyLoader`; the replay buffer supplies sampled observations and goals for reward inference.

`play.py` creates a new eval output directory under:

```text
exp_local/fb_mod/<task>/<timestamp>_play/
```

## Record A Video From A Saved Policy

The play config at `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_fb_play_config_base.yaml` sets `env.video_eval: true`, `env.headless: true`, and `env.num_envs: 512`. With those defaults, `play.py` records a headless evaluation video through `RecordVideo_EVAL_GC`.

Record the observed 150k local policy:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir "exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46" \
    --model-step 150000 \
    --replay-buffer-step 150000
```

Expected eval video output path, based on `play.py` and `wrapper/wrapper_video.py`:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/<timestamp>_play/videos_eval/locomotion_list_250.mp4
```

Disable playback video for metrics-only evaluation:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir "exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46" \
    --model-step 150000 \
    --replay-buffer-step 150000 \
    env.video_eval=False
```

## Play With An Xbox Controller

`play_xbox.py` uses the same run and artifact resolver as `play.py`.

```bash
./bash/fb_play_xbox.sh --run-dir exp_local/fb_mod/<task>/<group>/<timestamp>
```

or:

```bash
python scripts/reinforcement_learning/fb_mod/play_xbox.py \
    --run-dir exp_local/fb_mod/<task>/<group>/<timestamp> \
    --model-step latest \
    --replay-buffer-step latest
```

The script prompts for CPU or GPU simulation. CPU mode is documented in the prompt as allowing shift + left-click robot manipulation; GPU mode is documented as not allowing drag manipulation.

Controller mapping printed by the script:

| Input | Effect |
| --- | --- |
| Left stick | Linear velocity command. |
| Right stick X | Yaw command. |
| Right stick Y | Pitch/orientation command and `vz` command. |
| Bumpers | Roll/orientation command. |
| Triggers | Base-height adjustment. |
| D-pad | Read by the controller loader, but not used by `play_xbox.py` command mapping. |
| X button | Reset environment. |

## Collect Offline Data

`play_collect.py` uses the same run/model resolver with no replay-buffer load. It loads a trained policy, rolls out until the replay buffer reaches `train.replay_buffer_capacity`, and saves:

```text
<play_cfg.path>/offline_data.pt
```

Command:

```bash
./bash/fb_collect.sh --run-dir exp_local/fb_mod/<task>/<group>/<timestamp> --model-step latest
```

or:

```bash
python scripts/reinforcement_learning/fb_mod/play_collect.py \
    --run-dir exp_local/fb_mod/<task>/<group>/<timestamp> \
    --model-step latest
```

## Offline Pretraining

The checked-in offline pretraining path is currently stale. Keep these commands
for source inspection, not as validated runnable workflows:

```bash
./bash/fb_pretrain_offline.sh
```

Direct entry point:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain_offline.py --config-name=Isaaclab_pretrain_config_go2
```

Do not run this as-is. Verified blockers in `scripts/reinforcement_learning/fb_mod/pretrain_offline.py`:

- It still reads old `hydra_cfg.env.video`, `env.video_interval`, and `env.video_length` keys; the current configs use split `video_train` and `video_eval` keys.
- It hard-codes `offline_data_path` to an absolute `/home/jiajun_hu/.../offline_data.pt` path.
- It calls `ConvexHull` during density logging without importing it.

## Train Or Play With Standard RSL-RL

The standard RSL-RL scripts are separate from the FB-MEBE training path.

Train:

```bash
python scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Cartpole-Direct-v0 \
    --num_envs 64 \
    --headless \
    --max_iterations 10
```

Play:

```bash
python scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Cartpole-Direct-v0 \
    --num_envs 1 \
    --headless
```

RSL-RL logs go under:

```text
logs/rsl_rl/<experiment_name>/<timestamp>/
```

The train script writes `params/env.yaml`, `params/agent.yaml`, `params/env.pkl`, and `params/agent.pkl` in each run directory.

## Removed Upstream Docker And Cluster Scaffolding

The `docker/` directory is not part of the current core FB-MEBE checkout. It was inherited from upstream Isaac Lab and has been removed.

Do not use these inherited paths unless they are restored or rewritten:

```text
./isaaclab.sh --docker
python docker/container.py start
./docker/cluster/cluster_interface.sh job ...
```

Some notes and shell scripts remain under `bash/euler/` and `bash/tars_case/`, but they still reference the removed Docker tooling. Treat those files as stale until they are updated for a non-Docker cluster workflow.

## Troubleshooting

| Symptom | Likely cause | Concrete check or fix |
| --- | --- | --- |
| `Unable to find the Isaac Sim directory` from `isaaclab.sh` | Conda env is not active or Isaac Sim pip packages are missing. | Run `conda activate fb-mebe`, then verify the README Isaac Sim install command was run. |
| Import error for `hydra` | `hydra-core` is missing, or the unrelated `hydra` package was installed. | Run `pip install hydra-core`; remove the unrelated package if installed. |
| Unknown Go2 task ID | Config uses a stale or misspelled task name. | Use `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0`, `INC-v0`, or `ABS-KAIST-v0`. |
| `play.py` cannot find checkpoint files | No run was found under `exp_*`, or the requested step does not exist. | Pass `--run-dir <run>` explicitly; use `--model-step latest` and `--replay-buffer-step latest`, or choose one of the steps printed in the error. |
| `play_xbox.py` cannot find replay buffer | Same resolver failure as `play.py`; it no longer has a separate hard-coded replay-buffer step. | Pass `--run-dir`, `--model-step`, and `--replay-buffer-step` explicitly. |
| Offline pretraining fails before or during startup | `pretrain_offline.py` is stale: old `env.video*` keys, hard-coded `offline_data_path`, and missing `ConvexHull` import. | Update the script before relying on offline pretraining. |
| `./isaaclab.sh --test`, `--docs`, or `--docker` fails immediately | Those are upstream Isaac Lab paths and this checkout does not include the referenced helper directories. | Use direct FB-MEBE commands from this guide unless the upstream helpers are restored. |
| `bash/euler/*.sh` or `bash/tars_case/*` cannot find Docker files | Those inherited scripts still reference the removed `docker/` directory. | Treat them as stale until a current non-Docker cluster workflow is added. |
