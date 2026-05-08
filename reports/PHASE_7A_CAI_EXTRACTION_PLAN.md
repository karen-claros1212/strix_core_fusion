# PHASE 7A — CAI EXTRACTION PLAN

## Scope
This phase is audit-only. STRIX will not copy CAI source, will not create a CAI runtime, and will not enable external offensive workflows.

## Strategy Counts
- ADAPT_PATTERN: 8
- REIMPLEMENT_CLEAN: 5
- DOCUMENT_ONLY: 3
- DISCARD: 0
- FUTURE_RESEARCH: 2

## Extraction Decisions
### guardrails
- Decision: ADAPT_PATTERN
- Source path: `docs/guardrails.md; src/cai/sdk/agents/guardrail.py; src/cai/agents/guardrails.py`
- STRIX strategy: Strengthen STRIX PromptGuard + MissionPolicy preflight around Telegram/LLM messages.
- Risk: Medium: do not import CAI runtime; reimplement policy adapters in Saga Fusion.
- Target phase: 7B

### tool routing
- Decision: REIMPLEMENT_CLEAN
- Source path: `examples/agent_patterns/routing.py; src/cai/sdk/agents/tool.py; src/cai/tools/*`
- STRIX strategy: Improve STRIX tool dispatch taxonomy without bypassing SandboxController.
- Risk: High: tool routing can become fail-open if not gated.
- Target phase: 7B

### permission model
- Decision: ADAPT_PATTERN
- Source path: `docs/ref/tool.md; src/cai/tools/reconnaissance/generic_linux_command.py; tests/tools/test_generic_linux_command_guardrails.py`
- STRIX strategy: Map CAI command restrictions into STRIX R0-R5 + SandboxPolicy.
- Risk: High: command execution must stay dry-run/gated.
- Target phase: 7B

### sandbox/policy
- Decision: DOCUMENT_ONLY
- Source path: `src/cai/sdk/agents/parallel_isolation.py; src/cai/agents/meta/local_python_executor.py`
- STRIX strategy: Compare against STRIX SandboxController/ProcessGuard for non-looping bounded execution.
- Risk: Medium: do not replace existing sandbox.
- Target phase: 7C

### offensive workflow
- Decision: ADAPT_PATTERN
- Source path: `src/cai/agents/patterns/offsec.py; src/cai/agents/red_teamer.py; src/cai/prompts/system_red_team_agent.md`
- STRIX strategy: Use only for authorized lab-mode mission templates and risk classification.
- Risk: High: must not enable external pentest automation yet.
- Target phase: 7C

### defensive workflow
- Decision: REIMPLEMENT_CLEAN
- Source path: `src/cai/agents/blue_teamer.py; src/cai/prompts/system_blue_team_agent.md`
- STRIX strategy: Useful for STRIX repository, config, detection, and incident-response planning.
- Risk: Low: defensive analysis aligns with current safe mode.
- Target phase: 7B

### bug bounty workflow
- Decision: ADAPT_PATTERN
- Source path: `src/cai/agents/bug_bounter.py; src/cai/agents/patterns/bb_triage.py; src/cai/prompts/system_bug_bounter.md`
- STRIX strategy: Create STRIX lab-only finding triage/report workflows before external scope.
- Risk: High: requires explicit authorized target/scope gates.
- Target phase: 7C

### recon workflow
- Decision: FUTURE_RESEARCH
- Source path: `src/cai/tools/reconnaissance/*; src/cai/tools/web/*; src/cai/prompts/system_web_pentester.md`
- STRIX strategy: Pattern for future scoped recon modules, initially repo/internal only.
- Risk: High: external recon remains blocked.
- Target phase: 8+

### exploit validation workflow
- Decision: DOCUMENT_ONLY
- Source path: `src/cai/agents/retester.py; src/cai/prompts/system_exploit_expert.md`
- STRIX strategy: Convert into STRIX validation-plan generation without executing PoCs.
- Risk: High: PoC execution must remain blocked until lab authorization.
- Target phase: 8+

### report generation
- Decision: REIMPLEMENT_CLEAN
- Source path: `src/cai/agents/reporter.py; src/cai/prompts/system_reporting_agent.md`
- STRIX strategy: Upgrade STRIX ReportEngine for executive/technical/evidence-linked reports.
- Risk: Low: reporting is safe if redaction preserved.
- Target phase: 7B

### memory/context handling
- Decision: ADAPT_PATTERN
- Source path: `src/cai/agents/memory.py; docs/context.md; src/cai/repl/commands/compact.py`
- STRIX strategy: Improve STRIX mission memory/evidence summarization with OutputBudget.
- Risk: Medium: avoid memory loops and secret retention.
- Target phase: 7C

### approval gates / HITL
- Decision: ADAPT_PATTERN
- Source path: `README architecture HITL section; docs/ref/guardrail.md; docs/running_agents.md`
- STRIX strategy: Map to existing ApprovalWorkflow; do not add parallel approval runtime.
- Risk: Medium: duplicate gates can conflict if not unified.
- Target phase: 7B

### dangerous action handling
- Decision: REIMPLEMENT_CLEAN
- Source path: `docs/guardrails.md; tests/tools/test_generic_linux_command_guardrails.py`
- STRIX strategy: Expand STRIX R4/R5 regression matrix for command-like intents.
- Risk: High: must never fail-open.
- Target phase: 7B

### browser/terminal tools
- Decision: FUTURE_RESEARCH
- Source path: `src/cai/repl/commands/shell.py; docs/tui/terminals_management.md; src/cai/tools/web/*`
- STRIX strategy: Future controlled tool wrappers under SandboxController only.
- Risk: High: tool execution risk.
- Target phase: 8+

### malware/forensics knowledge
- Decision: DOCUMENT_ONLY
- Source path: `src/cai/agents/dfir.py; src/cai/agents/reverse_engineering_agent.py; src/cai/prompts/system_dfIR_agent.md; src/cai/prompts/reverse_engineering_agent.md`
- STRIX strategy: Feed future STRIX malware_knowledge/detection engineering docs, no payload generation.
- Risk: High: dual-use; keep analysis/detection only.
- Target phase: 10

### prompt patterns
- Decision: ADAPT_PATTERN
- Source path: `src/cai/prompts/*; examples/cai/prompt_injections/*`
- STRIX strategy: Extract prompt hardening lessons for STRIX PromptBuilder/LLMRouter.
- Risk: Medium: never copy prompts directly; avoid prompt-injection seeds as instructions.
- Target phase: 7B

### task planner / patterns
- Decision: REIMPLEMENT_CLEAN
- Source path: `src/cai/agents/patterns/pattern.py; examples/agent_patterns/*; docs/multi_agent.md`
- STRIX strategy: Design STRIX pattern registry that keeps MissionPolicy/Sandbox as single gate.
- Risk: Medium: avoid creating CAI runtime parallel to Saga Fusion.
- Target phase: 7B

### tracing/logging
- Decision: ADAPT_PATTERN
- Source path: `src/cai/sdk/agents/tracing/*; src/cai/sdk/agents/logger.py`
- STRIX strategy: Compare with EvidenceLogger; adapt evidence/span ideas if redacted.
- Risk: Low/Medium: logs can leak secrets if copied blindly.
- Target phase: 7C

## 7B Recommendation
Start with non-runtime design plan for: guardrails, tool routing, dangerous action handling, prompt hardening, report generation, and task-pattern registry. All implementations must keep MissionPolicy, ApprovalWorkflow, SandboxController, EvidenceLogger, OutputBudget, and SecretRedactor as the authoritative STRIX controls.
