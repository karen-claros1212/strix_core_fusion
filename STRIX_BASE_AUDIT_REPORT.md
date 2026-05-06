# STRIX BASE AUDIT REPORT
## Fase 0+1: Auditoría SAST Profunda

**Fecha:** 2026-05-03
**Fuente de Verdad:** Código real en `strix_base/strix/` y `strix_base/saga_fusion/`

---

### 1. Resumen Ejecutivo
Strix presenta una arquitectura base sólida pero con vulnerabilidades críticas en la gestión de contexto y ejecución de herramientas. El prototipo `UnifiedSagaAgent` utiliza *monkey-patching* agresivo, mientras que el adaptador oficial `StrixSagaAgent` implementa una integración middleware más limpia. Se identifican riesgos de inyección de comandos y desbordamiento de memoria no manejados.

### 2. Mapa Real del Core Strix
- **`strix/agents/unified_saga_agent.py`**: Motor Híbrido experimental. Hereda de `BaseAgent`.
- **`saga_fusion/strix_adapter.py`**: Adaptador oficial. Hereda de `BaseAgent`.
- **`saga_fusion/context_manager.py`**: Lógica de colapso de contexto (Mythos).
- **`saga_fusion/security_policy.py`**: Políticas de seguridad (CAI).

### 3. Call Graph Real
1. `StrixSagaAgent._process_iteration()`
   - `context_manager.collapse_history()`
   - `super()._process_iteration()` (Llama al LLM)
2. `StrixSagaAgent._execute_actions()`
   - `tool_guard.evaluate_actions()`
   - `super()._execute_actions()` (Ejecuta herramientas)

### 4. Tool Execution Flow
- **Entrada:** Acciones generadas por el LLM.
- **Filtro:** `SagaToolGuard` evalúa con `SagaSecurityPolicy`.
- **Ejecución:** `super()._execute_actions()` pasa las acciones permitidas.

### 5. LLM-to-Tool Taint Analysis
- **Origen:** `action['command']` generado por el LLM.
- **Sinks:** `asyncio.subprocess` (Shell), `page.evaluate` (Browser).
- **Flujo:** LLM -> `unified_saga_agent._current_actions` -> `subprocess.run()`.

### 6. Subprocess/Security Sinks
- `unified_saga_agent.py`:
  - **Riesgo:** `action['command']` se pasa directo a shell.
  - **Fallo:** `echo '[CAI] Ejecución denegada...'` para comandos bloqueados.
- `strix_adapter.py`:
  - **Mejora:** `tool_guard` devuelve `DENIED` sin ejecutar.

### 7. Browser Automation Risks
- **`page.evaluate`**: Sin sanitización de variables JS inyectadas.
- **`add_script_tag`**: Riesgo de XSS si el contenido no se escapa.

### 8. Filesystem Risks
- **`shutil.rmtree`**: Sin validación de `base_path`.
- **`os.path.exists`**: Race conditions en escritura.

### 9. Memory/Context Risks
- **`unified_saga_agent`**: Asume `history[0]` existe (IndexError si vacío).
- **`strix_adapter`**: Maneja `history` vacío correctamente.

### 10. Logging/Secrets Risks
- **`~/.ssh`**: No redactado en logs de `unified_saga_agent`.
- **`.env`**: Cargado sin sanitización de claves.

### 11. Async/Concurrency Risks
- **`asyncio.subprocess`**: Sin timeouts configurados.
- **`_current_actions`**: Mutación compartida sin locks.

### 12. Estado de Compatibilidad con Saga Fusion
- **Alto**: `StrixSagaAgent` está diseñado para ser core-agnóstico.
- **Medio**: `UnifiedSagaAgent` requiere refactorización para eliminar monkey-patching.

### 13. Matriz P0/P1/P2/P3
- **P0 (Crítico)**: Inyección de comandos en `unified_saga_agent`.
- **P1 (Alto)**: Desbordamiento de contexto sin resumen.
- **P2 (Medio)**: Log de secretos en `~/.ssh`.
- **P3 (Bajo)**: Falta de timeouts en subprocess.

### 14. Recomendaciones de Parche
1. Migrar `UnifiedSagaAgent` a `StrixSagaAgent`.
2. Implementar `SagaContextManager` robusto.
3. Añadir `SagaAuditLogger` para redactar secretos.

### 15. Criterios de Aceptación para Fase 2
- [ ] `StrixSagaAgent` sustituye a `UnifiedSagaAgent`.
- [ ] `SagaContextManager` maneja `history` vacío.
- [ ] `SagaToolGuard` bloquea acciones sin ejecutar `echo`.
