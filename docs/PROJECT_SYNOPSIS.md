# STRIX ELITE CYBER AGENT - Synopsis
## Proposito
STRIX Elite Cyber Agent: core unico con Saga Fusion como capa propia de seguridad, sandbox, evidencia, Telegram, CloudOps.

## Raiz
/home/jesus/agent-zero/docker/run/agent-zero/usr/workdir/frameworks_fusion/strix_core_fusion/strix_base

## Estado de fases
- Fase 0+1: baseline/documentacion
- Fase 2/2.5: Saga Fusion sobre Strix real
- Fase 3/3.5: tests/regresion
- Fase 4: Evidence Store + Output Budget + Runtime Safety
- Fase 5: CloudOps / InfraOps Operator
- Fase 6B-1D-C: Sandbox + Telegram contracts fixed
- Fase 6B-2: Telegram mock mode
- Actual: 126/126 tests passed

## Arquitectura
- strix/: core
- saga_fusion/: capa propia
- saga_fusion/runtime/sandbox/: runtime seguro
- saga_fusion/telegram/: interfaz Telegram oficial
- saga_fusion/evidence/: evidencia
- extensions/cai_patterns/: patrones CAI
- extensions/hermes_patterns/: patrones Hermes

## Reglas
- STRIX es core unico
- Telegram es interfaz, no proyecto aparte
- R4 requiere aprobacion
- R5 bloqueado
- Nada ejecuta fuera de SandboxController
- No secretos en repo
- Codex programa; Morgan/OpenCLAW orquesta
