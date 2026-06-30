# FB-MEBE Tutorial

This tutorial explains how FB-MEBE works in this repository, from training to
playback, with references to the actual code.

It focuses on the checked-in implementation under
`scripts/reinforcement_learning/fb_mod/` and
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/`.

## Read Order

Read these files in order:

- `00_big_picture.md`: the goal, mechanism, and runtime pipeline.
- `01_paper_to_original_code_map.md`: paper concepts mapped to concrete code.
- `02_codebase_map.md`: main repo codebase map for training,
  environment, agent, replay, density, and play components.
- `04_system_components.md`: component-by-component map across paper concepts
  and checked-in code.
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

Reference files:

- `modernization_notes.md`
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

## Current Local Validation Limit

This tutorial does not prove full Go2 training by itself. Before claiming a
successful Go2 run, validate CUDA, Isaac Sim startup, Go2 asset access, task
registration, and at least a short FB training command from
`08_debugging_and_validation.md`.
