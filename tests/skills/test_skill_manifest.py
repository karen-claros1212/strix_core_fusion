from saga_fusion.skills import SkillManifest, SkillRiskLevel


def test_valid_manifest_round_trips_and_env_names_only():
    manifest = SkillManifest(
        name="RepoAuditSkill",
        version="1.0.0",
        description="Repository audit metadata",
        category="repo_audit",
        permissions=("read_repo_metadata",),
        allowed_tools=("repo_audit", "secret_scan"),
        required_env=("STRIX_AUDIT_MODE",),
        risk_level="R3",
        entrypoint="saga_fusion.skills.repo_audit:describe",
        enabled=True,
        metadata={"owner": "strix"},
    )

    assert manifest.name == "repoauditskill"
    assert manifest.risk_level == SkillRiskLevel.R3
    assert manifest.public_env_requirements() == ("STRIX_AUDIT_MODE",)
    payload = manifest.to_dict()
    assert payload["required_env"] == ["STRIX_AUDIT_MODE"]
    assert "secret-value" not in str(payload)
    assert SkillManifest.from_dict(payload) == manifest
