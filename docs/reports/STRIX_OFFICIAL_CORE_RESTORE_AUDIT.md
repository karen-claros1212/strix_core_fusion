# STRIX Official Core Restore Audit

**Date:** 2026-05-14
**Executor:** Morgan (subagent:strix-official-audit)
**Work dir:** `/home/jesus/Proyectos/strix_core_fusion`

---

## 1. STRIX oficial clonado

**SI** — `git clone https://github.com/usestrix/strix` completado en `external_sources/strix_official`. 94 archivos Python en 4 niveles de profundidad.

---

## 2. Tag real usado

**v0.8.3**

```
$ git describe --tags --always --abbrev=0
v0.8.3
$ git log --oneline -5
7d5a45d chore: bump version to 0.8.3
dec2c47 fix: use anthropic model in anthropic provider docs example
4f90a56 fix: strengthen tool-call requirement in interactive and autonomous modes
640bd67 chore: bump sandbox image to 0.1.13
4e83637 refine system prompt, add scope verification, and improve tool guidance
```

---

## 3. Licencia Apache-2.0 confirmada

**SI** — `pyproject.toml` contiene `license = "Apache-2.0"`. Archivo `LICENSE` presente en raíz del repo oficial.

---

## 4. StrixAgent importable en repo actual

**NO** — Falla con `ImportError: cannot import name 'StrixAgent' from 'strix.agents' (unknown location)`.

El directorio `strix/` actual no tiene `__init__.py`, no expone `StrixAgent`, y no tiene la estructura de paquetes necesaria.

```python
$ python3 -c "from strix.agents import StrixAgent; print('StrixAgent OK')"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ImportError: cannot import name 'StrixAgent' from 'strix.agents' (unknown location)
```

---

## 5. strix-agent instalado como paquete pip

**NO**

```
$ pip3 show strix-agent
WARNING: Package(s) not found: strix-agent
```

No está instalado en ningún entorno del sistema.

---

## 6. Repo actual contiene STRIX oficial completo

**NO**

El repo actual contiene **únicamente stubs mínimos** en `strix/`:
- `strix/agents/base_agent.py` — stub de ~30 líneas con métodos vacíos
- `strix/agents/state.py` — stub de ~31 líneas
- `strix/agents/unified_saga_agent.py` — ~113 líneas
- `strix/brain/` — 4 archivos de configuración de hybrid brain
- `strix/integrations/telegram/` — 3 archivos de integración Telegram

Contraste con **upstream v0.8.3** (~94 archivos):
- `strix/agents/StrixAgent/strix_agent.py` — clase `StrixAgent(BaseAgent)` completa con `execute_scan()`
- `strix/agents/base_agent.py` — 400+ líneas con `agent_loop()`, `_execute_actions()`, `AgentMeta`
- `strix/tools/` — 11 toolkits completos: browser, proxy, terminal, file_edit, python, web_search, reporting, thinking, todo, notes, finish, load_skill, agents_graph
- `strix/llm/` — LLM config, deduplicación, memory_compressor
- `strix/runtime/` — Docker runtime, tool server
- `strix/interface/` — CLI, TUI (Textual), streaming parser, 16 renderers de tool components
- `strix/config/`, `strix/telemetry/`, `strix/skills/`, `strix/utils/`
- `tests/` — 14 archivos de test

---

## 7. Repo actual contiene stubs/parcial

**SI**

El directorio `strix/` contiene stubs funcionales mínimos diseñados para compatibilidad con `saga_fusion/`. El `BaseAgent` actual es placeholder (~30 líneas, métodos vacíos). El verdadero motor está en `saga_fusion/` (~150+ archivos).

---

## 8. Diferencias principales

