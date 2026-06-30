# Big Picture

## Problem

FB-MEBE trains a zero-shot reinforcement-learning policy for the Unitree Go2.
After pretraining, the policy should adapt to a new downstream reward, such as a
velocity or orientation command, without training again.

The paper states the motivation in `paper/arXiv-2603.25464v1/main.tex`: online
Forward-Backward (FB) training can collapse toward low-diversity behavior when
exploration is undirected. FB-MEBE addresses that by sampling exploration
behaviors from low-density areas of the achieved behavior distribution.

The repository implements the Go2 path mostly in:

- `scripts/reinforcement_learning/fb_mod/pretrain.py`
- `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py`
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py`
- `scripts/reinforcement_learning/fb_mod/play.py`

## Inputs And Outputs

Training inputs:

- A registered Isaac Lab Go2 task ID, usually
  `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0`.
- A Hydra config, usually
  `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml`.
- The Go2 environment observation dictionary returned by
  `Go2NormEnv._get_observations`.

Training outputs:

- `hydra_config.yaml`: resolved training config.
- `models/model_step_<step>.pt`: actor, backward map, and normalizers.
- `models/replay_buffer_step_<step>.pt`: sampled observations used for reward
  inference during play.
- Optional videos under `videos_pretrain/` and `videos_eval/`.

Playback inputs:

- A model checkpoint.
- A replay-buffer checkpoint.
- A command distribution, such as locomotion list commands from
  `scripts/reinforcement_learning/toolbox/config_task.py`.

Playback output:

- A zero-shot policy rollout for the inferred reward embedding `z_r`.
- Optional video under an `exp_local/.../<timestamp>_play/videos_eval/` directory.

## Core Idea

FB learns a low-rank factorization of successor measures:

```text
M^{pi_z}(s' | s, a) ~= F(s, a, z)^T B(s')
```

The actor is conditioned on `z`, and it is trained to choose actions with high
`F(s, a, z)^T z`. At test time, a task reward `r(s)` is projected through the
learned backward map:

```text
z_r ~= E[B(s) r(s)]
```

Then the same actor runs with `z_r`.

FB-MEBE changes how exploration latents are selected during online training.
Instead of only sampling random `z` from the sphere, it samples many latents from
rare achieved behaviors. In this repo that is implemented by fitting a
normalizing-flow density estimator over selected goal coordinates and sampling
from replay-buffer goals with probability proportional to inverse density.

## System Components

The training system has five main components:

| Component | Code | Runtime role |
|---|---|---|
| Isaac Lab Go2 task | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py` | Simulates Go2 and returns FB-specific observation groups. |
| Training workspace | `scripts/reinforcement_learning/fb_mod/pretrain.py:108` | Creates env, agent, replay buffer, metrics, evaluation, and checkpoint directories. |
| Replay buffer | `scripts/reinforcement_learning/fb_mod/buffer.py:44` | Stores nested transition dictionaries. |
| FB agent | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:36` | Updates F, B, actor, optional regularization critic, and density sampler. |
| Play loader | `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py:9` | Rebuilds actor/B networks from saved config and loads checkpoint weights. |

## What This Tutorial Preserves

- FB factorization and actor objective from the paper.
- Reward inference with `E[B(s) r(s)]`.
- Go2 action semantics: 12-D action in `[-1, 1]`, scaled by `0.5`, added to the
  nominal joint pose.
- Isaac Lab timing: 200 Hz simulation and 50 Hz control through decimation `4`.
- The repo's observation groups: `policy`, `obs`, `goal`, `critic`, and `raw`.
- Evaluation on command rewards rather than task-specific retraining.

## What This Tutorial Simplifies

- The minimal implementation skips W&B and uses TensorBoard-friendly local logs.
- The minimal implementation uses a small, readable config and a clean module
  layout instead of the original Hydra-heavy workspace style.
- The minimal implementation keeps inverse-density exploration simple and
  testable. It does not reproduce every normalizing-flow detail from the repo.
- The tutorial does not claim hardware transfer reproduction.

## First Command To Run

For reading the existing repo:

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

For the clean tutorial implementation:

```bash
python -m tutorial.min_implementation.scripts.train \
    --config tutorial/min_implementation/configs/go2_fb.yaml \
    --num-envs 64 \
    --steps 1000 \
    --no-video
```
