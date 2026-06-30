# Main Codebase Map

This file maps the FB-MEBE research concepts to the checked-in implementation.
It intentionally points at the production training and play paths in this
repository, not at a separate tutorial implementation.

| Concept | Main repo implementation | Runtime role | Notes and checks |
|---|---|---|---|
| Training entry point | `scripts/reinforcement_learning/fb_mod/pretrain.py` | Composes Hydra config, launches Isaac Lab, builds `WORKSPACE`, collects replay, updates the agent, evaluates, and saves artifacts. | Use `--config-name=Isaaclab_pretrain_config_go2` for the main Go2 path. |
| Training shell shortcut | `bash/fb_pretrain.sh` | Calls `pretrain.py` with the Go2 config. | It does not forward extra CLI arguments; run `pretrain.py` directly for Hydra overrides. |
| Multi-seed shortcut | `bash/fb_pretrain_multi.sh` | Runs repeated Go2 FB training jobs with different seeds and fixed overrides. | Check GPU/device settings before launching multiple long runs. |
| Go2 task registration | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` | Registers Gymnasium task IDs and points each ID at an env class and config. | Prefer `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0`; avoid the stale `Isaac-Flat-Unitree-Go2-FB-v0` registration. |
| Go2 base config | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py` | Defines timing, action scale, observation dimensions, goal dimensions, and default env count. | Actor policy observations are 45-D; FB forward observations are 34-D. |
| Go2 env dynamics and observations | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py` | Applies actions, computes observations, rewards, regularization reward, termination, and reset behavior. | Preserve observation keys `policy`, `obs`, `goal`, `critic`, and `raw`. |
| Environment wrapper | `scripts/reinforcement_learning/fb_mod/wrapper/wrapper_env.py` | Adapts Isaac Lab env outputs to the transition dictionary consumed by FB training and eval. | `eval_task()` disables contact termination and writes command tensors. |
| Video wrappers | `scripts/reinforcement_learning/fb_mod/wrapper/wrapper_video.py` | Records train/eval videos when configured. | Outputs live under each run's `videos_pretrain/` or `videos_eval/`. |
| Replay buffer | `scripts/reinforcement_learning/fb_mod/buffer.py` | Stores nested transition dictionaries on the configured device. | Inserted transitions must keep the same nested keys and leading batch dimension. |
| FB agent selector | `scripts/reinforcement_learning/fb_mod/pretrain.py` | Chooses `agent_meta.fb.agent.FBAgent` for `train.agent: meta` or `agent_crl.agent.FB_CRL_AGENT` for `train.agent: crl`. | The Go2 config uses `train.agent: meta`. |
| FB model | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py` | Builds F, B, actor, optional regularization critic, target networks, and normalizers. | Saved play checkpoints include actor, B, and normalizers, not F. |
| FB losses and updates | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py` | Implements contrastive FB TD loss, actor update, optional regularization critic, latent refresh, density sampling, and checkpoint save. | Check `update_fb`, `update_td3_actor`, `sample_mixed_z`, and `refresh_z`. |
| Density estimator | `scripts/reinforcement_learning/fb_mod/density_estimator/` | Fits a normalizing-flow density model and samples low-density achieved goals for MEBE exploration. | `agent.train.train_goal_ratio` controls the `sample_mixed_z` training batch mix; rollout-time `refresh_z` has a separate hard-coded `p_reverse = 0.8` after a buffer-size gate. |
| Command sampling | `scripts/reinforcement_learning/toolbox/config_task.py` | Defines locomotion and orientation command modes. | `FB_VecEnvWrapper.eval_task()` expects `[vx, vy, wz]` command tensors. |
| Reward inference helpers | `scripts/reinforcement_learning/toolbox/functions_reward.py` | Computes command rewards from raw replay observations for play/eval. | Raw observations must include `vx`, `vy`, `vz`, `wz`, `gx`, `gy`, `gz`, and `base_height`. |
| Training metrics | `scripts/reinforcement_learning/toolbox/dataclass_metrics.py` | Structures train/eval metric fields before logging. | W&B logging is optional through Hydra config. |
| Play config resolver | `scripts/reinforcement_learning/fb_mod/play_config.py` | Resolves run directory, model step, replay-buffer step, and saved training config. | Prefer explicit `--run-dir` when multiple `exp_*` runs exist. |
| Policy loader | `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py` | Rebuilds actor/B from `hydra_config.yaml`, loads checkpoint weights, and exposes action/reward-inference helpers. | The loader expects `hydra_config.yaml` two directories above the model file. |
| Play script | `scripts/reinforcement_learning/fb_mod/play.py` | Loads a saved model and replay buffer, infers `z_r`, runs eval, logs metrics, and can record video. | Requires matching `model_step_<t>.pt` and `replay_buffer_step_<t>.pt`. |
| Xbox play script | `scripts/reinforcement_learning/fb_mod/play_xbox.py` | Runs a saved policy with controller-driven commands. | Hardware assumptions are not fully documented in this repo. |
| Offline data collection | `scripts/reinforcement_learning/fb_mod/play_collect.py` | Rolls out a saved policy and writes `offline_data.pt`. | Uses the same run/model resolver as play without requiring a replay-buffer artifact. |
| Offline pretraining | `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` | Intended to train from offline data. | Currently stale: old `env.video*` config keys, hard-coded absolute `offline_data_path`, and missing `ConvexHull` import. Fix before relying on it. |

## Separate Paths

The standard RSL-RL scripts under `scripts/reinforcement_learning/rsl_rl/` are
separate from the FB-MEBE training path. They use Isaac Lab task registration
and RSL-RL wrappers, but they do not use the FB agent, FB replay buffer, or
reward-inference play flow.
