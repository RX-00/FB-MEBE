# Deviations From Original Implementation

| Area | Original | Tutorial/minimal implementation | Why | Risk | Validation |
|---|---|---|---|---|---|
| Runnable tutorial slice | Skill normally asks for `tutorial/tutorial_impl/` | User requested Markdown first and `tutorial/min_implementation/` | Repo is large; user explicitly changed scope | Different from skill default layout | Documented here and in README |
| Config system | Hydra config stack under `scripts/reinforcement_learning/fb_mod/configs/` | Plain YAML plus CLI overrides | Easier to teach and test | Some original defaults may be missed | Config tests and explicit docs |
| Logging | W&B optional/offline | TensorBoard/local metrics | Fewer external services | Metrics names differ | Check event files or local logs |
| Replay schema | Nested `DictBuffer` | Explicit typed fields | Easier shape checks | Less flexible for new obs keys | Unit tests for insertion/sample |
| Density model | RealNVP normalizing flow | Simple inverse-density sampler by default | Keeps MEBE concept minimal | May underperform full flow | Density sampler tests; long-run eval needed |
| Network ensembles | Original forward and critic can use parallel networks | Minimal first version uses simpler networks | Reduces code size | Less pessimism/uncertainty handling | Full training needed to judge performance |
| Regularization critic | Enabled in Go2 config | Optional in minimal code | Keeps first path readable | Policy may foot-drag if disabled | Full Go2 eval and foot-slide metrics |
| W&B videos | Original video wrappers | Optional simple video path | Avoids wrapper complexity | Video output names differ | Isaac Lab smoke play |
| Full Go2 validation | Original workspace has generated 150k run | Local workspace lacks visible CUDA and cannot resolve the Go2 USD asset during smoke train | Cannot fake simulator availability or asset access | Full-policy success not locally proven | Must run on Isaac Lab GPU machine with Go2 asset access |
