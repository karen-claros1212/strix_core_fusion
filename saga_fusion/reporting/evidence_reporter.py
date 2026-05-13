from __future__ import annotations

import json
from pathlib import Path

from .report_redactor import ReportRedactor


class EvidenceReporter:
    def __init__(self, redactor: ReportRedactor | None = None):
        self.redactor = redactor or ReportRedactor()

    def load(self, evidence_path):
        path = Path(evidence_path)
        if not path.exists():
            return []
        text = path.read_text(errors='ignore')
        if path.suffix == '.jsonl':
            return [self.redactor.redact(json.loads(line)) for line in text.splitlines() if line.strip()]
        return self.redactor.redact(json.loads(text))

    def summarize(self, evidence) -> dict:
        if isinstance(evidence, dict):
            items = evidence.get('records') or evidence.get('findings') or evidence.get('actions') or []
        else:
            items = evidence or []
        return {'item_count': len(items), 'actions': [item.get('action_type') or item.get('event_type') for item in items if isinstance(item, dict)], 'evidence_ref_preserved': True}

    def build_manifest_ref(self, evidence_path, *, source_phase='unknown', mission_id=None, session_id=None, classification='internal', risk='R0', metadata=None):
        """Return an inert manifest reference for evidence without embedding artifact content."""
        from saga_fusion.manifests import ManifestBuilder
        builder = ManifestBuilder()
        return builder.evidence_ref_from_path(
            evidence_path,
            source_phase=source_phase,
            mission_id=mission_id,
            session_id=session_id,
            classification=classification,
            risk=risk,
            metadata=metadata,
        )

