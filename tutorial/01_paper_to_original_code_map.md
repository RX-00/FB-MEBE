# Paper To Original Code Map

This file maps paper concepts to the current repository. When a mapping is not
directly verified from code or paper source, it is marked `TODO: verify`.

| Paper concept | Paper source | Original code | Role in system | Confidence |
|---|---|---|---|---|
| Reward-free MDP and online data collection | `ch03-background.tex`, Background | `scripts/reinforcement_learning/fb_mod/pretrain.py::WORKSPACE.train` | The training loop collects transitions from the vectorized Go2 environment while learning. | High |
| Successor measure factorization `F(s,a,z)^T B(s')` | `ch03-background.tex`, Eq. `fb_factorization` | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.update_fb` | `update_fb` forms `Ms = F @ B.T` for contrastive TD learning. | High |
| FB temporal-difference contrastive loss | `ch03-background.tex`, Eq. `fb_loss` | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.update_fb` | Uses target F/B networks, diagonal attraction, off-diagonal penalty, and target bootstrapping. | High |
| Backward-map orthonormality regularization | `Supplementary_Materials.tex`, FB details | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.update_fb` | Adds covariance regularization on `B` to prevent representation collapse. | High |
| Actor objective `-F(s,a,z)^T z` | `ch03-background.tex`, Eq. `actor_loss` | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.update_td3_actor` | Actor samples actions and maximizes the FB Q estimate. | High |
| Regularized actor objective with `Q_reg` | `ch05-method.tex`, Eq. `actor_loss_with_reg`; `Supplementary_Materials.tex`, Regularized Exploration | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.update_critic` and `FBAgent.update_td3_actor` | Optional critic learns regularization reward and contributes to actor loss. | High |
| Reward inference `z_r = E[B(s) r(s)]` | `ch03-background.tex`, reward inference paragraph | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py::FBModel.reward_inference`; `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py::FBPolicyLoader.reward_inference` | Projects command rewards over replay-buffer goals into a latent command for play/eval. | High |
| Maximum entropy behavior exploration | `ch05-method.tex`, Maximum Entropy Behavior Exploration | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:140`; `density_estimator/agent_normalizing_flow.py:24` | Mixes inverse-density replay-buffer goals with random sphere latents. | High |
| Inverse-density sampling `q(s)^(-beta)` | `ch05-method.tex`, Eq. `sample_inv` and `practical_fb_mebe` | `scripts/reinforcement_learning/fb_mod/density_estimator/agent_normalizing_flow.py::NF_AGENT.inverse_sample_from_buffer` | Samples replay-buffer goals using inverse estimated density. | High |
| Normalizing-flow density model | `Supplementary_Materials.tex`, Normalizing Flow table | `scripts/reinforcement_learning/fb_mod/density_estimator/model_normalizing_flow.py:96` | RealNVP-style flow estimates density over selected goal coordinates. | High |
| 80 percent MEBE / 20 percent random latent mix | `ch06-experiments.tex`, Baselines paragraph; `Supplementary_Materials.tex`, hyperparameters | `scripts/reinforcement_learning/fb_mod/configs/Isaaclab_pretrain_config_go2.yaml`; `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.sample_mixed_z` | `train_goal_ratio: 0.8` controls the training-batch mix. Rollout `refresh_z` separately uses hard-coded `p_reverse = 0.8` after its density-buffer gate. | High |
| Go2 robot with 12-D action space | `ch06-experiments.tex`, Environment paragraph | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py::Go2_Base_Cfg` | Sets action dimension to 12. | High |
| 200 Hz sim, 50 Hz control | `ch06-experiments.tex`, Environment paragraph | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py::Go2_Base_Cfg` | `sim.dt = 1/200`, `decimation = 4`, so policy/control runs at 50 Hz. | High |
| Joint-position control `q_target = q_nom + scale * action` | `Supplementary_Materials.tex`, Joint Control | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:155` | Converts actor action into joint-position targets. | High |
| Observation spaces for F, B, actor, reg critic | `Supplementary_Materials.tex`, Observation Space | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:163`; `go2_cfg_base.py:27` | Environment returns `policy`, `obs`, `goal`, `critic`, and `raw`. | High |
| Velocity and orientation command tasks | `ch06-experiments.tex`, Task Metrics | `scripts/reinforcement_learning/toolbox/config_task.py:30`; `config_task.py:59` | Defines locomotion and orientation command lists/ranges. | High |
| Command reward formula | `Supplementary_Materials.tex`, Task Reward Function | `scripts/reinforcement_learning/toolbox/functions_reward.py:126` | Computes command rewards from raw velocity, gravity, yaw-rate, and height observations. | High |
| Behavior entropy metric | `ch06-experiments.tex`, Main Results | `scripts/reinforcement_learning/toolbox/functions_entropy.py:3` | Computes histogram entropy over selected goal dimensions for logging. | Medium |
| Real Unitree Go2 deployment | `ch06-experiments.tex`, Hardware Tests | `scripts/reinforcement_learning/fb_mod/play_xbox.py`; `bash/fb_play_xbox.sh` | Repo has joystick play path, but hardware deployment setup is not fully documented in checked-in code. | TODO: verify |

## Important Code/Paper Mismatches

- The paper reward appendix defines separate locomotion and orientation rewards,
  but `scripts/reinforcement_learning/toolbox/functions_reward.py:126` computes
  all four terms together for inference. Treat exact task-specific reward
  decomposition as a point to verify before reproducing paper numbers.
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py:26`
  imports `.go2_cfg_fix_f.Go2FlatEnvNormCfg`, while the registered ABS task uses
  `env_default_abs.go2_cfg_rnd_full:Go2FlatEnvNormCfg`. This affects type hints,
  not the runtime registry.
- The stale registration `Isaac-Flat-Unitree-Go2-FB-v0` in
  `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` points to missing
  module paths. Use the `Rnd-Full` task IDs.
