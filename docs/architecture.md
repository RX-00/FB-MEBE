# FB-MEBE Architecture

This document describes the repository as inspected from the checked-in files. It focuses on the FB-MEBE path in `scripts/reinforcement_learning/fb_mod/` and the custom Go2 Isaac Lab tasks in `source/isaaclab_tasks/isaaclab_tasks/direct/go2/`.

## Repository Shape

| Path | Role |
| --- | --- |
| `README.md` | Short project overview, install notes, and primary FB training command. |
| `isaaclab.sh` | Utility wrapper inherited from upstream Isaac Lab. Some options still reference upstream files that are not present in this FB-MEBE checkout. |
| `source/isaaclab/` | Core Isaac Lab Python package. `setup.py` declares the `isaaclab` package and Isaac Sim 4.5.0 classifier. |
| `source/isaaclab_assets/` | Isaac Lab asset package, including robot configs such as `isaaclab_assets.robots.unitree.UNITREE_GO2_CFG`. |
| `source/isaaclab_tasks/` | Task package. This fork adds direct Go2 FB tasks under `isaaclab_tasks/direct/go2/`. |
| `source/isaaclab_rl/` | RL integration package. It exposes RSL-RL wrappers and config classes used by `scripts/reinforcement_learning/rsl_rl/`. |
| `source/isaaclab_mimic/` | Isaac Lab mimic/data generation package inherited from upstream. |
| `scripts/reinforcement_learning/fb_mod/` | Main FB-MEBE implementation for Isaac Lab Go2 experiments. |
| `scripts/reinforcement_learning/fb/url_benchmark/` | URLB-style benchmark code adapted from a separate codebase; it has its own README and DMC task files. |
| `scripts/reinforcement_learning/rsl_rl/` | Standard RSL-RL train/play scripts for registered Isaac Lab tasks. |
| `scripts/environments/` | Utility agents and environment listing scripts. |
| `bash/` | Thin shell entry points for FB workflows. Some inherited cluster helper scripts remain but reference the removed Docker tooling. |
| `pictures/` | README image assets. |

The top-level `docs/` directory contains repository-facing Markdown documentation. It is not currently a Sphinx documentation tree.

## Package Loading And Task Registration

`source/isaaclab_tasks/isaaclab_tasks/__init__.py` imports task subpackages through `isaaclab_tasks.utils.import_packages`. Registered Gymnasium environments become available after importing `isaaclab_tasks`.

Go2 task registrations live in `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py`:

| Task ID | Entry point | Env config | Notes |
| --- | --- | --- | --- |
| `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0` | `env_default_abs.go2_env:Go2NormEnv` | `env_default_abs.go2_cfg_rnd_full:Go2FlatEnvNormCfg` | Absolute joint-position control. |
| `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-INC-v0` | `env_default_inc.go2_env_incremental:Go2_Incremental_Env` | `env_default_inc.go2_cfg_rnd_full_incremental:Go2FlatEnvNormCfg` | Incremental action control based on current joint position. |
| `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-KAIST-v0` | `env_KAIST_abs.go2_env_KAIST:Go2_KAIST_Env` | `env_KAIST_abs.go2_cfg_KAIST:Go2FlatEnvNormKAISTCfg` | Adds gait phase features and barrier-style regularization. |
| `Isaac-Flat-Unitree-Go2-FB-v0` | `go2_env:Go2NormEnv` | `go2_cfg_fix_f:Go2FlatEnvNormCfg` | Stale registration: `direct/go2/go2_env.py` and `direct/go2/go2_cfg_fix_f.py` are not present. |

Cartpole direct tasks are registered in `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/__init__.py`, including `Isaac-Cartpole-Direct-v0`. The FB cartpole config points at this task through `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_cartpole.yaml`.

Task configs are loaded by `source/isaaclab_tasks/isaaclab_tasks/utils/parse_cfg.py`. The FB scripts call `load_cfg_from_registry(task, "env_cfg_entry_point")`, then patch device, number of environments, seed, and video resolution.

## Go2 Environment Contract

The base Go2 config is `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py`:

