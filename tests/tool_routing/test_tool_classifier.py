from saga_fusion.tool_routing import ToolCategory, ToolClassifier, ToolRisk


def test_classifier_repo_audit_and_secret_scan():
    c = ToolClassifier()
    repo = c.classify({'action':'repo audit dry-run'})
    assert repo['tool_name'] == 'repo_audit'
    assert repo['category'] == ToolCategory.REPO_AUDIT
    assert repo['risk_level'] in {ToolRisk.R2, ToolRisk.R3}
    secret = c.classify({'action':'secret scan repo'})
    assert secret['tool_name'] == 'secret_scan'
    assert secret['category'] == ToolCategory.REPO_AUDIT
    assert secret['risk_level'] == ToolRisk.R2


def test_classifier_cloudops_r4_r5_and_unknown():
    c = ToolClassifier()
    create = c.classify({'action':'create VPS in Hostinger'})
    assert create['category'] == ToolCategory.CLOUDOPS
    assert create['risk_level'] == ToolRisk.R4
    delete = c.classify({'action':'delete server and backups'})
    assert delete['category'] == ToolCategory.CLOUDOPS
    assert delete['risk_level'] == ToolRisk.R5
    unknown = c.classify({'tool_name':'mystery_tool','action':'do thing'})
    assert unknown['category'] == ToolCategory.UNKNOWN
