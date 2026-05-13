# Phase 10D — Defensive Report Packs Design (10D-1)

## Scope
Phase 10D-1 is inspection, design, and golden characterization only. No runtime `DefensiveReportPack` generator was implemented.

## Current Building Blocks
- `saga_fusion/defensive_workflows/defensive_workflow_types.py` defines `DefensiveWorkflowPlan` and `DefensiveWorkflowReport` with enforced `execution_allowed=False`, `evidence_required=True`, `report_required=True`, and `non_authoritative=True`.
- `saga_fusion/defensive_workflows/defensive_workflow_reporter.py` already renders redacted executive, technical, and Telegram summaries for workflow plans.
- `saga_fusion/reporting/` provides reusable redaction, evidence loading, report building, and Telegram-safe formatting.
- `saga_fusion/manifests/` provides reference/hash/provenance metadata for evidence and reports without embedding artifact bodies.
- `saga_fusion/telegram/defensive_command_router.py` and `lab_mode.py` already wrap defensive workflows in lab/report-only responses.

## Minimal Future `DefensiveReportPack` Structure
A future report pack should be an aggregation layer over the existing workflow, reporting, and manifest components rather than a duplicate report engine.

Recommended fields:

```text
DefensiveReportPack
- pack_id
- workflow_category
- workflow_id
- report_id
- source_phase = "10D"
- created_at
- safety_contract
  - execution_allowed = false
  - executed = false
  - non_authoritative = true
  - evidence_required = true
  - report_required = true
  - real_telegram_used = false
  - real_tool_execution = false
- plan_summary_ref
  - classification summary
  - MITRE ids
  - indicator count/types only
  - recommendation count
- report_sections
  - executive_summary (redacted)
  - technical_report_ref or redacted technical summary
  - telegram_summary (redacted and bounded)
- evidence_refs[]
  - artifact_id
  - path or external ref
  - sha256
  - size_bytes
  - classification/risk
  - redaction_status
  - secret_scan_status
- report_refs[]
  - artifact_id
  - path/ref
  - sha256
  - evidence_refs[]
- metadata
  - schema_version = "defensive_report_pack_v1"
  - workflow source command/request id if available
```

## Evidence and Redaction Rules
- Evidence must be referenced by metadata, SHA-256 hash, path/ref, and provenance only.
- Raw artifact bodies, attachment contents, malware/sample bytes, ransom-note bodies, webshell content, credentials, tokens, and secrets must never be embedded in the pack.
- Pack metadata must reuse `ReportRedactor`/`ManifestRedactor`; sensitive artifacts require `redaction_status` and `secret_scan_status`.
- Manifest validation remains authoritative for raw metadata keys and hash/ref integrity.

## Workflow Coverage Target
Future pack generation should cover:
- `malware_triage`
- `ransomware_response`
- `phishing_attachment` / Telegram `/phishing_review`
- `webshell_investigation`
- `credential_theft` / Telegram `/credential_theft_review`
- `suspicious_process` / Telegram `/suspicious_process_review`
- `defense_status` as a control-surface/status pack or safe status summary

## Non-Duplication Decision
Do not create a parallel report builder. Future 10D-2 implementation should call:
1. `DefensiveWorkflowRegistry` to obtain a `DefensiveWorkflowPlan`.
2. `DefensiveWorkflowReporter` for existing redacted report summaries.
3. `ManifestBuilder`/`EvidenceReporter` for evidence/report refs and safe summaries.
4. `TelegramReportFormatter` or existing `telegram_summary` for Telegram-safe bounded output.

## Golden Tests Added in 10D-1
`tests/defensive_workflows/test_defensive_report_pack_golden.py` characterizes current outputs as pack-ready inputs:
- Stable plan/report fields exist for all six defensive workflows.
- Safety invariants remain enforced: `execution_allowed=False`, `executed=False`, `evidence_required=True`, `report_required=True`, `non_authoritative=True`.
- Workflow outputs do not expose dummy token/password values after redaction.
- Telegram lab-mode responses are safe pack inputs and remain bounded/redacted.
- `defense_status` remains lab-only and exposes workflow availability without execution.

## Phase 10D-2 GO Criteria
Proceed to runtime pack implementation only if it remains a thin aggregation layer over existing components and adds tests for:
- Report pack schema construction per workflow.
- Manifest-backed evidence/report references.
- Secret/raw-body blocking.
- Telegram-safe pack summary.
- Full suite green.

## Explicit Non-Goals
- No real Telegram calls.
- No malware/sample execution or download.
- No payload or webshell generation.
- No attachment execution or processing.
- No destructive commands.
- No external network execution.
- No secrets, tokens, or `.env`/config changes.