| Field | Value in `Go2_Base_Cfg` |
| --- | --- |
| `episode_length_s` | `20.0` |
| `decimation` | `4` |
| `sim.dt` | `1 / 200` |
| `action_scale` | `0.50` |
| `action_space` | `12` |
| `policy_space` | `33 + 12` |
| `observation_space` | `33 + 1` |
| `goal_space` | `10` |
| `critic_space` | `33 + 1 + 8 + 12` |
| `scene.num_envs` | `4096` default before Hydra overrides |

`Go2NormEnv` in `env_default_abs/go2_env.py` returns an observation dictionary with these keys:

| Key | Intended consumer | Source |
| --- | --- | --- |
| `policy` | Actor policy | Noisy root velocities, projected gravity, joint position offsets, joint velocities, previous actions. |
| `obs` | Forward map `F` | Prefix of raw critic observation. |
| `goal` | Backward map `B` | Prefix of raw critic observation, including velocity, gravity, and height targets. |
| `critic` | Optional critic | Raw state, contacts, feet state, and previous actions. |
| `raw` | Reward inference | Dictionary with named tensors such as `vx`, `vy`, `wz`, `gx`, `gy`, `gz`, and `base_height`. |

The FB reward code depends on the named raw dictionary. `scripts/reinforcement_learning/toolbox/functions_reward.py` expects `obs` dictionaries to contain:

`vx`, `vy`, `vz`, `wz`, `gx`, `gy`, `gz`, and `base_height`.

`scripts/reinforcement_learning/toolbox/config_task.py` defines default commands and task command samples:

| Task | Modes observed in code | Sampled keys |
| --- | --- | --- |
| `locomotion` | `list`, `random` | `vx`, `vy`, `wz` |
| `orientation` | `list` | `gx`, `gy`, `gz` |

The environment action path differs by task:

| Variant | Action processing |
| --- | --- |
| ABS | `processed_actions = cfg.action_scale * actions + default_joint_pos` in `Go2NormEnv._pre_physics_step`. |
| INC | `processed_actions = cfg.action_scale * actions + current_joint_pos` in `Go2_Incremental_Env._pre_physics_step`. |
| KAIST | Inherits ABS action handling, adds `sin`/`cos` gait phase features and `barrier` regularization in `Go2_KAIST_Env`. |

Termination behavior is controlled by `Go2NormEnv.termination_type`. The default is `"contact"`. `FB_VecEnvWrapper.eval_task()` sets it to `"none"` during evaluation and fixes `_commands`; `train_task()` restores `"contact"`.

Isaac Lab `DirectRLEnv` uses `cfg.observation_space` to build `single_observation_space["policy"]`. The current Go2 config also defines `policy_space` and uses `observation_space` as the FB forward-map `F` dimension, which mixes two contracts. The better long-term contract is:

- `cfg.observation_space` should match the actor policy observation returned as `observations["policy"]`.
- FB-specific dimensions such as the forward-map `F` input should live in a separate field, for example `fb_observation_space` or `forward_space`.
- `Go2NormEnv.__init__` should validate `observations["policy"]` against the Isaac Lab policy space and validate `observations["obs"]` against the FB forward-map dimension.

If making the smallest local fix without renaming fields, comparing `observations["policy"]` to `cfg.policy_space` is more consistent with the current `pretrain.py` and `_get_observations()` code. It still leaves Isaac Lab's `single_observation_space["policy"]` inconsistent because that space is derived from `cfg.observation_space`.

## FB Training Flow

Primary file: `scripts/reinforcement_learning/fb_mod/pretrain.py`.

Flow:

