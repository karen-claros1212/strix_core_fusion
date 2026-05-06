import pytest
import json
from pathlib import Path
from saga_fusion.evidence.evidence_store import SagaEvidenceStore

@pytest.fixture
def store(tmp_path):
    base = tmp_path / "evidence"
    return SagaEvidenceStore(base_dir=str(base))

def test_secret_redaction_in_actions(store):
    store.create_mission("test_mission")
    store.append_action("test_mission", {"command": "export API_KEY=secret123"})
    actions_file = Path(store.get_mission_path("test_mission")) / "actions.jsonl"
    content = json.loads(actions_file.read_text())
    assert "secret123" not in content["command"]
    assert "[REDACTED]" in content["command"]

def test_secret_redaction_in_commands(store):
    store.create_mission("test_mission")
    store.append_command("test_mission", {"cmd": "curl -H 'Authorization: Bearer token123'"})
    commands_file = Path(store.get_mission_path("test_mission")) / "commands.jsonl"
    content = json.loads(commands_file.read_text())
    assert "token123" not in content["cmd"]
    assert "[REDACTED]" in content["cmd"]
