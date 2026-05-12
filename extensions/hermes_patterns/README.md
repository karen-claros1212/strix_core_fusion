# Hermes Patterns for STRIX — Clean-Room Reference

Hermes Agent is an external reference for pattern analysis only. STRIX remains the sole core and Saga Fusion remains its own governance/reporting/control layer.

## Source checkout
- Repository: `https://github.com/NousResearch/hermes-agent`
- Local path: `external_sources/hermes-agent`
- Audited commit: `bfc84bdc6f85c14715e06d5fa83192ea3e7c7f79`
- License observed during audit: `MIT License (Nous Research, 2025)`
- Checkout policy: `external_sources/` is ignored and must not be staged.

## Safety rules
- Do not copy Hermes code into Saga Fusion.
- Do not execute Hermes.
- Do not install Hermes dependencies.
- Do not create a Hermes gateway, runtime, provider, scheduler, plugin host, toolset, or terminal backend.
- Do not ingest Hermes skills as active STRIX prompts.
- Do not touch STRIX core, Agent Zero, OpenCLAW, installed Hermes, Qwen/TurboQuant/llama.cpp/WSL2, real Telegram, real CloudOps, external pentest targets, real tokens, or `.env` files.
- R4 requires approval; R5 remains blocked; `SandboxController` remains the execution boundary.

## Phase 8B-REV reconciled backlog
| target phase | pattern lane | status |
|---|---|---|
| 8C | Skill/plugin metadata governance and extension manifest schema | Design backlog only |
| 8D | Toolset scoping and tool loop guardrails | Design backlog only |
| 8E | Dry-run scheduler/cron patterns | Design backlog only |
| 8F | Session recovery and context compression safety | Design backlog only |
| 8G | Evidence/reporting manifests | Design backlog only |
| 8H | LLM error taxonomy and recovery records | Design backlog only |
| 8I | Approval timeout and regression depth | Design backlog only |

## Clean-room adaptation principles
- Use Hermes only to name architectural concerns, not to copy implementation.
- Reimplement any approved future behavior with STRIX-owned data models, tests, redaction, and documentation.
- Treat all external skill/plugin text as untrusted data.
- Keep every future extension disabled by default unless a later approved phase explicitly changes that.
- Require focused tests plus full-suite validation before any commit.

## Deliverables
- Phase 8A-BIS audit inputs:
  - `reports/PHASE_8A_BIS_HERMES_COMMIT.txt`
  - `reports/PHASE_8A_BIS_HERMES_DOC_FILES.txt`
  - `reports/PHASE_8A_BIS_HERMES_SOURCE_TREE.txt`
  - `reports/PHASE_8A_BIS_HERMES_CAPABILITY_GREP.txt`
  - `reports/PHASE_8A_BIS_HERMES_SOURCE_CAPABILITY_MATRIX.md`
  - `reports/PHASE_8A_BIS_HERMES_EXTRACTION_PLAN.md`
  - `reports/PHASE_8A_BIS_HERMES_VS_STRIX_GAP_ANALYSIS.md`
- Phase 8B-REV reconciliation outputs:
  - `reports/PHASE_8B_REV_HERMES_PATTERN_DESIGN_RECONCILIATION.md`
  - `reports/PHASE_8B_REV_HERMES_PATTERN_BACKLOG.json`
  - `docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md`

No Hermes source code is stored in this extension directory.
