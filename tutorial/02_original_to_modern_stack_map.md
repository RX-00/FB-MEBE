# Original To Modern Stack Map

The original code in this repository is already based on Isaac Lab, but the FB
implementation is still difficult to teach because training, environment
wrapping, logging, artifact saving, density sampling, and evaluation are tightly
coupled. The modern tutorial keeps the scientific mechanism and Go2 interface
semantics while using a smaller, more explicit code layout.

| Original component | Original stack/API | Modern tutorial equivalent | Preserved semantics | Changed because | Verification |
|---|---|---|---|---|---|
| Training entry point | `scripts/reinforcement_learning/fb_mod/pretrain.py` with global Hydra composition and `WORKSPACE` | `tutorial/min_implementation/scripts/train.py` with explicit config loading and runner class | Online replay collection, FB updates, periodic eval/save | Easier to read and test without global config side effects | Non-sim unit tests plus Isaac Lab smoke train on a GPU machine |
| Go2 task | Registered Isaac Lab direct task `Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0` | Same registered task by default | Go2 asset, timing, action scale, observation groups | Reusing the task avoids silently changing robot semantics | `env.reset()` and observation shape checks |
| Env wrapper | `FB_VecEnvWrapper` | Thin local adapter in `min_implementation` | Transition dict with policy/obs/goal/raw and episode step counts | The original wrapper includes RSL-RL compatibility and video indirection not needed for the tutorial | Interface tests for reset/step output |
| Replay buffer | `DictBuffer` nested storage | Small typed replay buffer | Stores `obs`, `action`, `next_obs`, `done`, `reward_reg`, and `raw` | Simpler schema and direct shape assertions | `test_replay_buffer.py` |
| FB networks | `FBModel`, `nn_models.py` | `min_implementation/fbmebe_min/networks.py` | Forward map, backward map, actor, target networks, sphere-projected `z` | Removes parallel-layer infrastructure unless configured | Network shape tests |
| FB loss | `FBAgent.update_fb` | `min_implementation/fbmebe_min/agent.py` | Diagonal attraction, off-diagonal contrastive penalty, target bootstrapping, orthonormality | Fewer knobs and clearer metric names | Loss smoke test with synthetic batch |
| Actor update | TD3-style actor with optional regularization critic | Same core actor update; regularization critic optional | Maximize `F(s,a,z)^T z`, optionally add regularization Q | Keeps minimal path readable, preserves extension point | Synthetic update test |
| MEBE density sampler | RealNVP normalizing flow over selected goal coordinates | Histogram/KNN-lite inverse-density sampler by default, flow as optional future extension | Prefer rare achieved behaviors and mix with random sphere latents | Flow training is heavy and not required to teach the mechanism | Density sampler unit test |
| Logging | W&B optional/offline, console prints | TensorBoard scalar logs plus local JSON config | Training/eval metrics are still recorded | Reduces external setup | Check event files and metrics JSON |
| Checkpoint | `model_step_<t>.pt` plus `replay_buffer_step_<t>.pt` | Same logical split: `checkpoint_<t>.pt` and `replay_sample_<t>.pt` | Play rebuilds actor/B and uses replay sample for reward inference | Names are clearer in tutorial code | Save/load test |
| Play/eval | `play.py`, `play_config.py`, `FBPolicyLoader` | `min_implementation/scripts/play.py` and loader utilities | Command reward inference and actor rollout with inferred `z_r` | Avoids Hydra run auto-selection for tutorial clarity | Play smoke command on Isaac Lab machine |

## Explicit Non-Goals

- The minimal implementation is not a bitwise reproduction of the original
  training code.
- It does not reproduce W&B behavior.
- It does not reproduce hardware deployment scripts.
- It does not guarantee paper benchmark numbers without long GPU training and
  careful hyperparameter sweeps.
