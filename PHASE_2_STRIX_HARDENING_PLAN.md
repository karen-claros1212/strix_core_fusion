# PHASE 2 STRIX HARDENING PLAN
## Fase 2: Evolución a Strix Elite Cyber Agent

**Fecha:** 2026-05-03
**Basado en:** `STRIX_BASE_AUDIT_REPORT.md`

---

### 1. Objetivo
Migrar el motor experimental `UnifiedSagaAgent` al adaptador oficial `StrixSagaAgent`, eliminando el *monkey-patching* y robusteciendo la capa de seguridad y contexto.

### 2. Archivos a Tocando
- **`saga_fusion/strix_adapter.py`**:
  - Refactorizar `__init__` para inyección de dependencias.
  - Implementar `SagaContextManager` robusto.
  - Implementar `SagaToolGuard` con `SagaSecurityPolicy`.
- **`saga_fusion/context_manager.py`**:
  - Añadir lógica de resumen (LLM-based) para `hard_limit`.
  - Manejo seguro de `history` vacío.
- **`saga_fusion/security_policy.py`**:
  - Definir reglas de `allowlist` y `denylist` explícitas.

### 3. Archivos a NO Tocando
- **`strix/agents/base_agent.py`**: Mantener integridad de la herencia.
- **`strix/agents/state.py`**: No modificar estructura de estado base.

### 4. Interfaces a Crear/Actualizar
- **`SagaContextManager`**: Método `collapse_history(history, config) -> List[Dict]`.
- **`SagaSecurityPolicy`**: Método `evaluate_action(action) -> SecurityDecision`.
- **`SagaToolGuard`**: Método `execute(actions, executor) -> List[ToolResult]`.

### 5. Puntos de Integración Saga Fusion
1. **Pre-LLM**: `StrixSagaAgent._process_iteration()` llama a `context_manager.collapse_history()`.
2. **Pre-Exec**: `StrixSagaAgent._execute_actions()` llama a `tool_guard.evaluate_actions()`.

### 6. Eliminación de Monkey-Patching
- `UnifiedSagaAgent` usa `_original_method = self.method` y reasignación.
- `StrixSagaAgent` usará **composición**: `self.context_manager = SagaContextManager()`.

### 7. Orden de Implementación
1. **Día 1**: Implementar `SagaContextManager` (contexto vacío, límites, resumen).
2. **Día 2**: Implementar `SagaSecurityPolicy` (regex, shlex, allow/deny).
3. **Día 3**: Implementar `SagaToolGuard` (interceptación, logging).
4. **Día 4**: Actualizar `StrixSagaAgent` para usar los módulos anteriores.
5. **Día 5**: Pruebas unitarias y eliminación de `UnifiedSagaAgent`.

### 8. Criterios de Éxito
- [ ] `StrixSagaAgent` no usa *monkey-patching*.
- [ ] `SagaContextManager` maneja `history` vacío sin errores.
- [ ] `SagaSecurityPolicy` bloquea `rm -rf /` y permite `ls`.
- [ ] Logs sin secretos (`.ssh`, `.env`).
