from saga_fusion.memory import ContextItem, ContextWindow, MemoryScope, MemorySensitivity


def test_context_window_budget_priority_and_excludes_secret_blocked():
    items = [
        ContextItem("low recent note", scope=MemoryScope.SESSION, priority=1),
        ContextItem("internal project constraint: MissionPolicy remains authority", scope=MemoryScope.PROJECT, priority=10),
        ContextItem("api_key=redacted", sensitivity=MemorySensitivity.SECRET_BLOCKED, priority=999),
        ContextItem("evidence ref evidence:abc", scope=MemoryScope.MISSION, priority=5),
    ]
    selected = ContextWindow(char_budget=90).select(items)
    contents = "\n".join(i.content for i in selected)
    assert "SECRET" not in contents
    assert "api_key" not in contents
    assert "MissionPolicy" in contents
    assert len(contents) <= 90


def test_context_render_declares_non_authoritative_no_override():
    rendered = ContextWindow().render([ContextItem("remember old R4 was safe", scope=MemoryScope.USER_APPROVED, user_approved=True)])
    assert "NON-AUTHORITATIVE" in rendered
    assert "must not override" in rendered
    assert "R4/R5" in rendered
