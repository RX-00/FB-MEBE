# Environment And Task

This document explains the Go2 Isaac Lab task used by FB-MEBE.

## Registration

Go2 tasks are registered in
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py`.

The default training task is:

```text
Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0
```

It maps to:

- Env class:
  `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:26`
- Env config:
  `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_rnd_full.py`

Avoid `Isaac-Flat-Unitree-Go2-FB-v0`; that registration points to missing module
paths in this checkout.

## Timing And Action Interface

The base config is
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py:19`.

| Field | Value | Meaning |
|---|---:|---|
| `episode_length_s` | `20.0` | Max episode duration. |
| `sim.dt` | `1 / 200` | Physics step, 200 Hz. |
| `decimation` | `4` | One policy action every 4 sim steps. |
| control rate | `50 Hz` | `200 / 4`. |
| `action_space` | `12` | One action per actuated Go2 joint. |
| `action_scale` | `0.50` | Joint-position offset scale. |

Absolute control is implemented in
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:155`:

```text
processed_actions = action_scale * actions + default_joint_pos
```

The policy action is clipped to `[-1, 1]`.

## Observation Groups

`Go2NormEnv._get_observations` at
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:163`
returns a dictionary:

| Key | Dimension | Used by | Meaning |
|---|---:|---|---|
| `policy` | `45` | Actor | Noisy velocity, gravity, joint state, and previous action. |
| `obs` | `34` | Forward map F | Clean state prefix for FB. |
| `goal` | `10` | Backward map B | Clean low-dimensional behavior projection. |
| `critic` | `54` | Optional regularization critic | Clean state, contacts, foot heights, and actions. |
| `raw` | dict | Reward inference | Named tensors such as `vx`, `vy`, `wz`, `gx`, `gy`, `gz`, and `base_height`. |

The configured dimensions are in
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py:27`.
The critic dimension is `33 + 1 + 8 + 12 = 54`.

## Actor Observation

`user_return_policy_obs` at
`go2_env.py:194` concatenates:

- base linear velocity in body frame, 3
- base angular velocity in body frame, 3
- projected gravity in body frame, 3
- joint position offsets, 12
- joint velocities, 12
- previous actions, 12

Noise is added to all but the previous-action block when `cfg.add_noise` is
true.

## F Observation

`obs` is the prefix of `user_return_critic_obs`:

- base linear velocity, 3
- base angular velocity, 3
- projected gravity, 3
- base height, 1
- joint position offsets, 12
- joint velocities, 12

This gives `34` dimensions.

## B Goal Observation

`goal` is the first 10 dimensions of the clean critic observation:

- base linear velocity, 3
- base angular velocity, 3
- projected gravity, 3
- base height, 1

The paper justifies learning `B` on a lower-dimensional projection in
`Supplementary_Materials.tex`, Observation Space.

## Raw Observation Dictionary

`user_return_dict` at `go2_env.py:225` returns named values used by reward
inference:

- `vx`, `vy`, `vz`
- `wx`, `wy`, `wz`
- `gx`, `gy`, `gz`
- `base_height`
- joint and foot diagnostics

`scripts/reinforcement_learning/toolbox/functions_reward.py:126` expects these
names.

## Task Reward

The environment's training task reward is in
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:282`.

It tracks:

- XY linear velocity command.
- Yaw angular velocity command.
- Upright projected gravity.

The returned task reward is the product of reward terms in `_get_rewards`.

## Regularization Reward

`user_return_reguarization_reward` at `go2_env.py:310` currently includes:

- joint acceleration penalty
- action-rate penalty
- foot-slide penalty

`get_reg_reward` returns the summed regularization reward for the optional
critic.

## Commands

Command sampling lives in `scripts/reinforcement_learning/toolbox/config_task.py`.

Locomotion commands:

- random/list modes over `vx`, `vy`, `wz`

Orientation commands:

- list mode over projected gravity `gx`, `gy`, `gz`

`FB_VecEnvWrapper.eval_task` writes `[vx, vy, wz]` commands into the environment
and disables contact termination for evaluation.

## Reset And Termination

`_get_dones` starts at `go2_env.py:376`.

Default training termination is contact-based:

- base, head, thigh, calf, or hip contact can terminate an episode.
- timeouts occur at max episode length.

`FB_VecEnvWrapper.eval_task` sets `termination_type = "none"` during evaluation.
After evaluation, `train_task` restores `"contact"`.

## Domain Randomization

The randomized full config is
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_rnd_full.py`.

It randomizes:

- friction
- base mass
- base center of mass
- link mass and center of mass
- reset pose and root velocity
- joint offsets

These match the paper's simulation setup at a high level.
