# STRIX TOOL MAP - EXECUTION ENVIRONMENT

## 1. Tool Execution Layer
- **Mechanism:** `asyncio.subprocess` for shell commands.
- **State:** `AgentState` manages tool invocation context.
- **Integration:** `BaseAgent` invokes tools via `_execute_actions`.

## 2. Identified Tools (Inferred from Strix Patterns)
- **Shell:** Bash execution via `asyncio.subprocess`.
- **Browser:** Headless browser interaction (likely Playwright/Selenium).
- **Filesystem:** Read/Write operations on the host.
- **Network:** HTTP requests (likely `aiohttp` or `requests`).

## 3. Tool Invocation Flow
1. **LLM generates action:** `{"tool": "shell", "args": {"cmd": "ls -la"}}`.
2. **Tool Router:** Maps action to `BaseAgent` tool handler.
3. **Execution:** Runs tool in sandboxed environment.
4. **Result:** Returns output to `AgentState` for next iteration.
