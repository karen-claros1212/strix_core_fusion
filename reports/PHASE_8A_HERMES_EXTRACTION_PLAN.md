# PHASE 8A — HERMES EXTRACTION PLAN

## Scope
This phase is audit/documentation only. STRIX will not copy Hermes source, create a Hermes runtime, install Hermes, integrate Hermes gateway/tools, or change STRIX core/Agent Zero/OpenCLAW/Hermes/Qwen/TurboQuant/llama.cpp/WSL2.

## Source Finding
- Local STRIX Hermes agent source: NOT FOUND.
- Local STRIX references: docs/status/license entries only.
- Unrelated local `Hermes` hits: React Native/Hermes JS engine parser/compiler files and vLLM Hermes tool parser in other projects; not audited as Hermes Agent.
- Public reference used: `https://github.com/NousResearch/hermes-agent` GitHub tree metadata and public README/docs references; metadata only, no code copied.

## Strategy Counts
- ADAPT_PATTERN: 8
- REIMPLEMENT_CLEAN: 5
- DOCUMENT_ONLY: 2
- DISCARD: 1
- FUTURE_RESEARCH: 1

## Top Useful Patterns
1. Tool/toolset routing with strict non-execution and sandbox-required metadata.
2. Approval/HITL button and command regressions mapped to STRIX approval_id/action_hash verification.
3. Cron/long-running task model for future scheduled defensive audits.
4. Skill/plugin metadata structure for STRIX extension templates, without plugin execution.
5. Context compression/session recovery tests to strengthen Phase 7J memory/context under policy constraints.

## Extraction Decisions
### orchestration patterns
- Decision: ADAPT_PATTERN
- Source path/reference: `README.md; agent/*; run_agent.py; website/docs/developer-guide/architecture.md; tests/run_agent/*`
- STRIX strategy: Useful as a comparison point for STRIX mission lifecycle orchestration and evidence checkpoints.
- Risk: Medium: importing runtime loop would create a parallel Hermes runtime and compete with Saga Fusion controls.
- Target phase: 8B

### memory/context
- Decision: DOCUMENT_ONLY
- Source path/reference: `agent/memory_manager.py; agent/memory_provider.py; agent/context_engine.py; plugins/memory/*; website/docs/user-guide/features/memory/`
- STRIX strategy: Useful to evolve STRIX process-local memory toward durable/semantic memory later while preserving redaction and non-authoritative status.
- Risk: Medium: direct memory injection can leak secrets or override policy if treated as authority.
- Target phase: 8B

### planning
- Decision: REIMPLEMENT_CLEAN
- Source path/reference: `tools/todo_tool.py; skills/software-development/plan/SKILL.md; plans/*; .plans/*; tests/tools/test_todo_tool.py`
- STRIX strategy: Useful to refine STRIX TaskPlanner outputs and require explicit verification artifacts per step.
- Risk: Medium: plans must remain declarative until SandboxController/ApprovalVerifier execution phases.
- Target phase: 8B

### agents/subagents
- Decision: ADAPT_PATTERN
- Source path/reference: `tools/delegate_tool.py; tests/tools/test_delegate*.py; tests/agent/test_subagent_progress.py; skills/software-development/subagent-driven-development/*`
- STRIX strategy: Useful for future STRIX subagent orchestration under isolated scopes and parent-visible evidence.
- Risk: High: subagents can bypass policy or multiply unsafe actions if not scoped and audited.
- Target phase: 8C

### tool routing
- Decision: REIMPLEMENT_CLEAN
- Source path/reference: `model_tools.py; toolsets.py; toolset_distributions.py; agent/tool_guardrails.py; hermes_cli/tools_config.py; tests/tools/*`
- STRIX strategy: Useful to harden STRIX ToolRouter taxonomy, toolset scopes, and test coverage without adding executors.
- Risk: High: direct tool execution is unsafe; STRIX must keep ToolRouter non-executing until explicitly approved.
- Target phase: 8B

### approval/HITL
- Decision: ADAPT_PATTERN
- Source path/reference: `tools/approval.py; tests/tools/test_approval*.py; tests/gateway/test_*_approval_buttons.py; tests/gateway/test_approve_deny_commands.py`
- STRIX strategy: Useful to compare against STRIX structured R4 approval IDs, action hashes, expiry, and replay resistance.
- Risk: Medium: duplicate approval paths can conflict; STRIX ApprovalVerifier must remain single authority.
- Target phase: 8B

### sandbox/policy
- Decision: ADAPT_PATTERN
- Source path/reference: `tools/terminal_tool.py; tools/environments/vercel_sandbox.py; environments/*; tests/tools/test_terminal_*; tests/environments/*security*`
- STRIX strategy: Useful for future STRIX execution adapter requirements and sandbox evidence capture.
- Risk: High: terminal backends are execution-capable; document patterns only until a later approved execution phase.
- Target phase: 8C

