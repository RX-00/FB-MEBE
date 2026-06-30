# Modernization Notes

## Deprecated Or Stale Infrastructure Found

- The repo is based on Isaac Lab, not IsaacGym, so no simulator migration is
  needed for the main Go2 path.
- Some inherited Isaac Lab helper paths are stale, including `isaaclab.sh --test`,
  `isaaclab.sh --docs`, and Docker-related scripts.
- `bash/euler/` and `bash/tars_case/` contain cluster notes that reference
  removed Docker tooling.
- `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` contains a
  hard-coded absolute offline-data path.
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` registers a stale
  task ID, `Isaac-Flat-Unitree-Go2-FB-v0`.

## Modern Replacements Used

The tutorial keeps the current Isaac Lab Go2 task but replaces the teaching
surface:

- Explicit minimal config instead of a large Hydra stack.
- TensorBoard/local logs instead of W&B as a required dependency.
- A small adapter over the env instead of broad RSL-RL compatibility wrappers.
- A typed replay buffer instead of arbitrary nested dictionaries.
- A simple inverse-density sampler for pedagogy, with the normalizing flow
  documented as the original implementation choice.

## Semantics That Must Remain Unchanged

- Go2 action scale and joint-position action semantics.
- 200 Hz sim, 50 Hz control.
- Observation groups and dimensions.
- FB factorization and reward inference.
- Online replay collection.
- MEBE preference for rare achieved behaviors.
- Evaluation by inferred reward embedding, not task-specific retraining.

## Known Unresolved Migration Questions

- Whether the paper's task-specific locomotion/orientation reward definitions
  exactly match the code's `RewardFunction.inference` multiplication of all
  terms.
- Whether hardware `play_xbox.py` has out-of-repo assumptions.
- Whether the stale Go2 registration should be removed or repaired.
- Whether the `cfg.observation_space` naming should be changed to avoid
  overloading Isaac Lab policy observation semantics.
