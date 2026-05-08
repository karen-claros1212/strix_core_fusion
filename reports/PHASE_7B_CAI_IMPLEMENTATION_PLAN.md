# PHASE 7B — CAI PATTERN IMPLEMENTATION PLAN

## Executive Summary
This is a clean-room implementation plan only. No CAI source code is copied, no CAI runtime is created, and STRIX/Saga Fusion controls remain authoritative.

## Target Module Grouping
- `saga_fusion/policy/`: dangerous action handling and HITL policy adapters.
- `saga_fusion/tool_routing/`: controlled routing metadata under SandboxController.
- `saga_fusion/prompt_security/`: prompt injection and prompt safety layer.
- `saga_fusion/reporting/`: evidence-linked reports and redacted traces.
- `saga_fusion/task_planning/`: deterministic pattern registry and mission steps.
- `saga_fusion/memory/`: bounded redacted memory/context patterns.
- `extensions/cai_patterns/`: documentation-only future pattern taxonomy.

## 7C — Prompt Security Layer
- Objective: prompt-injection defense + prompt safety layer
- Primary target module: `saga_fusion/prompt_security/`
- Files to create:
  - `saga_fusion/prompt_security/__init__.py`
  - `saga_fusion/prompt_security/prompt_guard.py`
  - `saga_fusion/prompt_security/injection_signatures.py`
  - `tests/prompt_security/test_prompt_guard.py`
- Files to touch:
  - `saga_fusion/llm/prompt_builder.py`
  - `saga_fusion/telegram/mission_operator.py`
- Required tests:
  - Targeted tests for `saga_fusion/prompt_security/`
  - Full suite before commit
- Risks:
  - Do not copy CAI prompts; do not call LLM real in tests.
- Acceptance criteria:
  - Prompt injection patterns block or downgrade unsafe prompts before LLM/tool routing; benign prompts still pass.
- Must NOT do:
  - Do not copy CAI prompts; do not call LLM real in tests.

## 7D — Tool Routing Enhancement
- Objective: route tool intents under SandboxController and MissionPolicy
- Primary target module: `saga_fusion/tool_routing/`
- Files to create:
  - `saga_fusion/tool_routing/__init__.py`
  - `saga_fusion/tool_routing/router.py`
  - `saga_fusion/tool_routing/tool_contracts.py`
  - `tests/tool_routing/test_router.py`
- Files to touch:
  - `saga_fusion/telegram/mission_operator.py`
- Required tests:
  - Targeted tests for `saga_fusion/tool_routing/`
  - Full suite before commit
- Risks:
  - Do not add direct shell/terminal/browser execution.
- Acceptance criteria:
  - Every routed tool intent carries risk, sandbox mode, evidence id, and denial reason if blocked.
- Must NOT do:
  - Do not add direct shell/terminal/browser execution.

## 7E — Dangerous Action Handling
- Objective: harden R4/R5 dangerous action classifiers
- Primary target module: `saga_fusion/policy/`
- Files to create:
  - `saga_fusion/policy/dangerous_action_classifier.py`
  - `tests/policy/test_dangerous_action_classifier.py`
- Files to touch:
  - `saga_fusion/telegram/mission_policy.py`
  - `saga_fusion/llm/action_normalizer.py`
- Required tests:
  - Targeted tests for `saga_fusion/policy/`
  - Full suite before commit
- Risks:
  - Do not weaken R5; do not approve R4 automatically.
- Acceptance criteria:
  - Known destructive/infra-changing actions classify deterministically in ES/EN; highest-risk wins.
- Must NOT do:
  - Do not weaken R5; do not approve R4 automatically.

## 7F — HITL Approval Gate Improvements
- Objective: improve human-in-the-loop approval metadata and expiry semantics
- Primary target module: `saga_fusion/policy/`
- Files to create:
  - `saga_fusion/policy/hitl_gate.py`
  - `tests/policy/test_hitl_gate.py`
- Files to touch:
  - `saga_fusion/telegram/approval_workflow.py`
- Required tests:
  - Targeted tests for `saga_fusion/policy/`
  - Full suite before commit
- Risks:
  - Do not create parallel approval runtime.
- Acceptance criteria:
  - Approval contains actor, action_hash, expiry, evidence link, and cannot be replayed.
- Must NOT do:
  - Do not create parallel approval runtime.

## 7G — Reporting Improvements
- Objective: report generation improvements with evidence links and redaction
- Primary target module: `saga_fusion/reporting/`
- Files to create:
  - `saga_fusion/reporting/__init__.py`
  - `saga_fusion/reporting/report_engine.py`
  - `saga_fusion/reporting/templates.py`
  - `tests/reporting/test_report_engine.py`
- Files to touch:
  - `saga_fusion/repo_audit/report_engine.py`
- Required tests:
  - Targeted tests for `saga_fusion/reporting/`
  - Full suite before commit
- Risks:
  - Do not delete historical reports.
- Acceptance criteria:
  - Technical/executive reports render from evidence without leaking secrets.
- Must NOT do:
  - Do not delete historical reports.

## 7H — Task Planner / Pattern Registry
- Objective: clean-room pattern registry for deterministic mission steps
- Primary target module: `saga_fusion/task_planning/`
- Files to create:
  - `saga_fusion/task_planning/__init__.py`
  - `saga_fusion/task_planning/pattern_registry.py`
  - `saga_fusion/task_planning/mission_steps.py`
  - `tests/task_planning/test_pattern_registry.py`
- Files to touch:
  - `saga_fusion/llm/brain_service.py`
  - `saga_fusion/llm/llm_router.py`
- Required tests:
  - Targeted tests for `saga_fusion/task_planning/`
  - Full suite before commit
- Risks:
  - Do not implement autonomous external exploitation workflows.
- Acceptance criteria:
  - Mission plans remain declarative/dry-run until policy+sandbox approval.
- Must NOT do:
  - Do not implement autonomous external exploitation workflows.

## 7I — Defensive Workflow Templates
- Objective: defensive templates for repo audit, config review, DFIR planning
- Primary target module: `extensions/cai_patterns/defensive_workflows/`
- Files to create:
  - `extensions/cai_patterns/defensive_workflows/README.md`
  - `docs/DEFENSIVE_WORKFLOW_TEMPLATES.md`
- Files to touch:
  - None expected
- Required tests:
  - Targeted tests for `extensions/cai_patterns/defensive_workflows/`
  - Full suite before commit
- Risks:
  - Do not add malware payload generation or offensive playbooks.
- Acceptance criteria:
  - Templates describe safe defensive workflows and required evidence/tests.
- Must NOT do:
  - Do not add malware payload generation or offensive playbooks.

## 7J — Memory / Context Patterns
- Objective: bounded mission memory and context compaction patterns
- Primary target module: `saga_fusion/memory/`
- Files to create:
  - `saga_fusion/memory/__init__.py`
  - `saga_fusion/memory/mission_memory.py`
  - `saga_fusion/memory/context_budget.py`
  - `tests/memory/test_mission_memory.py`
- Files to touch:
  - `saga_fusion/llm/brain_service.py`
- Required tests:
  - Targeted tests for `saga_fusion/memory/`
  - Full suite before commit
- Risks:
  - Do not persist secrets or unbounded conversation history.
- Acceptance criteria:
  - Memory stores redacted summaries and evidence refs, not secrets/raw tokens.
- Must NOT do:
  - Do not persist secrets or unbounded conversation history.

