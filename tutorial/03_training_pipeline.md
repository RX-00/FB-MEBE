# Training Pipeline

This document traces the checked-in training flow from command to checkpoint.

## 1. Command Entry

The shell shortcut is `bash/fb_pretrain.sh`:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2
```

Use the Python command directly when passing overrides:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    env.num_envs=64 \
    env.video_train=False \
    env.video_eval=False \
    train.num_train_steps=1000 \
    wandb.use_wandb=False
```

## 2. Hydra Config Composition

`scripts/reinforcement_learning/fb_mod/pretrain.py` reads configs from
`scripts/reinforcement_learning/fb_mod/configs/`.

Important files:

- `Isaaclab_pretrain_config_go2.yaml`: main Go2 config.
- `Isaaclab_pretrain_config_base.yaml`: inherited base config.
- `agent/FBAgent.yaml`: FB agent defaults.

The Go2 config overrides:

- `env.task`: `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0`
- `env.num_envs`: `2048`
- `train.agent`: `meta`
- `train.num_train_steps`: `150_000`
- `agent.model.archi.z_dim`: `50`
- `agent.train.train_goal_ratio`: `0.8`
- `agent.train.reg_coeff`: `20.0`

## 3. Isaac Lab Launch

`pretrain.py` launches Isaac Lab before importing simulator-dependent modules:

- `scripts/reinforcement_learning/fb_mod/pretrain.py`
- `isaaclab.app.AppLauncher(app_cfg).app`

This order matters. Importing many Isaac Lab modules before the app exists can
fail because simulator extensions are not loaded.

## 4. Environment Config

`env_cfg_from_hydra` is defined at
`scripts/reinforcement_learning/fb_mod/pretrain.py:419`.

It loads the registered task config:

```python
env_cfg = load_cfg_from_registry(hydra_cfg.env.task, "env_cfg_entry_point")
```

Then it patches:

- `env_cfg.sim.device`
- `env_cfg.scene.num_envs`
- `env_cfg.seed`
- `env_cfg.viewer.resolution`

## 5. Agent Dimensions

Before constructing the agent, `pretrain.py` copies environment dimensions
into the Hydra agent config:

| Config field | Source |
|---|---|
| `policy_dim` | `env_cfg.policy_space` |
| `obs_dim` | `env_cfg.observation_space` |
| `goal_dim` | `env_cfg.goal_space` |
| `critic_dim` | `env_cfg.critic_space` |
| `action_dim` | `env_cfg.action_space` |

These dimensions come from
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py:27`.

## 6. Workspace Construction

`WORKSPACE` starts at `scripts/reinforcement_learning/fb_mod/pretrain.py:108`.

It creates:

- The run directory under `exp_<machine>/fb_mod/<task>/<group>/<timestamp>/`.
- `hydra_config.yaml`.
- Optional W&B run.
- Gymnasium Isaac Lab env.
- Optional train/eval video wrappers.
- `FB_VecEnvWrapper`.
- FB agent: `FBAgent` when `train.agent: meta`.
- Replay buffer: `DictBuffer`.
- Metrics objects.
- Command sampler and reward function.

## 7. Replay Collection

Training starts in `WORKSPACE.train`.

The loop keeps a current transition dictionary `td`, with:

- `td["obs"]`: the environment observation dictionary.
- `td["time"]`: episode step count.
- `td["done"]`
- `td["reward_task"]`
- `td["reward_reg"]`

For the first `num_seeding_steps`, actions are random. After that, the actor
uses `agent.act(obs["policy"], z, mean=False)`.

The latent `z` is refreshed by `FBAgent.refresh_z` at
`scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:467`.

## 8. Valid Transition Filtering

The code avoids storing transitions that cross reset boundaries:

```python
indices = ((td["time"] + 1 == new_td["time"]) & (td["time"] != 1)).squeeze()
```

This matters because FB learns from valid `(s, a, s')` transitions. If `s'` is
the first observation after reset, it does not follow from the previous action.

## 9. Agent Update

Every `train.interval_update` steps after seeding, the workspace runs
`train.num_updates` gradient updates.

`FBAgent.update` at
`scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:157`:

1. Samples a replay batch.
2. Updates normalizers.
3. Filters plausible goals for density estimation.
4. Samples mixed `z` values.
5. Updates F/B with `update_fb`.
6. Optionally updates the regularization critic.
7. Updates actor every two agent updates.
8. Soft-updates target networks.

## 10. Evaluation During Training

`WORKSPACE.eval` starts at `pretrain.py:379`.

Evaluation:

1. Samples command dictionaries with `CMDSampler`.
2. Puts env into eval mode through `FB_VecEnvWrapper.eval_task`.
3. Samples replay observations/goals.
4. Computes command rewards with `RewardFunction.inference`.
5. Infers `z_r = agent.reward_inference(goal, reward.T)`.
6. Rolls out 250 steps with `agent.act(policy_obs, z_r, mean=True)`.
7. Logs task and regularization metrics.

## 11. Checkpoint Saving

Every `train.interval_save_model`, the training loop writes:

- `models/replay_buffer_step_<t>.pt`
- `models/model_step_<t>.pt`

The model checkpoint is written by
`scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:488`.

It contains:

- `actor`
- `policy_normalizer`
- `B`
- `B_normalizer`

The replay-buffer sample is needed later for zero-shot reward inference in
`play.py`.
