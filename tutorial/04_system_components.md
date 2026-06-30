# System Components

This file maps the main FB-MEBE components across the paper concept and the
checked-in implementation.

| Component | Paper role | Checked-in code | Verify |
|---|---|---|---|
| Go2 MDP | Environment for online reward-free data collection | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py` | Isaac Lab reset/step smoke. |
| Actor observation | State input to `pi_z` | `go2_env.py:user_return_policy_obs` | Shape `45`. |
| Forward observation | State input to F | `go2_env.py:_get_observations` and `Go2_Base_Cfg.observation_space` | Shape `34`. |
| Goal observation | Input to B and density sampler | `go2_env.py:_get_observations` and `Go2_Base_Cfg.goal_space` | Shape `10`. |
| Raw observation | Reward inference values | `go2_env.py:user_return_dict` | Includes reward keys expected by `functions_reward.py`. |
| Replay storage | Online transition dataset | `scripts/reinforcement_learning/fb_mod/buffer.py::DictBuffer` | Nested transition schema remains stable. |
| Forward map F | Successor feature factor | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py::FBModel` | Used by `FBAgent.update_fb`. |
| Backward map B | Feature basis and reward projection | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py::FBModel` | Saved by `FBAgent.save` and loaded by `FBPolicyLoader`. |
| Actor | Chooses action for latent `z` | `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py::FBAgent.update_td3_actor` | Actor checkpoint loads in play. |
| MEBE sampler | Rare-behavior exploration | `scripts/reinforcement_learning/fb_mod/density_estimator/agent_normalizing_flow.py::NF_AGENT` | `train_goal_ratio` controls use in `sample_mixed_z`. |
| Reward inference | Convert command reward into `z_r` | `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py::FBPolicyLoader.reward_inference` | Requires saved replay-buffer sample. |
| Checkpoint | Save actor/B and replay sample | `FBAgent.save`; `pretrain.py` model/replay save block | Keep model and replay-buffer steps paired. |

For deeper explanations, read:

- `03_training_pipeline.md`
- `04_environment_and_task.md`
- `05_models_losses_and_objectives.md`
- `07_evaluation_and_play.md`
