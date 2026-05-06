import pytest
import os
import json
from pathlib import Path
from saga_fusion.evidence.evidence_store import SagaEvidenceStore

@pytest.fixture
def store(tmp_path):
    base = tmp_path / "evidence"
    return SagaEvidenceStore(base_dir=str(base))

def test_create_mission(store):
    path = store.create_mission("test_mission")
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(path, "mission.json"))

def test_mission_id_traversal(store):
    with pytest.raises(ValueError):
        store.create_mission("../etc")

def test_append_action(store):
    store.create_mission("test_mission")
    store.append_action("test_mission", {"action": "test"})
    actions_file = Path(store.get_mission_path("test_mission")) / "actions.jsonl"
    assert actions_file.exists()
    content = actions_file.read_text()
    assert "test" in content

def test_list_artifacts(store):
    store.create_mission("test_mission")
    store.write_raw_output("test_mission", "test.txt", "content")
    artifacts = store.list_artifacts("test_mission")
    assert "test.txt" in artifacts