1. Parse Hydra config from `scripts/reinforcement_learning/fb_mod/configs/`.
2. Launch Isaac Lab through `isaaclab.app.AppLauncher`.
3. Import `isaaclab_tasks` indirectly through task utilities so Gymnasium task registrations are available.
4. Load the task config with `load_cfg_from_registry(hydra_cfg.env.task, "env_cfg_entry_point")`.
5. Override `env_cfg.sim.device`, `env_cfg.scene.num_envs`, `env_cfg.seed`, and `env_cfg.viewer.resolution`.
6. Copy environment dimensions into `hydra_cfg.agent.model`: `policy_dim`, `obs_dim`, `goal_dim`, `critic_dim`, and `action_dim`.
7. Set `hydra_cfg.train.replay_buffer_capacity = env.num_envs * train.replay_buffer_N`.
8. Create `WORKSPACE`, including Gymnasium env, optional video wrappers, `FB_VecEnvWrapper`, an FB agent, `DictBuffer`, metrics classes, command sampler, and reward function.
9. Run the training loop:
   - collect transitions from the vectorized env;
   - discard reset-crossing transitions using the time-buffer check;
   - update the replay buffer;
   - update the FB agent after `num_seeding_steps`;
   - periodically evaluate locomotion and orientation commands;
   - periodically log metrics and save model artifacts.

`pretrain.py` supports two agent choices through `hydra_cfg.train.agent`:

| `train.agent` | Class |
| --- | --- |
| `meta` | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:FBAgent` |
| `crl` | `scripts/reinforcement_learning/fb_mod/agent_crl/agent.py:FB_CRL_AGENT` |

`scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml` sets `train.agent: meta` and overrides FB hyperparameters for Go2. The base config sets `train.agent: crl`.

## Hydra Config Structure

FB configs live under `scripts/reinforcement_learning/fb_mod/configs/`:

| File | Purpose |
| --- | --- |
| `Isaaclab_pretrain_config_base.yaml` | Base FB training config. Its default task string is stale: `Isaac-Flat-Unitree-Go2-Rnd-full-FB-v0` does not match the registered Go2 task IDs. |
| `Isaaclab_pretrain_config_go2.yaml` | Main Go2 training config used by `bash/fb_pretrain.sh`; overrides task, env count, W&B defaults, agent type, and network/training hyperparameters. |
| `Isaaclab_pretrain_config_cartpole.yaml` | Minimal cartpole FB config for `Isaac-Cartpole-Direct-v0`. |
| `Isaaclab_fb_play_config_base.yaml` | Play/eval config. It defaults to `latest` run and artifact selection and is resolved by `play_config.py`. |
| `agent/FBAgent.yaml` | Default FB agent hyperparameters and model architecture. Several model dimensions are initialized to `0` and filled from the environment in `pretrain.py`. |

Hydra is configured with `hydra.run.dir: .` and `hydra.job.chdir: false`, so scripts keep the current working directory instead of writing into Hydra's default `outputs/` directory.

## Replay Buffer And Transition Schema

`scripts/reinforcement_learning/fb_mod/buffer.py:DictBuffer` stores nested dictionaries on the configured device. `pretrain.py` writes transitions with this structure:

```text
{
  "observation": {
    "policy": ...,
    "obs": ...,
    "goal": ...,
    "critic": ...,
    "raw": {...}
  },
  "action": ...,
  "next": {
    "observation": {...},
    "terminated": ...,
    "reward_reg": ...
  }
}
```

The buffer initializes tensor storage from the first inserted transition. New insertions must preserve the same nested keys and leading batch dimension.

## Agent Checkpoint Contract

Both `FBAgent.save()` and `FB_CRL_AGENT.save()` write the same keys:

```text
{
  "actor": actor state_dict,
  "policy_normalizer": policy normalizer state_dict,
  "B": backward map state_dict,
  "B_normalizer": backward-map normalizer state_dict
}
```

`scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py::FBPolicyLoader` depends on that contract. Given `path/to/run/models/model_step_<t>.pt`, it resolves the run config at `path/to/run/hydra_config.yaml`, rebuilds actor and backward-map networks from that config, loads the checkpoint keys, and exposes:

| Method | Role |
| --- | --- |
| `act(obs, z, mean=True)` | Produces an action from policy observation and latent `z`. |
| `backward_map(goal)` | Maps goal observations into FB latent space. |
| `reward_inference(Z_Bs, reward)` | Projects reward weights into a normalized latent command. |
| `refresh_z(z, step_count)` | Resamples exploration latents based on `update_z_every_step`. |

Play artifact selection is centralized in `scripts/reinforcement_learning/fb_mod/play_config.py`:

| Consumer | Resolver behavior |
| --- | --- |
| `fb_mod/play.py` | Resolves `path`, `model_step`, and `replay_buffer_step`; loads both model and replay buffer. |
| `fb_mod/play_xbox.py` | Uses the same resolver as `play.py`; loads both model and replay buffer. |
| `fb_mod/play_collect.py` | Uses the same run/model resolver with `require_replay_buffer=False`; collects a new offline buffer. |

Accepted run selectors include `--run-dir`, `--path`, `--model-step`, `--replay-buffer-step`, and Hydra-style overrides for `Isaaclab_fb_play_config_base.yaml`. When `path: latest`, `play_config.py` searches `exp_*/**/hydra_config.yaml` and chooses the run with the newest model artifact mtime.

## Generated Artifacts

`pretrain.py` writes under:

```text
exp_<train.machine>/fb_mod/<env.task>/<wandb.group>/<timestamp>/
```

Observed generated files and directories:

| Artifact | Created by | Meaning |
| --- | --- | --- |
| `hydra_config.yaml` | `pretrain.py`; intended stale offline path | Resolved training config used by loaders and reproducibility. |
| `models/model_step_<t>.pt` | `pretrain.py`; intended stale offline path | Actor/backward-map checkpoint. |
| `models/replay_buffer_step_<t>.pt` | `pretrain.py`; intended stale offline path | Sample of stored observations for reward inference. |
| `videos_pretrain/` | Video wrappers when training video is enabled. |
| `videos_eval/` | Video wrappers when eval video is enabled. |
| `offline_data.pt` | `play_collect.py` | Full collected offline buffer saved under `play_cfg.path`. |

The current workspace contains one observed Go2 ABS run from June 26, 2026:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46/
```

