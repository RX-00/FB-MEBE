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

## Documentation Scope

The tutorial documents the current Isaac Lab Go2 FB-MEBE path directly. It does
not introduce or maintain a separate simplified implementation.

The main teaching surface is:

- `scripts/reinforcement_learning/fb_mod/pretrain.py`
- `scripts/reinforcement_learning/fb_mod/agent_meta/fb/`
- `scripts/reinforcement_learning/fb_mod/density_estimator/`
- `scripts/reinforcement_learning/fb_mod/play.py`
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/`

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
