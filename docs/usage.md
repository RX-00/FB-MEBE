# FB-MEBE Usage

This guide gives copy-pastable commands for the workflows that are present in the repository. Commands assume the repository root is the current directory.

## Environment Setup

The project conda environment is `fb-mebe`.

```bash
conda activate fb-mebe
```

If the environment does not exist, the repository contains two setup paths:

```bash
conda create -n fb-mebe python=3.10 -y
conda activate fb-mebe
```

or:

```bash
./isaaclab.sh --conda fb-mebe
conda activate fb-mebe
```

The README documents the Isaac Sim and Torch install sequence used by this fork:

```bash
pip install --upgrade pip
pip install "isaacsim[all,extscache]==4.5.0" --extra-index-url https://pypi.nvidia.com
pip install -U torch==2.7.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128
./isaaclab.sh --install
pip install -U torch==2.7.0+cu128 torchvision==0.22.0+cu128 torchaudio==2.7.0+cu128 --index-url https://download.pytorch.org/whl/cu128
pip install hydra-core
```

Do not install the unrelated PyPI package named `hydra`; the scripts import Facebook Hydra through `hydra-core`.

Needs verification: there is no checked-in `environment.yml`, `requirements.txt`, or lockfile for the `fb-mebe` conda environment. Package versions beyond the setup files and README are not fully pinned in the repo.

## Isaac Lab Utility Commands

`./isaaclab.sh --help` reports these supported actions:

| Command | Purpose |
| --- | --- |
| `./isaaclab.sh --install` | Install packages under `source/` and extra RL framework dependencies. |
| `./isaaclab.sh --format` | Run pre-commit hooks over the repository. |
| `./isaaclab.sh --python <args>` | Run Python from the active conda env or Isaac Sim Python. |
| `./isaaclab.sh --sim <args>` | Launch Isaac Sim. |
| `./isaaclab.sh --docker <args>` | Delegate to `docker/container.sh`, which delegates to `docker/container.py`. |
| `./isaaclab.sh --conda fb-mebe` | Create a conda env and install Isaac Lab activation hooks. |

Needs verification: `./isaaclab.sh --test` references `tools/run_all_tests.py`, which is not present in this checkout.

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

Equivalent Python command:

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
| `wandb.use_wandb` | `false` |
| `train.agent` | `meta` |
| `train.num_train_steps` | `150_000` |
| `train.interval_save_model` | `50000` |
| `train.interval_eval` | `20000` |

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

## Run Multiple FB Seeds

Local multi-seed script:

```bash
./bash/fb_pretrain_multi.sh
```

The script runs seeds `0`, `42`, `17`, `5`, and `24`, disables train/eval video, uses `cuda:0`, sets `env.num_envs=2048`, and sets `train.num_train_steps=300000`.

## Enable W&B

The Go2 config disables W&B by default. To enable it for one run:

```bash
wandb login
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    wandb.use_wandb=True \
    wandb.entity=<your-entity> \
    wandb.project=<your-project> \
    wandb.group=<group-name>
```

README notes a workaround if W&B `0.12.x` crashes online in this FB script:

```bash
pip uninstall rl-games
pip install "wandb==0.17.9" "protobuf<5,>=3.20.3"
```

## Play Or Evaluate A Saved FB Run

Edit `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_fb_play_config_base.yaml` first:

```yaml
path: exp_local/fb_mod/<task>/<group>/<timestamp>
```

The directory must contain:

```text
hydra_config.yaml
models/model_step_150000.pt
models/replay_buffer_step_150000.pt
```

Then run:

```bash
python scripts/reinforcement_learning/fb_mod/play.py
```

`play.py` creates a new eval output directory under:

```text
exp_local/fb_mod/<task>/<timestamp>_play/
```

Needs verification: `play.py` currently hard-codes `model_step_150000.pt` and `replay_buffer_step_150000.pt`. Change the script or create matching checkpoint names if your run saved a different step.

## Play With An Xbox Controller

Edit `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_fb_play_config_base.yaml` as above, then run:

```bash
./bash/fb_play_xbox.sh
```

or:

```bash
python scripts/reinforcement_learning/fb_mod/play_xbox.py
```

The script prompts for CPU or GPU simulation. CPU mode is documented in the prompt as allowing shift + left-click robot manipulation; GPU mode is documented as not allowing drag manipulation.

Controller mapping printed by the script:

