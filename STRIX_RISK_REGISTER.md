# STRIX RISK REGISTER - SECURITY VULNERABILITIES

## 1. Context Management Risks
- **Risk:** Memory overflow due to unbounded conversation history.
- **Mitigation:** Implement `SagaContextManager` with soft/hard limits and summarization.

## 2. Tool Execution Risks
- **Risk:** Command injection via LLM-generated actions.
- **Mitigation:** `SagaSecurityPolicy` with regex-based allow/deny lists.

## 3. Credential Leakage
- **Risk:** API keys or SSH keys exposed in logs or outputs.
- **Mitigation:** `SecretRedactor` middleware to mask sensitive patterns.

## 4. Sandbox Escape
- **Risk:** Tools breaking out of the execution environment.
- **Mitigation:** Strict `SandboxRuntime` with resource limits and network policies.

## Risk Register Update (Phase 6B-2)
- [CLOSED] RB-6B2-01: Telegram Mission Operator not implemented → Mock mode complete
- [CLOSED] RB-6B2-02: Sandbox block on Codex writes → Writable root configured
- [OPEN] RB-6B3-01: Real Telegram connection pending Phase 6B-3
