# Glossary

| Term | Meaning in this project | Where used |
|---|---|---|
| FB | Forward-Backward representations for zero-shot RL. | Paper background; `agent_meta/fb/` |
| FB-MEBE | FB with maximum entropy behavior exploration. | Paper method; `FBAgent.sample_mixed_z` |
| F | Forward map from state/action/latent to latent successor feature. | `agent_meta/fb/model.py` |
| B | Backward map from goal/state projection to latent feature. | `agent_meta/fb/model.py` |
| `z` | Latent behavior or reward embedding. | Actor, F, reward inference |
| `z_r` | Reward embedding inferred from replay states and task reward. | `play.py`, `FBPolicyLoader.reward_inference` |
| policy observation | Noisy actor input: velocities, gravity, joints, and previous action. | `go2_env.py:user_return_policy_obs` |
| F observation | Clean input used by the forward map. | `go2_env.py:_get_observations` |
| goal observation | Low-dimensional clean projection used by B. | `go2_env.py:_get_observations` |
| raw observation | Named dictionary used for command reward inference. | `go2_env.py:user_return_dict` |
| regularization critic | Critic trained on behavior regularization reward. | `FBAgent.update_critic` |
| inverse-density sampling | Sampling rare achieved behaviors more often for exploration. | `density_estimator/agent_normalizing_flow.py` |
| replay-buffer sample | Saved observations used for play-time reward inference. | `models/replay_buffer_step_<step>.pt` |
| ABS task | Absolute joint-position Go2 task. | `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0` |
| INC task | Incremental action variant. | `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-INC-v0` |
| KAIST task | Absolute variant with phase/barrier logic. | `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-KAIST-v0` |