### evidence/reporting
- Decision: REIMPLEMENT_CLEAN
- Source path/reference: `optional-skills/security/oss-forensics/references/evidence-types.md; optional-skills/security/oss-forensics/scripts/evidence-store.py; tests/test_evidence_store.py; optional-skills/security/oss-forensics/templates/*report.md`
- STRIX strategy: Useful to extend STRIX Reporting with evidence manifests, chain-of-custody fields, and artifact integrity hashes.
- Risk: Low/Medium: reporting is safe if redaction, fingerprints, and output budgets remain mandatory.
- Target phase: 8B

### long-running tasks
- Decision: ADAPT_PATTERN
- Source path/reference: `cron/scheduler.py; cron/jobs.py; hermes_cli/cron.py; tools/cronjob_tools.py; tests/cron/*; website/docs/developer-guide/cron-internals.md`
- STRIX strategy: Useful for STRIX scheduled audits/recurring defensive checks as dry-run report jobs.
- Risk: Medium: unattended jobs can hit approval gates or leak stale context; require explicit scope and dry-run defaults.
- Target phase: 8C

### failure recovery
- Decision: ADAPT_PATTERN
- Source path/reference: `agent/error_classifier.py; tests/run_agent/test_1630_context_overflow_loop.py; tests/gateway/test_session_state_cleanup.py; tests/cron/test_cron_inactivity_timeout.py; release notes`
- STRIX strategy: Useful to add STRIX failure taxonomy, retry budgets, and recovery evidence for mission runs.
- Risk: Medium: automated retry can loop or repeat sensitive actions unless bounded.
- Target phase: 8C

### token/context compression
- Decision: DOCUMENT_ONLY
- Source path/reference: `agent/context_compressor.py; agent/manual_compression_feedback.py; trajectory_compressor.py; website/docs/developer-guide/context-compression-and-caching.md; tests/*compress*`
- STRIX strategy: Useful for STRIX long-context summaries and evidence-aware context windows after Phase 7J.
- Risk: Medium: compression can drop safety constraints or evidence; system policy must never be compressed away.
- Target phase: 8C

### skill/plugin patterns
- Decision: REIMPLEMENT_CLEAN
- Source path/reference: `agent/skill_commands.py; agent/skill_preprocessing.py; hermes_cli/skills_config.py; hermes_cli/plugins.py; plugins/*/plugin.yaml; skills/*/SKILL.md`
- STRIX strategy: Useful for a STRIX extension taxonomy under `extensions/` and future docs-only skill templates.
- Risk: Medium: untrusted skills/plugins can introduce prompt injection or side effects.
- Target phase: 8B

### observability
- Decision: REIMPLEMENT_CLEAN
- Source path/reference: `hermes_logging.py; tests/test_hermes_logging.py; web/src/*; ui-tui/*; tests/cli/test_cli_terminal_response_sanitizer.py`
- STRIX strategy: Useful to enrich STRIX redacted logs, mission timelines, and dashboard-ready summaries.
- Risk: Low/Medium: observability can leak prompts/secrets if not redacted at source.
- Target phase: 8C

### security guardrails
- Decision: ADAPT_PATTERN
- Source path/reference: `SECURITY.md; tools/path_security.py; tools/tirith_security.py; agent/file_safety.py; tests/agent/test_streaming_context_scrubber.py; tests/cli/test_worktree_security.py`
- STRIX strategy: Useful to broaden STRIX PromptSecurity, path safety, and redaction regression corpus.
- Risk: High: guardrails must fail closed and cannot lower existing R4/R5 policy.
- Target phase: 8B

### dangerous action handling
- Decision: ADAPT_PATTERN
- Source path/reference: `agent/tool_guardrails.py; tests/tools/test_force_dangerous_override.py; tests/tools/test_terminal_none_command_guard.py; tests/tools/test_terminal_foreground_timeout_cap.py`
- STRIX strategy: Useful to expand STRIX DangerousActionPolicy regression coverage and explainers.
- Risk: High: dangerous override concepts must not become user-accessible bypasses.
- Target phase: 8B

### messaging gateway patterns
- Decision: DISCARD
- Source path/reference: `gateway/*; gateway/platforms/telegram.py; gateway/platforms/*; gateway/session.py; website/docs/user-guide/messaging/*`
- STRIX strategy: Limited value because STRIX already has its own Telegram gateway; only session/gating ideas are relevant.
- Risk: High: integrating Hermes gateway would violate no-runtime/no-Telegram-real constraints and duplicate STRIX interface.
- Target phase: N/A

### self-improvement/RL research
- Decision: FUTURE_RESEARCH
- Source path/reference: `agent/curator.py; plugins/*; tinker-atropos; trajectory_compressor.py; website/docs/getting-started/learning-path.md`
- STRIX strategy: Potential long-term research for defensive evaluation, not needed for STRIX current safety roadmap.
- Risk: High: self-modifying skills can mutate policy or create unsafe automation if uncontrolled.
- Target phase: 9+

## 8B Recommendation
Start Phase 8B with documentation-first design for Hermes-inspired extension/skill/plugin governance, toolset scoping, approval/cron/session recovery test requirements, and evidence manifests. Do not implement a Hermes compatibility layer, gateway, terminal backend, or self-improvement runtime.
