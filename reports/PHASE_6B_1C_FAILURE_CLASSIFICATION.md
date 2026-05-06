# PHASE 6B-1C FAILURE CLASSIFICATION

| Test File | Test Name | Error Exact | Category | Contract Affected | Decision |
|-----------|-----------|-------------|----------|-------------------|----------|
| `tests/sandbox/test_sandbox_controller.py` | `test_execute_dry_run` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_controller.py` | `test_execute_real_command_success` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_controller.py` | `test_validate_action_block_r5` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_controller.py` | `test_validate_action_success` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_policy.py` | `test_validate_command_privileged` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_policy.py` | `test_validate_command_r5` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_runtime.py` | `test_policy_allows_r0` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_runtime.py` | `test_policy_blocks_r5` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_runtime.py` | `test_policy_blocks_privileged_docker` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_runtime.py` | `test_policy_blocks_docker_sock` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_runtime.py` | `test_filesystem_jailer_blocks_symlinks` | `assert True == False` | 5. Error real de lógica | `FilesystemJailer` | Corregir código |
| `tests/sandbox/test_sandbox_runtime.py` | `test_network_jailer_allows_internal` | `assert False == True` | 5. Error real de lógica | `NetworkJailer` | Corregir código |
| `tests/sandbox/test_sandbox_runtime.py` | `test_resource_limiter_allows_within_limits` | `AttributeError: 'ResourceLimiter' object has no attribute 'is_allowed'` | 2. Código incumple contrato congelado | `ResourceLimiter` | Corregir código |
| `tests/sandbox/test_sandbox_runtime.py` | `test_resource_limiter_blocks_over_limits` | `AttributeError: 'ResourceLimiter' object has no attribute 'is_allowed'` | 2. Código incumple contrato congelado | `ResourceLimiter` | Corregir código |
| `tests/sandbox/test_sandbox_runtime.py` | `test_sandbox_audit_logs_action` | `SandboxAudit.__init__() missing 1 required positional argument: 'config'` | 2. Código incumple contrato congelado | `SandboxAudit` | Corregir código |
| `tests/sandbox/test_sandbox_runtime.py` | `test_sandbox_controller_executes_dry_run` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/sandbox/test_sandbox_runtime.py` | `test_sandbox_controller_blocks_r5` | `SandboxAction.__init__() got an unexpected keyword argument 'risk_level'` | 1. Test espera contrato viejo | `SandboxAction` | Corregir test |
| `tests/telegram/test_command_parser.py` | `test_classify_risk_create` | `AssertionError: 'R0' != <RiskLevel.R3: 'R3'>` | 4. Ruta legacy usada todavía | `CommandParser` | Corregir test |
| `tests/telegram/test_command_parser.py` | `test_classify_risk_run` | `AssertionError: 'R0' != <RiskLevel.R4: 'R4'>` | 4. Ruta legacy usada todavía | `CommandParser` | Corregir test |
| `tests/telegram/test_command_parser.py` | `test_classify_risk_unknown` | `AssertionError: 'R0' != <RiskLevel.R0: 'R0'>` | 4. Ruta legacy usada todavía | `CommandParser` | Corregir test |
| `tests/telegram/test_telegram_gateway.py` | `test_handle_message_unauthorized_user` | `AttributeError: 'MockTelegramGateway' object has no attribute 'handle_message'` | 1. Test espera contrato viejo | `TelegramGateway` | Corregir test |
| `tests/telegram/test_telegram_gateway.py` | `test_handle_message_unknown_command` | `AttributeError: 'MockTelegramGateway' object has no attribute 'handle_message'` | 1. Test espera contrato viejo | `TelegramGateway` | Corregir test |
| `tests/telegram/test_telegram_gateway.py` | `test_handle_message_valid_command` | `AttributeError: 'MockTelegramGateway' object has no attribute 'handle_message'` | 1. Test espera contrato viejo | `TelegramGateway` | Corregir test |
| `tests/telegram/test_telegram_mission_operator.py` | `test_evidence_log_redacts_secrets` | `AssertionError: assert 'REDACTED' in 'api_key=***'` | 5. Error real de lógica | `EvidenceLogger` | Corregir código |
| `tests/telegram/test_telegram_mission_operator.py` | `test_operator_end_to_end_dry_run` | `AssertionError: assert 'requires approval' in "Mission executed: ..."` | 5. Error real de lógica | `TelegramMissionOperator` | Corregir código |
| `tests/unit/test_sandbox_policy.py` | `test_dangerous_command_docker` | `TypeError: 'bool' object is not subscriptable` | 1. Test espera contrato viejo | `SandboxPolicy` | Corregir test |
| `tests/unit/test_sandbox_policy.py` | `test_dangerous_command_kubectl` | `TypeError: 'bool' object is not subscriptable` | 1. Test espera contrato viejo | `SandboxPolicy` | Corregir test |
| `tests/unit/test_sandbox_policy.py` | `test_docker_socket` | `TypeError: 'bool' object is not subscriptable` | 1. Test espera contrato viejo | `SandboxPolicy` | Corregir test |
| `tests/unit/test_sandbox_policy.py` | `test_filesystem_inside_workspace` | `AssertionError: False is not true` | 5. Error real de lógica | `SandboxPolicy` | Corregir código |
| `tests/unit/test_sandbox_policy.py` | `test_filesystem_outside_workspace` | `AssertionError: 'Ruta fuera del workspace' not found in 'Path outside workspace'` | 5. Error real de lógica | `SandboxPolicy` | Corregir código |
| `tests/unit/test_sandbox_policy.py` | `test_filesystem_path_traversal` | `AssertionError: 'Path traversal' not found in 'Path outside workspace'` | 5. Error real de lógica | `SandboxPolicy` | Corregir código |
| `tests/unit/test_sandbox_policy.py` | `test_network_aws_metadata` | `AssertionError: 'Metadata endpoint' not found in 'Metadata IP'` | 5. Error real de lógica | `SandboxPolicy` | Corregir código |
| `tests/unit/test_sandbox_policy.py` | `test_network_gcp_metadata` | `AssertionError: True is not false` | 5. Error real de lógica | `SandboxPolicy` | Corregir código |
| `tests/unit/test_sandbox_policy.py` | `test_path_traversal` | `TypeError: 'bool' object is not subscriptable` | 1. Test espera contrato viejo | `SandboxPolicy` | Corregir test |
| `tests/unit/test_sandbox_policy.py` | `test_shadow_file` | `TypeError: 'bool' object is not subscriptable` | 1. Test espera contrato viejo | `SandboxPolicy` | Corregir test |
| `tests/unit/test_sandbox_policy.py` | `test_valid_command` | `TypeError: 'bool' object is not subscriptable` | 1. Test espera contrato viejo | `SandboxPolicy` | Corregir test |