| Dimensión | Upstream STRIX v0.8.3 | Repo actual (strix_core_fusion) |
|---|---|---|
| **Agente** | `StrixAgent(BaseAgent)` con `execute_scan()` 300 iteraciones | `UnifiedSagaAgent(BaseAgent)` — stub, sin scan |
| **Toolkit** | browser, proxy, terminal, file_edit, python, web_search, reporting, thinking, todo, notes, finish, load_skill, agents_graph (13 módulos) | **Ninguno** — no hay toolkits en `strix/tools/` |
| **LLM** | `strix/llm/` completo (LiteLLM, dedup, compressor) | `saga_fusion/llm/` propio (router, brain_service, recovery, etc.) |
| **Runtime** | Docker runtime, tool server | `saga_fusion/runtime/` (sandbox, process_guard, output_budget) |
| **CLI** | `strix.interface.main:main` con TUI y CLI | No hay CLI propia de STRIX; usa adaptador Telegram |
| **Telemetry** | PostHog, OpenTelemetry | No tiene |
| **Skills** | Skills cargables por Jinja | `saga_fusion/skills/` propio (manifest, policy, registry) |
| **Seguridad** | Scope context, tool validation | `saga_fusion/` completo: policy R4/R5, approval gates, prompt security, tool routing, tool scoping |
| **Defensa** | No tiene | `saga_fusion/defensive_workflows/`, `saga_fusion/cyber_knowledge/`, `saga_fusion/workflows/` |
| **Telegram** | No tiene | `saga_fusion/telegram/` y `strix/integrations/telegram/` completo |

---

## 9. Decisión

**< 50% match → RECOMENDACIÓN: Reemplazar stubs con actualización directa del core oficial + wrappers**

Fundamento:
- `strix/` actual NO contiene nada del STRIX oficial; son stubs placeholder
- `saga_fusion/` es una capa de seguridad/defensa completamente independiente
- El Match Rate estimado entre `strix/` actual y `strix/` oficial es **<10%**
- No hay conflictos de importación porque `strix/` actual no expone los mismos nombres

**Estrategia recomendada:**

1. **No reemplazar** `strix/` completo (eso rompería la estructura actual)
2. **Integrar** STRIX oficial como dependencia pip (`pip install strix-agent==0.8.3`)
3. **Crear wrappers** en `strix_engine/` para conectar `StrixAgent` oficial con `saga_fusion/`
4. **Mantener** `strix/integrations/telegram/` y `strix/brain/` como capa de integración

Alternativa válida:
- Vendorizar el core oficial en `external_sources/strix_official` (ya clonado) y crear symlinks o imports controlados desde `saga_fusion/strix_engine/`

---

## 10. Evaluación módulos Saga Fusion

