# FUSION ARCHITECTURE - STRIX ELITE CYBER AGENT

## 1. High-Level Overview
The Strix Elite Cyber Agent is built by layering the `saga_fusion` module on top of the Strix Base (Apache 2.0). This approach ensures that the core agent loop remains intact while adding advanced security, context management, and tool execution capabilities.

## 2. Core Components
- **Strix Base:** The foundation, providing the agent loop, state management, and tool invocation.
- **Saga Fusion:** The new layer, providing context collapse, security policies, tool guards, and adapters.
- **Adapters:** Bridge between Strix Base and Saga Fusion, ensuring loose coupling and core-agnostic design.

## 3. Data Flow
1. **Mission Received:** Telegram Mission Parser -> Scope Engine -> Strix Planner.
2. **Context Management:** SagaContextManager collapses history before LLM call.
3. **Action Generation:** LLM generates actions -> SagaToolGuard evaluates actions.
4. **Execution:** Approved actions are executed in the Sandbox Runtime.
5. **Evidence Collection:** Results are stored in the Evidence Store.
6. **Reporting:** Report Engine generates professional reports.

## 4. Key Design Principles
- **Core-Agnostic:** Saga Fusion modules are independent of Strix internals.
- **Defense in Depth:** Multiple layers of security (input, execution, output).
- **Traceability:** All decisions and actions are logged for forensic analysis.
