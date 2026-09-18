# FB-MEBE Development Notes

This document is for maintainers and future coding agents changing this repository.

## Ground Rules For Changes

- Preserve existing checkpoints, replay artifacts, resolved configs, logs, and videos unless their deletion or replacement is explicitly authorized. Use a separate run directory for diagnostics; being ignored by Git does not make an artifact disposable.
- Keep FB training changes grounded in the existing flow: Hydra config, Isaac Lab task config, `FB_VecEnvWrapper`, `DictBuffer`, FB agent, checkpoint loader.
- Prefer adding config fields over hard-coded local paths when changing run-time behavior.
- Do not weaken validation by skipping assertions or swallowing errors unless the user explicitly asks for a temporary diagnostic patch.

## Environment

Use the separate `fb-mebe` environment, with editable packages bound to this
checkout. See [environment setup](usage.md#environment-setup) for installation
and package-location checks.

```bash
conda activate fb-mebe
```

Additional setup information is split across:

| File | What it verifies |
| --- | --- |
| `README.md` | Current project install sequence and Torch workaround. |
| `source/isaaclab/setup.py` | `isaaclab` package dependencies and Python `>=3.10`. |
| `source/isaaclab_tasks/setup.py` | `isaaclab_tasks` dependencies. |
| `source/isaaclab_rl/setup.py` | RL dependencies and extras such as `rsl-rl`. |

## Formatting And Linting

The repo uses pre-commit hooks configured in `.pre-commit-config.yaml`.

`isaaclab.sh` is inherited from upstream Isaac Lab. It is still useful for some package-management and simulator commands, but it also contains upstream options that reference files removed from this FB-MEBE checkout.

```bash
./isaaclab.sh --format
```

Equivalent direct command:

```bash
pre-commit run --all-files
```

Configured hooks include Black, Flake8, isort, pyupgrade, codespell, license insertion, and RST checks. `.flake8` sets max line length to `120`, max complexity to `30`, and ignores `E402`, `E501`, `W503`, `E203`, `D401`, `R504`, `R505`, `SIM102`, `SIM117`, and `SIM118`.

First-time pre-commit runs may need network access to install hook environments.

## Tests

Most tests launch Isaac Sim and are not lightweight unit tests. Run them from an environment that can import Isaac Sim and access the requested device.

Examples:

```bash
python source/isaaclab_tasks/test/test_environments.py
python source/isaaclab_tasks/test/test_environment_determinism.py
python source/isaaclab_tasks/test/test_record_video.py
python source/isaaclab_assets/test/test_valid_configs.py
python source/isaaclab/test/controllers/test_differential_ik.py
```

`./isaaclab.sh --test` is an upstream Isaac Lab convenience path and currently references missing `tools/run_all_tests.py`. For this fork, run individual test files directly unless the upstream helper is restored.

For an FB-specific change, run the [small Go2 configuration](usage.md#train-fb-on-go2)
and check that learning updates, evaluation, and checkpoint saving complete.
Then test playback with an explicit model/replay selection. A short smoke run
does not establish convergence, long-run density-estimator behavior, or task
performance; interpret evaluation scores using the
[reward limitation](architecture.md#evaluation-reward-limitation).
Headless train/play checks do not validate Xbox interaction, offline
pretraining, or the separate RSL-RL workflows.

## Documentation Checks

This documentation is plain Markdown. There is no checked-in Markdown linter.

Before claiming docs are complete, verify:

```bash
test -f README.md
test -f docs/architecture.md
test -f docs/usage.md
test -f docs/development.md
```

Also check every documented path that was added or changed.

Keep experiment results with their run artifacts. Avoid machine-specific run
inventories, copied configuration tables, and rolling validation counts in
these guides; link to executable sources and describe stable contracts instead.

There is no checked-in docs CI workflow for these Markdown docs.

## Safe Edit Map

| Change type | Primary files |
| --- | --- |
| Add or rename Go2 task IDs | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` |
| Change Go2 base observation/action/reward behavior | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_env.py` |
| Change Go2 randomization or dimensions | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_base.py`, `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_abs/go2_cfg_rnd_full.py`, `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_inc/go2_cfg_rnd_full_incremental.py`, `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_KAIST_abs/go2_cfg_KAIST.py` |
| Change incremental control | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_default_inc/go2_env_incremental.py` |
| Change KAIST gait/barrier variant | `source/isaaclab_tasks/isaaclab_tasks/direct/go2/env_KAIST_abs/go2_env_KAIST.py` |
| Change FB train defaults | `scripts/reinforcement_learning/fb_mod/configs/*.yaml` |
| Change FB network defaults | `scripts/reinforcement_learning/fb_mod/configs/agent/FBAgent.yaml` |
| Change online training loop | `scripts/reinforcement_learning/fb_mod/pretrain.py` |
| Change offline-data collection | `scripts/reinforcement_learning/fb_mod/play_collect.py` |
| Change offline pretraining | `scripts/reinforcement_learning/fb_mod/pretrain_offline.py` |
| Change checkpoint loading/playback | `scripts/reinforcement_learning/fb_mod/play_config.py`, `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py`, `scripts/reinforcement_learning/fb_mod/play.py`, `scripts/reinforcement_learning/fb_mod/play_xbox.py`, `scripts/reinforcement_learning/fb_mod/play_collect.py` |
| Change FB transition storage | `scripts/reinforcement_learning/fb_mod/buffer.py` |
| Change command/reward inference | `scripts/reinforcement_learning/toolbox/config_task.py`, `scripts/reinforcement_learning/toolbox/functions_reward.py` |

## Invariants To Preserve

The training loop, agent updates, reward inference, and playback scripts rely on these contracts:

- `pretrain.py` must launch Isaac Lab before importing modules that require the simulator runtime.
- `hydra_cfg.agent.model.policy_dim`, `obs_dim`, `goal_dim`, `critic_dim`, and `action_dim` are filled from the environment config before constructing the agent.
- `hydra_cfg.train.replay_buffer_capacity` is derived from `env.num_envs * train.replay_buffer_N`.
- `FB_VecEnvWrapper.reset()` and `step()` return transition dictionaries with `obs`, `time`, `done`, `reward_task`, and `reward_reg`.
- Replay-buffer transitions have `observation`, `action`, and nested `next` keys.
- Raw Go2 observations include the names required by `RewardFunction`: `vx`, `vy`, `vz`, `wz`, `gx`, `gy`, `gz`, and `base_height`.
- `FBPolicyLoader` expects `hydra_config.yaml` two directories above the model checkpoint file.
- Saved FB checkpoints contain `actor`, `policy_normalizer`, `B`, and `B_normalizer`.
- `play.py`, `play_xbox.py`, and `play_collect.py` resolve run directories and model steps through `play_config.py`.
- `bash/fb_pretrain.sh` pins `--config-name=Isaaclab_pretrain_config_go2` and does not forward extra CLI arguments; use `pretrain.py` directly for Hydra overrides.
- `FB_VecEnvWrapper.eval_task()` expects a command tensor shaped like `[num_envs, 3]` for `vx`, `vy`, and `wz`.
- In Isaac Lab `DirectRLEnv`, `cfg.observation_space` defines the Gym `single_observation_space["policy"]`. If FB needs a separate forward-map observation dimension, prefer a separate FB-specific config field over overloading `observation_space`.

## Known Technical Debt

These issues are verified from source inspection, not fixed here:

- `pretrain_offline.py` is stale against the current Go2 configs: it uses old `env.video*` keys, has a hard-coded absolute `offline_data_path`, and calls `ConvexHull` without importing it.
- `Isaaclab_fb_play_config_base.yaml` defaults `path`, `model_step`, and `replay_buffer_step` to `latest`; this is convenient locally but can select the wrong run if multiple `exp_*` runs are present.
- `Isaaclab_pretrain_config_base.yaml` uses `Isaac-Flat-Unitree-Go2-Rnd-full-FB-v0`, which does not match the registered Go2 IDs.
- `source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py` registers `Isaac-Flat-Unitree-Go2-FB-v0` to module paths that are not present.
- `isaaclab.sh --test`, `isaaclab.sh --docs`, and `isaaclab.sh --docker` are upstream Isaac Lab paths that reference files or directories not present in this checkout.
- The default ABS Gym policy space declares 34 values while the actor receives 45, and the constructor's Gym-space membership guard skips the intended assertion. See the [environment contract](architecture.md#go2-environment-contract).
- Training-time evaluation logs a reward that does not match the task reward used for inference. This issue also exists in the original implementation (`FB-MEBE_og`); see the [evaluation reward limitation](architecture.md#evaluation-reward-limitation).

## Future FB Reimplementations

For the planned high-level FB controller in `hierarchical_fb`, do not reproduce
the inherited evaluation mismatch as intended behavior. Correct it or explicitly
redesign the reward contract: inference and evaluation should share the intended
task targets and scoring. Test non-upright orientation and height targets, and
keep motion regularization distinct from task success. This is future work,
not a claim that the issue is fixed in FB-MEBE.

## Release Or PR Checklist

Before opening a PR or claiming a change is complete:

1. State which workflow changed: FB train, FB play, Go2 env, RSL-RL, docs, or tests.
2. Run the narrowest relevant validation command that exercises that workflow.
3. Include any failed or skipped validation explicitly.
4. Check `git status --short` for generated outputs under `exp_*`, `logs/`, `wandb/`, and `videos/`.
5. If public behavior, config fields, task IDs, generated artifact names, or commands changed, update `README.md` or `docs/`.
