# PROMPT MAESTRO FASE 0 + FASE 1: AUDITORÍA SAST DE STRIX BASE

## Contexto
Evolución de Strix a Strix Elite Cyber Agent.
Fase 0+1: Auditar Strix real, mapear archivos, congelar baseline.

## Instrucción
Actúa como Lead Security Engineer. Ejecuta auditoría SAST profunda sobre `strix_base/strix/`.

### 1. Exploración
- `find` todos los `.py` en `strix_base/strix/`.
- Identifica: `base_agent.py`, `agent_state.py`, `tools/`, `browser/`, `config.py`.

### 2. Análisis del Núcleo
- Mapea: `agent_loop()`, `_process_iteration()`.
- LLM: `LLMConfig`, `max_tokens`.
- Estado: `AgentState`, memoria.

### 3. Análisis de Herramientas
- `process_tool_invocations()`.
- `asyncio.subprocess` (Shell).
- Navegador y Archivos.

### 4. Seguridad
- Inyección (Input -> LLM -> Tool).
- Sanitización.
- Credenciales.

## Entrega
`STRIX_BASE_AUDIT_REPORT.md`:
- Mapa de clases/métodos.
- Diagrama de flujo.
- Inventario de herramientas/riesgos.
- Puntos de inyección Saga Fusion.

## Restricciones
- No modificar.
- No monkey-patching.
- Core-agnostic.

## Directriz Rectora
"Trabaja exclusivamente sobre Strix como core Apache 2.0. No rediseñes desde cero. No toques Qwen 3.6, TurboQuant, llama.cpp, WSL2 ni servicios ya funcionando. Primero audita Strix real: BaseAgent, AgentState, tool invocation, subprocess, browser tools, estado, logs y configuración. Después crea una capa saga_fusion modular con adapters, memoria, policy engine, evidence store, self-verification, output budget, sandbox runtime y Telegram Mission Operator. No hagas monkey-patching. No metas lógica cyber dentro del core de Strix. Todo debe estar documentado, testeado y trazable. Cada fase debe dejar AUDIT_SYSTEM_STATUS.md actualizado. El objetivo final es Strix Elite Cyber Agent: auditor autónomo por misión, controlado por Telegram, ofensivo autorizado y defensivo, con reportes profesionales."
