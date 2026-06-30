# Migration Log

| Date | Component | Change | Rationale | Verification |
|---|---|---|---|---|
| 2026-06-27 | Tutorial docs | Added audit-backed Markdown tutorial files | Teach FB-MEBE from paper to code to play | Source inspection; Markdown paths cite repo files |
| 2026-06-27 | Minimal implementation | Added clean implementation target under `tutorial/min_implementation/` | Provide a fresh-repo implementation guide and runnable code path | Non-simulator tests locally; Isaac Lab full train blocked by local runtime |
| 2026-06-27 | Validation notes | Documented missing local CUDA/asset runtime | Avoid claiming full Go2 training succeeded when it cannot run here | `torch.cuda.is_available() == False`; smoke train reports no CUDA-capable device and missing Go2 USD asset |
