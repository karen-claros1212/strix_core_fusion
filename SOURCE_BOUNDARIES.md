# SOURCE BOUNDARIES - STRIX ELITE CYBER AGENT

## 1. Strix Base (Core Apache 2.0)
- **Location:** `strix_base/strix/`
- **Content:** Original agent loop, state management, and tool invocation logic.
- **Boundary:** Read-only for Saga Fusion. Modifications only via adapters or explicit overrides.

## 2. Saga Fusion (New Layer)
- **Location:** `strix_base/saga_fusion/`
- **Content:** Context management, security policies, tool guards, and adapters.
- **Boundary:** Independent modules. No direct dependency on Strix internals except via `StrixAgentAdapter`.

## 3. Tests
- **Location:** `strix_base/tests/`
- **Content:** Unit, integration, and security tests for Saga Fusion.
- **Boundary:** Must not break Strix base functionality.