| Input | Effect |
| --- | --- |
| Left stick | Linear velocity command. |
| Right stick | Yaw and height/orientation command. |
| D-pad up/down | Height adjustment. |
| Triggers | Fine control. |
| X button | Reset environment. |

Needs verification: `play_xbox.py` loads `models/model_step_150000.pt` and `models/replay_buffer_step_300000.pt`, so the required replay-buffer checkpoint differs from `play.py`.

## Collect Offline Data

`play_collect.py` loads a trained policy from `play_cfg.path`, rolls out until the replay buffer reaches `train.replay_buffer_capacity`, and saves:

```text
<play_cfg.path>/offline_data.pt
```

Command:

```bash
./bash/fb_collect.sh
```

or:

```bash
python scripts/reinforcement_learning/fb_mod/play_collect.py
```

Needs verification: `play_collect.py` also expects `models/model_step_150000.pt`.

## Offline Pretraining

Entry point:

```bash
./bash/fb_pretrain_offline.sh
```

Equivalent:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain_offline.py --config-name=Isaaclab_pretrain_config_go2
```

Do not run this until `offline_data_path` inside `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` is made local or configurable. The checked-in script currently points to an absolute `/home/jiajun_hu/.../offline_data.pt` path.

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

## Docker

Build and start the base container:

```bash
python docker/container.py start
```

Enter the running container:

```bash
python docker/container.py enter
```

Stop it:

```bash
python docker/container.py stop
```

Render the composed Docker config:

```bash
python docker/container.py config
```

The shell wrapper exists but is deprecated:

```bash
docker/container.sh start
```

`docker/.env.base` sets the Isaac Sim image to `nvcr.io/nvidia/isaac-sim:4.5.0`.

Needs verification: `docker/docker-compose.yaml` bind-mounts `../tools`, but no top-level `tools/` directory exists in this checkout.

## Euler / Slurm Cluster Flow

Cluster settings live in `docker/cluster/.env.cluster`. Replace placeholders before pushing or submitting:

```text
USERNAME=Your_ETH_User_Name
CLUSTER_LOGIN=$USERNAME@euler.ethz.ch
WANDB_API_KEY=your_wandb_api_key
CLUSTER_PYTHON_EXECUTABLE=scripts/reinforcement_learning/fb_mod/pretrain.py
```

Build and push image from the local machine:

```bash
./bash/euler/build_image.sh
```

Submit one FB job:

```bash
./bash/euler/run.sh
```

Submit multi-seed jobs:

```bash
./bash/euler/run_multi.sh
```

`bash/euler/run.sh` submits Hydra overrides through:

```bash
./docker/cluster/cluster_interface.sh job \
    --config-name=Isaaclab_pretrain_config_go2 \
    env.video_train=False \
    env.video_eval=False \
    train.machine=cluster
```

`docker/cluster/submit_job_slurm.sh` requests one `rtx_4090` GPU, 4 CPUs, 8 hours, and `8192` MB per CPU. Change that file for different Slurm resources.

## Troubleshooting

| Symptom | Likely cause | Concrete check or fix |
| --- | --- | --- |
| `Unable to find the Isaac Sim directory` from `isaaclab.sh` | Conda env is not active or Isaac Sim pip packages are missing. | Run `conda activate fb-mebe`, then verify the README Isaac Sim install command was run. |
| Import error for `hydra` | `hydra-core` is missing, or the unrelated `hydra` package was installed. | Run `pip install hydra-core`; remove the unrelated package if installed. |
| Unknown Go2 task ID | Config uses a stale or misspelled task name. | Use `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0`, `INC-v0`, or `ABS-KAIST-v0`. |
| `play.py` cannot find checkpoint files | `Isaaclab_fb_play_config_base.yaml:path` is still a placeholder or checkpoint step names differ. | Point `path` at a run directory and check `models/model_step_150000.pt` plus `models/replay_buffer_step_150000.pt`. |
| `play_xbox.py` cannot find replay buffer | It expects `replay_buffer_step_300000.pt`. | Rename/copy the desired replay-buffer checkpoint or edit the script. |
| Offline pretraining loads missing data | `pretrain_offline.py` contains a hard-coded absolute path. | Replace that path before running. |
| `./isaaclab.sh --test` fails immediately | `tools/run_all_tests.py` is absent. | Run individual unittest files directly until the helper is restored. |
| Docs CI fails | `.github/workflows/docs.yaml` expects a Sphinx docs tree with `docs/requirements.txt` and Make targets. | Either restore the Sphinx tree or update the workflow for Markdown docs. |
