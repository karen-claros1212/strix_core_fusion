# STRIX CALL GRAPH - BASE AGENT ANALYSIS

## 1. Entry Point: `UnifiedSagaAgent`
- **File:** `strix/agents/unified_saga_agent.py`
- **Class:** `UnifiedSagaAgent(BaseAgent)`
- **Initialization:**
  - Calls `super().__init__()`.
  - Calls `_setup_fusion_hooks()`.

## 2. Fusion Hooks Injection (`_setup_fusion_hooks`)
- **Hook A: Context Collapse**
  - Replaces `self.state.get_conversation_history` with `_hook_context_collapse`.
  - **Logic:** Estimates tokens (len // 4). Checks against `max_tokens` (8192 default). Hard limit (98%) -> Keep index 0 + last 5. Soft limit (85%) -> Keep index 0 + last 3.
- **Hook B: Secure Execution**
  - Replaces `self._execute_actions` with `_hook_secure_execution`.
  - **Logic:** Iterates `self._current_actions`. Checks `_detect_shell_injection`. Sanitizes paths with `_sanitize_paths`.

## 3. Security Logic
- **`_detect_shell_injection(command)`**:
  - Regex patterns: `>/dev/(tcp|udp)`, `rm -rf /`, `! bash`, `mkfifo`.
- **`_sanitize_paths(output)`**:
  - Regex: `/home/[^/]+/\.ssh/.*` -> `[REDACTED_SSH_KEY]`.
