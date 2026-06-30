# Debugging And Validation

## Local Runtime Check

Before training Go2, check the runtime:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
nvidia-smi
```

For this workspace, the current result is:

- PyTorch imports.
- CUDA is not available.
- `nvidia-smi` cannot communicate with a driver.
- A minimal Isaac Sim train attempt reaches simulator startup but reports no
  CUDA-capable device.
- The same attempt fails environment creation because the Go2 USD asset URL
  cannot be resolved locally:
  `http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/IsaacLab/Robots/Unitree/Go2/go2.usd`.

That means full Go2 training cannot be validated in this local runtime.

## Import Order

Isaac Lab scripts must launch the app before importing modules that require
simulator extensions. The original script does this in
`scripts/reinforcement_learning/fb_mod/pretrain.py`.

If you see `ModuleNotFoundError: No module named 'omni.kit'`, verify:

1. Isaac Sim is installed in the active environment.
2. You are using the Isaac Lab launch pattern.
3. The app is launched before simulator-dependent imports.

## Shape Checks

The Go2 task should return:

| Key | Expected dimension |
|---|---:|
| `policy` | 45 |
| `obs` | 34 |
| `goal` | 10 |
| `critic` | 58 |
| `action` | 12 |

If a shape mismatch appears, check:

- `go2_cfg_base.py`
- `go2_env.py:_get_observations`
- agent config dimensions copied in `pretrain.py:427`

## Reset-Crossing Transitions

The original trainer filters transitions where `s'` came from a reset. Preserve
this logic in any rewrite. Invalid reset-crossing transitions corrupt the FB
temporal-difference target.

Original code:

```text
scripts/reinforcement_learning/fb_mod/pretrain.py:235
```

## Replay Buffer Contract

Training transitions must contain:

```text
observation
action
next.observation
next.terminated
next.reward_reg
```

Play replay samples must contain at least:

```text
goal
raw
```

Check:

- `scripts/reinforcement_learning/fb_mod/buffer.py:44`
- `scripts/reinforcement_learning/fb_mod/play.py:161`

## Reward Inference Failures

If play fails in reward inference, inspect `raw` keys. The reward function
expects:

```text
vx, vy, vz, wz, gx, gy, gz, base_height
```

Code:

- `scripts/reinforcement_learning/toolbox/functions_reward.py:126`
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:225`

## Checkpoint Mismatch

The loader rebuilds networks from the saved `hydra_config.yaml`. If you use a
model checkpoint with the wrong config, loading can fail or silently produce
incorrect shapes.

Always keep these paired:

- `hydra_config.yaml`
- `models/model_step_<step>.pt`
- `models/replay_buffer_step_<step>.pt`

## Useful Smoke Commands

Small main-repo train:

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

Minimal implementation unit tests:

```bash
python -m pytest tutorial/min_implementation/tests
```

In this workspace, `pytest` is not installed in the active `fb-mebe`
environment, so the pytest-style test functions were executed directly with
`python -B -c ...`.

Minimal implementation smoke train:

```bash
python -m tutorial.min_implementation.scripts.train \
    --config tutorial/min_implementation/configs/go2_fb.yaml \
    --num-envs 64 \
    --steps 1000 \
    --no-video
```

## Do Not Hide Failures

Do not weaken tests, reduce assertions, skip validation, or swallow simulator
errors to make training appear successful. If Isaac Sim, CUDA, assets, or task
registration are missing, report that directly.