It confirms the checkpoint/replay-buffer contract at steps `50000`, `100000`, and `150000`, and the final trained policy is:

```text
exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46/models/model_step_150000.pt
```

The same run also contains `videos_pretrain/pretrain-step-150000.mp4`, because `env.video_train` was enabled in the resolved `hydra_config.yaml`.

`.gitignore` ignores `exp_local/`, but it does not ignore every possible `exp_<machine>/` directory. If `train.machine=cluster`, check generated `exp_cluster/` output before committing.

## Removed Upstream Scaffolding

This fork keeps substantial Isaac Lab source code, but it is not a complete upstream Isaac Lab checkout. The `docker/` directory has been removed from the core FB-MEBE implementation. Remaining scripts under `bash/euler/` and `bash/tars_case/` reference `docker/container.py` or `docker/cluster/cluster_interface.sh`; treat them as stale inherited notes until they are rewritten for the current repository layout.

`isaaclab.sh` is also inherited from upstream Isaac Lab. Use the paths that are validated for this fork, such as `--install`, `--python`, `--sim`, and `--format`. Options such as `--test`, `--docs`, and `--docker` still reference upstream helper files or directories that are absent here.

## Known Inconsistencies And Risks

These are observed from repository files and should not be treated as fixed:

- `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` is stale against the current configs: it reads old `env.video`, `env.video_interval`, and `env.video_length` keys, hard-codes `offline_data_path` to `/home/jiajun_hu/.../offline_data.pt`, and calls `ConvexHull` without importing it. Treat offline pretraining as not currently validated until those are fixed.
- `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_fb_play_config_base.yaml` defaults to `path: latest`. This is convenient, but explicit `--run-dir` is safer when multiple runs exist.
- `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_base.yaml` uses an unregistered-looking task ID with lowercase `full`. Use `Isaaclab_pretrain_config_go2.yaml` or a registered task ID.
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` registers `Isaac-Flat-Unitree-Go2-FB-v0` to missing module paths.
- `isaaclab.sh --test`, `isaaclab.sh --docs`, and `isaaclab.sh --docker` reference upstream Isaac Lab helper paths that are not present in this checkout.
- Remaining Euler/TARS notes under `bash/` reference the removed Docker tooling.
