# System Components

This file maps the main FB-MEBE components across the paper, original code, and
minimal implementation.

| Component | Paper role | Original code | Minimal code | Verify |
|---|---|---|---|---|
| Go2 MDP | Environment for online reward-free data collection | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py` | Reused through `tutorial/min_implementation/fbmebe_min/envs.py` | Isaac Lab reset/step smoke |
| Actor observation | State input to `pi_z` | `go2_env.py:user_return_policy_obs` | adapter preserves `obs["policy"]` | shape `45` |
| Forward observation | State input to F | `go2_env.py:_get_observations` | replay stores `obs` | shape `34` |
| Goal observation | Input to B and density sampler | `go2_env.py:_get_observations` | replay stores `goal`; density observes `goal` | shape `10` |
| Raw observation | Reward inference values | `go2_env.py:user_return_dict` | replay stores required raw keys | reward tests |
| Forward map F | Successor feature factor | `agent_meta/fb/model.py::FBModel` | `fbmebe_min/networks.py::ForwardMap` | network shape tests |
| Backward map B | Feature basis and reward projection | `agent_meta/fb/model.py::FBModel` | `fbmebe_min/networks.py::BackwardMap` | norm/shape tests |
| Actor | Chooses action for latent `z` | `agent_meta/fb/agent.py:update_td3_actor` | `fbmebe_min/agent.py::MinimalFBAgent.update` | synthetic update test |
| MEBE sampler | Rare-behavior exploration | `density_estimator/agent_normalizing_flow.py::NF_AGENT` | `fbmebe_min/density.py::InverseDensitySampler` | sampler test |
| Reward inference | Convert command reward into `z_r` | `loader/fb_net_loader.py::reward_inference` | `MinimalFBAgent.reward_inference` | synthetic reward inference test |
| Checkpoint | Save actor/B and replay sample | `agent_meta/fb/agent.py:save`; `pretrain.py` | `fbmebe_min/checkpoint.py`; `MinimalFBAgent.save` | save path smoke on train |

For deeper explanations, read:

- `03_training_pipeline.md`
- `04_environment_and_task.md`
- `05_models_losses_and_objectives.md`
- `07_evaluation_and_play.md`
