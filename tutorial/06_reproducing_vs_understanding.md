# Reproducing Vs Understanding

This tutorial is primarily for understanding and implementing FB-MEBE cleanly.
It is not a claim that the full paper has been reproduced in this workspace.

## What Is Preserved

- FB successor-measure factorization.
- B-based reward inference.
- Online replay training.
- Go2 Isaac Lab environment semantics.
- 12-D joint-position action interface.
- 200 Hz simulation and 50 Hz control.
- MEBE rare-behavior exploration idea.

## What Is Simplified

- The minimal implementation uses a plain YAML config instead of Hydra.
- The minimal implementation uses TensorBoard/local logs instead of W&B.
- The minimal implementation uses a histogram inverse-density sampler instead
  of the original normalizing flow.
- The minimal implementation does not reproduce hardware deployment.
- The minimal implementation does not claim paper benchmark curves without a
  full GPU training/evaluation run.

## To Reproduce The Main Repo

Use the original training path:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    wandb.use_wandb=False
```

Then evaluate with:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir <run-dir> \
    --model-step latest \
    --replay-buffer-step latest
```

## To Understand And Modify The Method

Use the minimal implementation:

```bash
python -m tutorial.min_implementation.scripts.train \
    --config tutorial/min_implementation/configs/go2_fb.yaml \
    --num-envs 64 \
    --steps 1000 \
    --no-video
```

Start by reading:

- `tutorial/min_implementation/fbmebe_min/agent.py`
- `tutorial/min_implementation/fbmebe_min/replay.py`
- `tutorial/min_implementation/fbmebe_min/density.py`
- `tutorial/min_implementation/fbmebe_min/rewards.py`
