# Configs And Experiments

## Config Directory

FB configs live under:

```text
scripts/reinforcement_learning/fb_mod/configs/
```

Important files:

| File | Role |
|---|---|
| `Isaaclab_pretrain_config_go2.yaml` | Main Go2 training config. |
| `Isaaclab_pretrain_config_base.yaml` | Base train/env/W&B settings. |
| `Isaaclab_pretrain_config_cartpole.yaml` | Cartpole FB config. |
| `Isaaclab_fb_play_config_base.yaml` | Play/eval defaults. |
| `agent/FBAgent.yaml` | Agent model and optimizer defaults. |

## Main Go2 Defaults

`scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml`
sets:

| Field | Value |
|---|---|
| `env.device` | `cuda:0` |
| `env.headless` | `true` |
| `env.task` | `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0` |
| `env.num_envs` | `2048` |
| `train.num_train_steps` | `150_000` |
| `train.num_seeding_steps` | `1000` |
| `train.interval_update` | `10` |
| `train.num_updates` | `10` |
| `train.interval_eval` | `20000` |
| `train.interval_save_model` | `50000` |
| `train.save_buffer_size` | `100_000` |
| `agent.model.archi.z_dim` | `50` |
| `agent.train.batch_size` | `4096` |
| `agent.train.train_goal_ratio` | `0.8` |
| `agent.train.reg_coeff` | `20.0` |

## Hydra Override Pattern

Hydra overrides are passed as bare `key=value` arguments:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    env.num_envs=64 \
    train.num_train_steps=1000 \
    wandb.use_wandb=False
```

Use the Python entry point for overrides. `bash/fb_pretrain.sh` does not forward
extra arguments.

## Run Directory

`pretrain.py` creates:

```text
exp_<train.machine>/fb_mod/<env.task>/<wandb.group>/<timestamp>/
```

With default local settings this is under:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/<group>/<timestamp>/
```

Expected files:

```text
hydra_config.yaml
models/model_step_<step>.pt
models/replay_buffer_step_<step>.pt
videos_pretrain/
videos_eval/
```

Video directories appear only when matching video flags are enabled.

## Known Local Run

This workspace contains a generated local run:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46/
```

It contains checkpoints at:

- `50000`
- `100000`
- `150000`

`exp_local/` is generated output and ignored by Git, so do not assume it exists
in a fresh clone.

## Play Config

`scripts/reinforcement_learning/fb_mod/configs/Isaaclab_fb_play_config_base.yaml`
is resolved by `scripts/reinforcement_learning/fb_mod/play_config.py::load_play_configs`.

The loader supports:

- `--run-dir`
- `--path`
- `--model-step`
- `--replay-buffer-step`
- Hydra-style overrides

Prefer explicit run selection instead of `latest` when multiple runs exist.

## Experiment Reproduction Checklist

Before comparing to paper curves:

1. Verify the task ID is registered and points to the expected Go2 env/config.
2. Verify `env.num_envs`, `train.num_train_steps`, batch size, update frequency,
   and `z_dim`.
3. Disable W&B only if you do not need online logging.
4. Save the resolved `hydra_config.yaml`.
5. Save matching model and replay-buffer artifacts.
6. Evaluate using the same command lists and 250-step episode length.
7. Record whether video, domain randomization, and observation noise were
   enabled.
