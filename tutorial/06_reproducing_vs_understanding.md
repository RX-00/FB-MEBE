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

## What Is Not Claimed

- These docs do not claim paper benchmark curves without a full GPU
  training/evaluation run.
- These docs do not fully document hardware deployment.
- These docs do not replace the checked-in FB-MEBE implementation with a
  separate simplified code path.

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

Start by reading the real implementation in this order:

- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py`
- `scripts/reinforcement_learning/fb_mod/pretrain.py`
- `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py`
- `scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py`
- `scripts/reinforcement_learning/fb_mod/density_estimator/`
- `scripts/reinforcement_learning/fb_mod/play.py`
- `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py`