| Módulo | Estado | Decisión |
|---|---|---|
| **Policy R4/R5** (`saga_fusion/policy/`) | Funcional, probado | ✅ **CONSERVAR** — no existe en STRIX oficial |
| **Approval** (`saga_fusion/approval/`) | Funcional, con tests de regresión | ✅ **CONSERVAR** — capa HITL propia |
| **Evidence** (`saga_fusion/evidence/`) | Integrado con reporting y manifests | ✅ **CONSERVAR** |
| **Telegram** (`saga_fusion/telegram/`) | Integración completa, misiones, lab mode | ✅ **CONSERVAR** — canal de operación real |
| **Hybrid brain** (`strix/brain/`, `saga_fusion/llm/brain_service.py`) | Configurable, probado | ✅ **CONSERVAR** — orquestación propia |
| **Command parser** (`saga_fusion/telegram/command_parser.py`) | Natural-first, misiones, defensivo | ✅ **CONSERVAR** — UX principal |
| **Tool routing** (`saga_fusion/tool_routing/`) | Clasificación, ejecución, políticas | ✅ **CONSERVAR** — reemplaza el tool registry upstream |
| **Tool scoping** (`saga_fusion/tool_scoping/`) | Loop guard, scope policy, registries | ✅ **CONSERVAR** |
| **Cyber knowledge** (`saga_fusion/cyber_knowledge/`) | MITRE, Sigma, YARA, IOC, malware taxonomía | ✅ **CONSERVAR** |
| **Defensive workflows** (`saga_fusion/defensive_workflows/`) | 6+ workflows de respuesta a incidentes | ✅ **CONSERVAR** |
| **Prompt security** (`saga_fusion/prompt_security/`) | Detección de inyección, sanitización | ✅ **CONSERVAR** |
| **Memory** (`saga_fusion/memory/`) | Context window, retrieval, policies | ✅ **CONSERVAR** |
| **Manifests** (`saga_fusion/manifests/`) | Build, hash, policy, redactor | ✅ **CONSERVAR** |
| **Scheduler** (`saga_fusion/scheduler/`) | Cron validation, planner, registry | ✅ **CONSERVAR** |
| **Repositorio y workflows** (`saga_fusion/repo_audit/`, `saga_fusion/workflows/`) | Auditoría de código, hardening | ✅ **CONSERVAR** |
| **Session** (`saga_fusion/session/`) | Recovery, compressor, registry | ✅ **CONSERVAR** |
| **Skills** (`saga_fusion/skills/`) | Manifest, policy, validator, registry | ✅ **CONSERVAR** |
| **Reporting** (`saga_fusion/reporting/`) | Técnico, ejecutivo, Telegram formatter | ✅ **CONSERVAR** |
| **Runtime sandbox** (`saga_fusion/runtime/sandbox/`) | Docker, filesystem jail, network jail, resource limiter | ✅ **CONSERVAR** |
| **Task planning** (`saga_fusion/task_planning/`) | Patrones, planner, mission steps | ✅ **CONSERVAR** |

**Decisión global: NINGÚN módulo de saga_fusion debe descartarse. Son capas de seguridad y defensa que no existen en el STRIX oficial v0.8.3.**

---

## 11. Qué NO debe seguir ocurriendo

1. **❌ No mantener stubs vacíos en `strix/`** — `base_agent.py` actual es placeholder sin funcionalidad real. Reemplazar por import del oficial o wrapper funcional.

2. **❌ No desarrollar toolkits propios** (browser, proxy, terminal, file_edit) que ya existen en STRIX oficial. Usar los de upstream vía dependencia pip o vendorización.

3. **❌ No ignorar el upstream** — STRIX oficial v0.8.3 es un producto maduro con ~94 archivos, 13 toolkits, TUI, telemetría. El proyecto actual se beneficiaría enormemente de integrar este core.

4. **❌ No mezclar imports** — `strix/` actual y `strix/` oficial comparten namespace `strix.*`. Si se instala `pip install strix-agent==0.8.3` o se vendiriza, hay que gestionar la precedencia de imports.

5. **❌ No tener pyproject.toml** — El repo actual carece de pyproject.toml. El upstream ofrece una base excelente para configurar build, linting, type checking y testing.

6. **❌ No bifurcar manualmente funcionalidad que STRIX oficial ya resuelve** — `saga_fusion/tool_routing/` y `saga_fusion/tool_scoping/` son equivalentes conceptuales al `tool registry` y `tool executor` de upstream; evaluar si se pueden simplificar delegando en el core oficial.

---

## Resumen

| Métrica | Valor |
|---|---|
| STRIX oficial clonado | ✅ SI (v0.8.3) |
| Licencia | Apache-2.0 |
| `strix-agent` pip instalado | ❌ NO |
| StrixAgent importable | ❌ NO |
| Match stubs vs oficial | < 10% |
| Saga Fusion módulos | ~150+ archivos, todos conservar |
| Acción recomendada | `pip install strix-agent==0.8.3` + wrappers en `strix_engine/` |

**El proyecto strix_core_fusion NO contiene el core oficial de STRIX. Es una arquitectura de seguridad/defensa (saga_fusion) con stubs placeholder en strix/. La integración con STRIX oficial v0.8.3 es el siguiente paso lógico.**
