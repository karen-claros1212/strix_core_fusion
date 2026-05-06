# FASE 6B-1C: CONTRACT FREEZE REPORT

**Fecha:** 2026-05-04
**Objetivo:** Congelar interfaces establecidas en la Fase 6B-1B para evitar regresiones en la Fase 6B-2.

## 1. Contratos de Sandbox

### 1.1. `SandboxAction` (saga_fusion/runtime/sandbox/sandbox_types.py)
**Estructura de Datos:**
- `action_id`: str (UUID)
- `action_type`: ActionType (EXECUTE, READ, WRITE)
- `command`: str
- `args`: list
- `mode`: SandboxMode (DRY_RUN, REAL)
- `workspace_path`: str
- `timeout_seconds`: int

**Nota Crítica:** NO incluye `risk_level`.

### 1.2. `SandboxPolicy` (saga_fusion/runtime/sandbox/sandbox_policy.py)
**Métodos:**
- `validate_path(path: str) -> bool`
- `validate_filesystem(path: str, workspace: str) -> dict` (Retorna `{'valid': bool, 'errors': list}`)
- `validate_network(target: str) -> dict` (Retorna `{'valid': bool, 'errors': list}`)
- `validate_command(action: SandboxAction) -> bool`
- `is_allowed(action: SandboxAction) -> bool`

### 1.3. `SandboxController` (saga_fusion/runtime/sandbox/sandbox_controller.py)
**Métodos:**
- `__init__(config: SandboxConfig = None)`
- `validate_action(action: SandboxAction) -> bool`
- `execute(action: SandboxAction) -> SandboxResult`

## 2. Contratos de Telegram

### 2.1. `CommandParser` (saga_fusion/telegram/command_parser.py)
**Métodos:**
- `parse(text: str) -> dict` (Retorna dict con `command`, `args`, `raw` o `{'error': ...}`)
- `classify_risk(cmd) -> str` (Retorna 'R0', 'R3', 'R4')

### 2.2. `TelegramGateway` (saga_fusion/telegram/telegram_gateway.py)
**Métodos:**
- `send_message(chat_id: str, text: str) -> bool`
- `send_document(chat_id: str, content: bytes, filename: str) -> bool`

**Nota:** NO tiene método `handle_message`.

## 3. Estado de Duplicación
- **Ruta Oficial:** `saga_fusion/telegram/`
- **Duplicado:** `saga_fusion/telegram_mission_operator/` (13 archivos)
- **Imports Activos:** Sí, `saga_fusion.telegram` importa desde `mission_operator`.

## 4. Riesgos de Shell
- **os.system:** Sí, presente en `saga_fusion/runtime/sandbox/sandbox_controller.py`.
- **shell=True:** Sí, presente en `saga_fusion/runtime/sandbox/sandbox_controller.py`.
- **subprocess:** Sí, presente en `saga_fusion/runtime/sandbox/sandbox_controller.py`.

## 5. Estado Git
- **Modificados:** 14 archivos (incluyendo backups y logs).
- **Sin seguimiento:** 4 archivos.
- **Limpio:** No.

## 6. Decisión
- **APTO PARA FASE 6B-2:** Sí, con base en estos contratos.
- **Acción:** Corregir tests para alinearse con los contratos congelados.
