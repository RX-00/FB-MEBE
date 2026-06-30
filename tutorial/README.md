# FB-MEBE Tutorial

This tutorial explains how FB-MEBE works in this repository, from training to
playback, with references to the actual code.

It has two parts:

1. The repository tutorial explains the checked-in implementation under
   `scripts/reinforcement_learning/fb_mod/` and
   `source/isaaclab_tasks/isaaclab_tasks/direct/go2/`.
2. The minimal implementation under `tutorial/min_implementation/` is a cleaner
   Isaac Lab implementation intended for learning and modification.

## Read Order

Read these files in order:

- `00_big_picture.md`: the goal, mechanism, and runtime pipeline.
- `01_paper_to_original_code_map.md`: paper concepts mapped to concrete code.
- `02_original_to_modern_stack_map.md`: current repo pieces mapped to the clean
  tutorial implementation.
- `03_minimal_modern_implementation.md`: the runnable minimal implementation at
  a glance.
- `04_system_components.md`: component-by-component map across paper, original
  code, and minimal code.
- `05_evaluation_and_debugging.md`: skill-standard evaluation/debugging summary.
- `06_reproducing_vs_understanding.md`: what the tutorial reproduces versus what
  still requires a paper-scale run.
- `03_training_pipeline.md`: what happens during training.
- `04_environment_and_task.md`: Go2 observations, actions, rewards, resets, and
  randomization.
- `05_models_losses_and_objectives.md`: FB networks, actor objective, density
  exploration, reward inference, and checkpoint format.
- `06_configs_and_experiments.md`: Hydra configs, run directories, artifacts,
  and useful overrides.
- `07_evaluation_and_play.md`: saved-policy loading, zero-shot reward
  inference, video eval, and Xbox play.
- `08_debugging_and_validation.md`: checks and common failure modes.
- `09_implementation.md`: how to implement a minimal FB-MEBE Go2 trainer from a
  blank Isaac Lab repo.

Reference files:

- `modernization_notes.md`
- `deviations_from_original.md`
- `migration_log.md`
- `glossary.md`

## Main Repo Commands

Train the checked-in FB-MEBE implementation:

```bash
python scripts/reinforcement_learning/fb_mod/pretrain.py \
    --config-name=Isaaclab_pretrain_config_go2 \
    wandb.use_wandb=False
```

Play a saved checkpoint:

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir "exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46" \
    --model-step 150000 \
    --replay-buffer-step 150000
```

## Minimal Implementation Commands

The minimal implementation is in `tutorial/min_implementation/`.

Run its non-simulator tests:

```bash
python -m pytest tutorial/min_implementation/tests
```

Run a small Isaac Lab smoke train:

```bash
python -m tutorial.min_implementation.scripts.train \
    --config tutorial/min_implementation/configs/go2_fb.yaml \
    --num-envs 64 \
    --steps 1000 \
    --no-video
```

Run full Go2 training on an Isaac Lab machine with a working GPU:

```bash
python -m tutorial.min_implementation.scripts.train \
    --config tutorial/min_implementation/configs/go2_fb.yaml
```

Play the latest minimal checkpoint:

```bash
python -m tutorial.min_implementation.scripts.play \
    --run-dir tutorial/min_implementation/runs/latest
```

## Current Local Validation Limit

This workspace cannot currently prove full Go2 training. `torch.cuda.is_available()`
is false, `nvidia-smi` cannot communicate with a driver, Isaac Sim reports no
CUDA-capable device, and the smoke train cannot resolve the Go2 USD asset from
the configured Omniverse/S3 URL. The non-simulator parts of the minimal
implementation are tested locally.
