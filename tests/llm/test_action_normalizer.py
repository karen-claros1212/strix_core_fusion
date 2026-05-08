from saga_fusion.llm.response_parser import ResponseParser
from saga_fusion.telegram.mission_policy import MissionPolicy
from saga_fusion.telegram.telegram_types import MissionRequest, RiskLevel


def classify(text: str) -> RiskLevel:
    mission = ResponseParser().fallback_mission(text)
    request = MissionRequest(
        raw_text=text,
        action_type=mission["action_type"],
        target=mission["target"],
        arguments=mission["arguments"],
    )
    return MissionPolicy().classify_risk(request)


def test_crea_vps_hostinger_is_r4():
    assert classify("Crea un VPS en Hostinger") == RiskLevel.R4


def test_cambia_dns_is_r4():
    assert classify("Cambia el DNS del dominio") == RiskLevel.R4


def test_abre_puerto_22_publico_is_r4():
    assert classify("Abre el puerto 22 al público") == RiskLevel.R4


def test_restaura_backup_is_r4():
    assert classify("Restaura un backup") == RiskLevel.R4


def test_elimina_servidor_is_r5():
    assert classify("Elimina el servidor") == RiskLevel.R5


def test_borra_backups_is_r5():
    assert classify("Borra backups") == RiskLevel.R5


def test_elimina_servidor_y_borra_backups_is_r5():
    assert classify("Elimina el servidor y borra backups") == RiskLevel.R5


def test_benign_revisa_estado_is_r0_or_r1():
    assert classify("revisa estado") in {RiskLevel.R0, RiskLevel.R1}


def test_benign_prepara_auditoria_dry_run_is_r2_or_r3():
    assert classify("prepara auditoría dry-run") in {RiskLevel.R2, RiskLevel.R3}


def test_highest_risk_wins_conflict():
    assert classify("Crea un VPS y luego elimina el servidor") == RiskLevel.R5
