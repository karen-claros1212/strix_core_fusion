# Hermes Patterns for STRIX — Phase 8A-BIS Read-Only Source Audit

Phase 8A-BIS cloned the official Hermes Agent repository only as a read-only external source for clean-room pattern analysis.

## Source checkout
- Repository: `https://github.com/NousResearch/hermes-agent`
- Local path: `external_sources/hermes-agent`
- Audited commit: `bfc84bdc6f85c14715e06d5fa83192ea3e7c7f79`
- License observed: `MIT License (Nous Research, 2025)`
- Checkout policy: `external_sources/` is ignored and must not be staged.

## Safety rules
- Do not copy Hermes code into Saga Fusion.
- Do not execute Hermes.
- Do not install Hermes dependencies.
- Do not create a Hermes gateway, runtime, provider, scheduler, plugin host, or terminal backend.
- Do not touch STRIX core, Agent Zero, OpenCLAW, installed Hermes, Qwen/TurboQuant/llama.cpp/WSL2, or real tokens/`.env` files.

## Clean-room pattern candidates
- Skill/workflow metadata and allowlisted indexes.
- Plugin/extension manifest governance, disabled by default.
- Cron/scheduled audit policy as dry-run specs first.
- Memory provider fencing and streaming context scrubber tests.
- Context compression summaries that are explicitly non-authoritative.
- Tool loop/no-progress guardrails and mutating/idempotent taxonomy.
- Approval timeout-to-deny and channel-specific audit events.
- Evidence/report manifest schemas with provenance and redaction status.
- Session recovery and restart-drain patterns for Telegram continuity.

## Deliverables
- `reports/PHASE_8A_BIS_HERMES_COMMIT.txt`
- `reports/PHASE_8A_BIS_HERMES_DOC_FILES.txt`
- `reports/PHASE_8A_BIS_HERMES_SOURCE_TREE.txt`
- `reports/PHASE_8A_BIS_HERMES_CAPABILITY_GREP.txt`
- `reports/PHASE_8A_BIS_HERMES_SOURCE_CAPABILITY_MATRIX.md`
- `reports/PHASE_8A_BIS_HERMES_EXTRACTION_PLAN.md`
- `reports/PHASE_8A_BIS_HERMES_VS_STRIX_GAP_ANALYSIS.md`

No Hermes source code is stored in this extension directory.
