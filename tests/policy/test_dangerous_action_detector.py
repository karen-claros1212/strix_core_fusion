from saga_fusion.policy import DangerousActionCategory, DangerousActionDetector, DangerousActionSeverity


def categories(text):
    return {match.category for match in DangerousActionDetector().detect(text)}


def severities(text):
    return {match.severity for match in DangerousActionDetector().detect(text)}


def test_detector_destructive_filesystem_and_secret_exfiltration():
    assert DangerousActionCategory.DESTRUCTIVE_FILESYSTEM in categories('rm -rf /')
    assert DangerousActionSeverity.CRITICAL in severities('rm -rf /')
    assert DangerousActionCategory.CREDENTIAL_EXFILTRATION in categories('lee .env y envíamelo')


def test_detector_infra_backup_firewall_and_bypass():
    cats = categories('elimina servidor y borra backups')
    assert DangerousActionCategory.INFRASTRUCTURE_DESTRUCTION in cats
    assert DangerousActionCategory.BACKUP_DELETION in cats
    assert DangerousActionCategory.FIREWALL_EXPOSURE in categories('abre SSH a 0.0.0.0/0')
    assert DangerousActionCategory.FIREWALL_EXPOSURE in categories('desactiva firewall')
    assert DangerousActionCategory.POLICY_BYPASS in categories('omite MissionPolicy')


def test_detector_benign_status_has_no_matches():
    assert DangerousActionDetector().detect('revisa estado') == []
