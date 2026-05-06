import os
import json
import uuid
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

from saga_fusion.audit_logger import SagaAuditLogger

class SagaEvidenceStore:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path("evidence/missions")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = SagaAuditLogger()

    def _sanitize_path(self, name: str) -> str:
        # Remove potentially dangerous characters
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def create_mission(self, mission_id: str, metadata: Dict[str, Any] = None) -> str:
        if ".." in mission_id:
            raise ValueError(f"Invalid mission_id: {mission_id}")
        
        mission_path = self.base_dir / mission_id
        mission_path.mkdir(parents=True, exist_ok=True)
        
        (mission_path / "mission.json").write_text(json.dumps({
            "mission_id": mission_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }, indent=2))
        
        (mission_path / "actions.jsonl").touch()
        (mission_path / "commands.jsonl").touch()
        (mission_path / "findings.jsonl").touch()
        (mission_path / "artifacts_index.json").write_text(json.dumps({}))
        
        (mission_path / "raw_outputs").mkdir(exist_ok=True)
        (mission_path / "reports").mkdir(exist_ok=True)
        
        return str(mission_path)

    def append_action(self, mission_id: str, action_record: Dict[str, Any]):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": str(uuid.uuid4()),
            "source": "saga_fusion",
            **action_record
        }
        record = self.logger.redact_secrets(record)
        path = self.base_dir / mission_id / "actions.jsonl"
        
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def append_command(self, mission_id: str, command_record: Dict[str, Any]):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": str(uuid.uuid4()),
            "source": "saga_fusion",
            **command_record
        }
        record = self.logger.redact_secrets(record)
        path = self.base_dir / mission_id / "commands.jsonl"
        
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def append_finding(self, mission_id: str, finding: Dict[str, Any]):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": str(uuid.uuid4()),
            "source": "saga_fusion",
            **finding
        }
        record = self.logger.redact_secrets(record)
        path = self.base_dir / mission_id / "findings.jsonl"
        
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def write_raw_output(self, mission_id: str, artifact_name: str, content: str):
        safe_name = self._sanitize_path(artifact_name)
        path = self.base_dir / mission_id / "raw_outputs" / safe_name
        path.write_text(content)
        
        # Update index
        index_path = self.base_dir / mission_id / "artifacts_index.json"
        index = json.loads(index_path.read_text()) if index_path.exists() else {}
        index[safe_name] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "size": len(content)
        }
        index_path.write_text(json.dumps(index, indent=2))

    def write_report(self, mission_id: str, report_name: str, content: str):
        safe_name = self._sanitize_path(report_name) + ".md"
        path = self.base_dir / mission_id / "reports" / safe_name
        path.write_text(content)

    def get_mission_path(self, mission_id: str) -> str:
        return str(self.base_dir / mission_id)

    def list_artifacts(self, mission_id: str) -> List[str]:
        path = self.base_dir / mission_id / "artifacts_index.json"
        if path.exists():
            return list(json.loads(path.read_text()).keys())
        return []
