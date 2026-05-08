from saga_fusion.tool_routing import ToolRegistry


def test_registry_registers_known_tools_and_unknown_missing():
    registry = ToolRegistry()
    names = {tool.name for tool in registry.list_tools()}
    for name in ['status','repo_audit','secret_scan','dependency_audit','config_audit','docker_audit','report_generate','cloudops_plan','dns_plan','firewall_plan','backup_plan','llm_analyze','evidence_list']:
        assert name in names
        assert registry.exists(name)
    assert not registry.exists('rm_rf')


def test_registry_metadata_complete():
    for tool in ToolRegistry().list_tools():
        assert tool.name
        assert tool.category
        assert tool.default_risk
        assert isinstance(tool.requires_sandbox, bool)
        assert isinstance(tool.requires_approval, bool)
        assert tool.allowed_modes
        assert tool.description
