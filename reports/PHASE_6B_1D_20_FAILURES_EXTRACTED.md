# PHASE 6B-1D 20 FAILURES EXTRACTED REPORT

## 1. Log usado
- `reports/phase_6b_1d_loop_stop_tests.log`

## 2. Conteo exacto
- **Total Fallos:** 20

## 3. Lista de Fallos
### 1. test_validate_network_blocked_ip
- **Archivo de Test:** `tests/sandbox/test_network_jailer.py::TestNetworkJailer`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/network_jailer.py::TestNetworkJailer`

### 2. test_validate_network_metadata_ip
- **Archivo de Test:** `tests/sandbox/test_network_jailer.py::TestNetworkJailer`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/network_jailer.py::TestNetworkJailer`

### 3. test_execute_dry_run
- **Archivo de Test:** `tests/sandbox/test_sandbox_controller.py::TestSandboxController`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_controller.py::TestSandboxController`

### 4. test_execute_real_command_success
- **Archivo de Test:** `tests/sandbox/test_sandbox_controller.py::TestSandboxController`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_controller.py::TestSandboxController`

### 5. test_validate_action_block_r5
- **Archivo de Test:** `tests/sandbox/test_sandbox_controller.py::TestSandboxController`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_controller.py::TestSandboxController`

### 6. test_validate_command_privileged
- **Archivo de Test:** `tests/sandbox/test_sandbox_policy.py::TestSandboxPolicy`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_policy.py::TestSandboxPolicy`

### 7. test_validate_command_r5
- **Archivo de Test:** `tests/sandbox/test_sandbox_policy.py::TestSandboxPolicy`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_policy.py::TestSandboxPolicy`

### 8. test_policy_blocks_privileged_docker
- **Archivo de Test:** `tests/sandbox/test_sandbox_runtime.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_runtime.py`

### 9. test_filesystem_jailer_blocks_symlinks
- **Archivo de Test:** `tests/sandbox/test_sandbox_runtime.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_runtime.py`

### 10. test_network_jailer_allows_internal
- **Archivo de Test:** `tests/sandbox/test_sandbox_runtime.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_runtime.py`

### 11. test_sandbox_audit_logs_action
- **Archivo de Test:** `tests/sandbox/test_sandbox_runtime.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_runtime.py`

### 12. test_sandbox_controller_executes_dry_run
- **Archivo de Test:** `tests/sandbox/test_sandbox_runtime.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_runtime.py`

### 13. test_sandbox_controller_blocks_r5
- **Archivo de Test:** `tests/sandbox/test_sandbox_runtime.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/sandbox/sandbox_runtime.py`

### 14. test_classify_risk_create
- **Archivo de Test:** `tests/telegram/test_command_parser.py::TestCommandParser`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/command_parser.py::TestCommandParser`

### 15. test_classify_risk_run
- **Archivo de Test:** `tests/telegram/test_command_parser.py::TestCommandParser`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/command_parser.py::TestCommandParser`

### 16. test_classify_risk_unknown
- **Archivo de Test:** `tests/telegram/test_command_parser.py::TestCommandParser`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/command_parser.py::TestCommandParser`

### 17. test_handle_message_unauthorized_user
- **Archivo de Test:** `tests/telegram/test_telegram_gateway.py::TestTelegramGateway`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/telegram_gateway.py::TestTelegramGateway`

### 18. test_handle_message_unknown_command
- **Archivo de Test:** `tests/telegram/test_telegram_gateway.py::TestTelegramGateway`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/telegram_gateway.py::TestTelegramGateway`

### 19. test_evidence_log_redacts_secrets
- **Archivo de Test:** `tests/telegram/test_telegram_mission_operator.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/telegram_mission_operator.py`

### 20. test_operator_end_to_end_dry_run
- **Archivo de Test:** `tests/telegram/test_telegram_mission_operator.py`
- **Error Exacto:** ``
- **Archivo Probable a Corregir:** `saga_fusion/telegram/telegram_mission_operator.py`


## 4. Agrupación por Módulo

### SandboxResult
- (Sin fallos reportados en este módulo)

### SandboxPolicy
- `test_validate_command_privileged`: 
- `test_validate_command_r5`: 

### SandboxController
- `test_execute_dry_run`: 
- `test_execute_real_command_success`: 
- `test_validate_action_block_r5`: 

### SandboxRuntime
- `test_policy_blocks_privileged_docker`: 
- `test_filesystem_jailer_blocks_symlinks`: 
- `test_network_jailer_allows_internal`: 
- `test_sandbox_audit_logs_action`: 
- `test_sandbox_controller_executes_dry_run`: 
- `test_sandbox_controller_blocks_r5`: 

### NetworkJailer
- `test_validate_network_blocked_ip`: 
- `test_validate_network_metadata_ip`: 

### CommandParser
- `test_classify_risk_create`: 
- `test_classify_risk_run`: 
- `test_classify_risk_unknown`: 

### TelegramGateway
- `test_handle_message_unauthorized_user`: 
- `test_handle_message_unknown_command`: 

### MissionOperator
- `test_evidence_log_redacts_secrets`: 
- `test_operator_end_to_end_dry_run`: 


## 5. Confirmación
- No modifiqué código.
- No ejecuté correcciones.
- No ejecuté pytest en bucle.
