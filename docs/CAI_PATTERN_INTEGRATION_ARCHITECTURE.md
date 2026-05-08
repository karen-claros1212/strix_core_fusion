# CAI Pattern Integration Architecture for STRIX/Saga Fusion

## Principle
CAI is a reference pattern source only. STRIX does not import CAI code and does not run a CAI runtime. Patterns are reimplemented cleanly through Saga Fusion.

## Authoritative STRIX Controls
- MissionPolicy: risk classification and R0-R5 decisions.
- ApprovalWorkflow: R4 approval, replay/hash protection.
- SandboxController: mandatory execution boundary.
- EvidenceLogger: redacted evidence chain.
- OutputBudget and SecretRedactor: output/log safety.

## Target Modules
1. `saga_fusion/prompt_security/` — prompt-injection guard and safety labels.
2. `saga_fusion/tool_routing/` — tool intent contracts, denial reasons, sandbox dispatch metadata.
3. `saga_fusion/policy/` — dangerous action classifier and HITL gate metadata.
4. `saga_fusion/reporting/` — evidence-linked report engine.
5. `saga_fusion/task_planning/` — deterministic pattern registry.
6. `saga_fusion/memory/` — bounded redacted mission memory.
7. `extensions/cai_patterns/` — docs-only pattern taxonomy.

## Data Flow
Telegram/mock input -> PromptSecurity -> LLMRouter/BrainService -> TaskPlanning -> MissionPolicy -> ApprovalWorkflow if R4 -> SandboxController dry-run/approved dispatch -> EvidenceLogger -> Reporting.

## Non-Goals
- No external pentesting automation.
- No CloudOps real execution.
- No direct browser/terminal runtime.
- No malware payload generation.
- No CAI runtime compatibility layer.


## Phase 7C Implementation Note
`PromptSecurityLayer` is now the first natural-language security gate before BrainService/LLMRouter. It blocks prompt-injection and policy-bypass attempts before LLM calls, and passes WARN/ESCALATE metadata forward while MissionPolicy remains authoritative.
