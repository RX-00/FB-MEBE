<div align="center">

# FB-MEBE: Maximum Entropy Behavior Exploration

[Website](https://math-286-pro.github.io/FB-MEBE-Web/)&emsp;&emsp;[Paper](https://arxiv.org/abs/2603.25464)

Code for the paper [`"Maximum Entropy Behavior Exploration for Sim2Real Zero-Shot Reinforcement Learning"`](https://arxiv.org/abs/2603.25464).
<img src="pictures/FB-Teaser.png" alt="FB-MEBE teaser" width="900" />

</div>

This fork and branch is a minimal cleaning of the original repo and an additional (WIP) tutorial.

## Documentation

Detailed repository documentation is available in:

- [`docs/architecture.md`](docs/architecture.md): code layout, FB training flow, Go2 task contracts, generated artifacts, and known inconsistencies.
- [`docs/usage.md`](docs/usage.md): setup, training, playback, recording videos from saved policies, offline data, and troubleshooting.
- [`docs/development.md`](docs/development.md): validation, safe edit locations, invariants, and maintenance notes.

## Project Layout

This repository is a stripped-down FB-MEBE fork built on top of Isaac Lab. The FB-specific training path is mostly under `scripts/reinforcement_learning/fb_mod/`; the Go2 task implementations it trains against are under `source/isaaclab_tasks/isaaclab_tasks/direct/go2/`.

Core FB implementation subtree:

```text
scripts/
└── reinforcement_learning/
    └── fb_mod/
        ├── agent_meta/
        │   └── fb/
        │       └── agent.py (code related to FB agent)
        ├── configs/ (folder related to FB agent and training settings)
        ├── density_estimator/ (folder related to normalizing flow)
        └── pretrain.py (code of FB training)
```

| Path | Use |
| --- | --- |
| `README.md` | High-level setup, configuration, layout, and primary commands. |
| `docs/` | More detailed Markdown docs: architecture, usage workflows, and development notes. |
| `environment.yml` | Snapshot of the `fb-mebe` conda environment from this workspace. It is an environment export, not a strict lockfile. |
| `isaaclab.sh` | Isaac Lab utility wrapper for install, formatting, Python execution, and simulator launch. Some inherited options still reference removed upstream helper paths. |
| `apps/` | Isaac Lab Kit app files used by Isaac Sim / Isaac Lab launch paths. |
| `pictures/` | README images. |
| `bash/` | Thin shell entry points for common workflows. Current core scripts are `fb_pretrain.sh`, `fb_pretrain_multi.sh`, `fb_play_xbox.sh`, `fb_collect.sh`, and `fb_pretrain_offline.sh`. `bash/euler/` and `bash/tars_case/` are inherited cluster notes/scripts and are stale unless the removed Docker tooling is restored or replaced. |
| `scripts/environments/` | Environment utility scripts, including `list_envs.py`. |
| `scripts/reinforcement_learning/fb_mod/` | Main FB-MEBE implementation for Isaac Lab Go2 experiments. This is the main directory to inspect for FB training, playback, loading, wrappers, and configs. |
| `scripts/reinforcement_learning/toolbox/` | Shared FB helper code for task command sampling, reward inference, metrics, entropy, and visualization. |
| `scripts/reinforcement_learning/rsl_rl/` | Standard RSL-RL train/play scripts inherited from Isaac Lab. Separate from the FB-MEBE training path. |
| `scripts/reinforcement_learning/fb/url_benchmark/` | URLB-style benchmark code adapted from another codebase. Separate from the Go2 Isaac Lab FB workflow. |
| `scripts/tools/` and `scripts/tutorials/` | Inherited Isaac Lab utilities and tutorials. Useful reference material, but not the core FB-MEBE algorithm path. |
| `source/isaaclab/` | Core Isaac Lab Python package. |
| `source/isaaclab_assets/` | Isaac Lab asset package, including robot assets/configs used by tasks. |
| `source/isaaclab_tasks/` | Isaac Lab task package. Custom Go2 FB tasks are registered under `source/isaaclab_tasks/isaaclab_tasks/direct/go2/`. |
| `source/isaaclab_rl/` | Isaac Lab RL integration package used by standard RL scripts. |
| `source/isaaclab_mimic/` | Inherited Isaac Lab mimic/data generation package. Not the main FB-MEBE path. |
| `exp_local/` | Generated local training, playback, and collection outputs. This is where local FB runs and checkpoints are saved. It is ignored by Git. |
| `wandb/` | Local W&B run files when W&B is used or offline logs are created. Generated output, not source code. |

### FB-MEBE Code Path

The files most often touched for the Go2 FB workflow are:

| Path | Use |
| --- | --- |
| `scripts/reinforcement_learning/fb_mod/pretrain.py` | Online FB training entry point. Creates the environment, agent, replay buffer, metrics, videos, checkpoints, and run directory. |
| `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` | Offline pretraining entry point. Currently contains a hard-coded absolute offline-data path and should be made configurable before use. |
| `scripts/reinforcement_learning/fb_mod/play.py` | Evaluates a saved FB policy and can record an eval video. |
| `scripts/reinforcement_learning/fb_mod/play_xbox.py` | Runs a saved FB policy interactively with an Xbox controller. |
| `scripts/reinforcement_learning/fb_mod/play_collect.py` | Loads a saved policy, rolls out data, and saves `offline_data.pt`. |
| `scripts/reinforcement_learning/fb_mod/play_config.py` | Resolves run directories and artifact steps for `play.py`, `play_xbox.py`, and `play_collect.py`. |
| `scripts/reinforcement_learning/fb_mod/buffer.py` | `DictBuffer` replay buffer used by training, play, and collection code. |
| `scripts/reinforcement_learning/fb_mod/agent_meta/fb/` | Main meta FB agent implementation used by `Isaaclab_pretrain_config_go2.yaml` through `train.agent: meta`. |
| `scripts/reinforcement_learning/fb_mod/agent_crl/` | Alternate CRL-style FB agent path used when `train.agent: crl`. |
| `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py` | Loads saved FB checkpoints for play/eval/collection. |
| `scripts/reinforcement_learning/fb_mod/wrapper/` | Environment and video wrappers used by FB workflows. |
| `scripts/reinforcement_learning/fb_mod/configs/` | Hydra configs for training and playback. |
| `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/` | Absolute joint-position Go2 task used by the default FB config. |
| `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_inc/` | Incremental/delta action Go2 task variant. |
| `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_KAIST_abs/` | KAIST-style absolute-control task variant with additional phase/barrier logic. |

### Run Output Layout

`pretrain.py` saves FB training runs under this pattern:

```text
exp_<train.machine>/fb_mod/<env.task>/<wandb.group>/<timestamp>/
```

With the default Go2 config, `train.machine: local`, so local runs are written under `exp_local/`. Example from this workspace:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46/
```

Each training run directory contains the resolved config and any artifacts saved by the training loop:

```text
<run>/
├── hydra_config.yaml
├── models/
│   ├── model_step_<step>.pt
│   └── replay_buffer_step_<step>.pt
├── videos_pretrain/
└── videos_eval/
```

Important details:

- `hydra_config.yaml` is the resolved training config. Playback loaders use it to rebuild network shapes and config values.
- `models/model_step_<step>.pt` is the saved FB policy checkpoint. The checkpoint contains the actor, policy normalizer, backward map `B`, and backward-map normalizer.
- `models/replay_buffer_step_<step>.pt` is a saved sample of replay-buffer observations used by playback/eval code for reward inference.
- `videos_pretrain/` is created only when `env.video_train=True`.
- `videos_eval/` is created only when evaluation video recording is enabled.
- `exp_local/` is ignored by Git. If `train.machine` is changed to another value, for example `cluster`, outputs go under `exp_cluster/`; check those generated directories before committing.

Playback creates separate output directories. `play.py` writes evaluation output under:

```text
exp_local/fb_mod/<env.task>/<timestamp>_play/
```

For example, a recorded eval video is saved under:

```text
exp_local/fb_mod/<env.task>/<timestamp>_play/videos_eval/locomotion_list_250.mp4
```

`play_collect.py` saves offline data into the selected run directory:

```text
<run>/offline_data.pt
```

## Configuration
```yaml
# We use hydra to configure all the parameters

# this file stores all the FB agent hyperparameter settings
scripts/reinforcement_learning/fb_mod/configs/agent/FBAgent.yaml

# this file will inherit the "FBAgent.yaml" and override its hyperparameter
scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_base.yaml

# In Go2 Tasks we use Isaaclab_pretrain_config_go2.yaml
# It inherits the Isaaclab_pretrain_config_base.yaml and override its task type
scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml


# Details of Isaaclab_pretrain_config_go2.yaml. 
# These are the most frequently change parameters

env: 
 device:      simulate on which device
 video_train: record pretrain or not
 video_eval:  record evaluation or not 
              (if you enable this you also have to enable video_train,
               otherwise will report error)
 num_envs:    number of parallel environment you will run
 task:        select relevent tasks

 # there are three types of task now (we commented two out)

# 1. "Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0" 
# has random friction and robot base, link mass, and use absolute joint control

# 2. "Isaac-Flat-Unitree-Go2-Rnd-Full-FB-INC-v0" 
# same as above but use incremental/delta control (can be viewed as joint velocity control). This is to expend the action space.

# 3. "Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-KAIST-v0" 
# absolute joint control, and added (sin(t), cos(t)) two more observation and use soft-barrier-function from KAIST (remember to set agent.model.archi.critic=True to use this task)

wandb:
  use_wandb: upload data to wandb
  entity:    your wandb account entity
  project:   desired target project
  name:      desired target name
  group:     desired target group

agent:
 compile: by setting to True will make training faster
 train: 
   lr_f: learning rate for forward network
   lr_b: learning rate for backward network
   lr_actor: learning rate for actor network
 model:
   archi: architecture for different networks
     critic:
       enable: if you want to enable critic or not
```

## Training
```bash
# 0. clone this repo
git clone https://github.com/MATH-286-Pro/FB-MEBE.git

# 1. create virtual env (conda example)
conda create -n fb-mebe python=3.10 -y
conda activate fb-mebe

# 2. install isaacsim
# (you can follow: https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/pip_installation.html)
pip install --upgrade pip
pip install "isaacsim[all,extscache]==4.5.0" --extra-index-url https://pypi.nvidia.com
# NOTE: This command is for x86_64 system
pip install -U torch==2.7.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128


# 3. install isaaclab
./isaaclab.sh --install
# Reinstall torch after Isaac Lab install (needed for RTX 50xx / sm_120):
pip install -U torch==2.7.0+cu128 torchvision==0.22.0+cu128 torchaudio==2.7.0+cu128 --index-url https://download.pytorch.org/whl/cu128
# If Hydra is missing, install the Facebook Hydra package:
pip install hydra-core
# Do not install the unrelated package named "hydra".

# 4. Monitor training using wandb
# The Go2 config controls W&B through wandb.use_wandb.
# If it is enabled, first run this command to log in:
wandb login
# then go to "scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml"
# in wandb section set "entity" and "project" to a workspace you can access.
# For a no-W&B local run, use the Python entry point with wandb.use_wandb=False.
# If wandb 0.12.x crashes online, this FB script does not use rl-games; use:
pip uninstall rl-games
pip install "wandb==0.17.9" "protobuf<5,>=3.20.3"

# 5. Run bash to train FB (you might encounter some python dependency issues)
./bash/fb_pretrain.sh

```
```bash
# Other commands and notes
./bash/fb_pretrain_multi.sh # For series of training
./bash/fb_play_xbox.sh      # run model in isaaclab controlled by joystick
# bash/euler/ notes are stale unless the removed Docker tooling is restored or replaced.

```

## Play

Use `play.py` to evaluate a saved FB policy and record an eval video. It needs both a model checkpoint and the matching replay-buffer checkpoint.

To play the policy trained by `./bash/fb_pretrain.sh` in this workspace:

```bash
conda activate fb-mebe
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir "exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46" \
    --model-step 150000 \
    --replay-buffer-step 150000
```

For another run, pass its run directory and choose `latest` or a specific saved step:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir exp_local/fb_mod/<task>/<group>/<timestamp> \
    --model-step latest \
    --replay-buffer-step latest
```

`play.py` does not save videos back into the training run directory. Each playback call creates a new directory under `exp_local/fb_mod/<task>/` using the time playback started:

```text
exp_local/fb_mod/<task>/<play-timestamp>_play/
```

With the default play config, eval videos are saved in that run's `videos_eval/` directory. The file name is generated from the evaluated task and mode as `<task>_<mode>_250.mp4`; for the default locomotion eval, the path is:

```text
exp_local/fb_mod/<task>/<play-timestamp>_play/videos_eval/locomotion_list_250.mp4
```

## Q&A

> Q1: The trained FB model exhibits YAW drift during forward locomotion. Can this issue be mitigated by incorporating mirrored data during pretraining like [D3](https://leggedrobotics.github.io/d3-skill-discovery/)?
> 
> A1: In our experiments, training with mirrored data did not successfully eliminate the drift.
