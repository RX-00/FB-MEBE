# Evaluation And Debugging

This is the skill-standard summary. The detailed files are:

- `07_evaluation_and_play.md`
- `08_debugging_and_validation.md`

## Evaluation Mechanism

FB-MEBE evaluation does not train a new policy. It:

1. Samples a command.
2. Computes command reward over replay-buffer raw observations.
3. Projects rewards through B to infer `z_r`.
4. Runs the actor with `z_r`.
5. Measures rollout return and regularization metrics.

Original code:

- `scripts/reinforcement_learning/fb_mod/play.py:161`
- `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py:70`
- `scripts/reinforcement_learning/toolbox/functions_reward.py:126`

Minimal code:

- `tutorial/min_implementation/scripts/play.py`
- `tutorial/min_implementation/fbmebe_min/rewards.py`

## Debug First

Check these before long training:

- CUDA visible through PyTorch and `nvidia-smi`.
- Isaac Sim can start.
- Go2 USD asset is available locally or remotely.
- Task ID is registered.
- Observation shapes match expected dimensions.
- Replay buffer has valid transitions, not reset-crossing transitions.
- Checkpoint and replay sample step numbers match.

## Local Status

In this workspace, non-simulator tests pass when called directly. Full Go2
training cannot be validated here because CUDA is unavailable and the Go2 USD
asset cannot be resolved during Isaac Lab environment creation.
