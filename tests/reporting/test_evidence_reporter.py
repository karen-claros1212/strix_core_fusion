import json
from saga_fusion.reporting import EvidenceReporter


def test_evidence_reporter_reads_json_and_redacts(tmp_path):
    path = tmp_path / 'evidence.json'
    path.write_text(json.dumps({'records':[{'event_type':'action','token':'secret'}]}))
    reporter = EvidenceReporter()
    evidence = reporter.load(path)
    assert evidence['records'][0]['token'] == '[REDACTED]'
    summary = reporter.summarize(evidence)
    assert summary['item_count'] == 1
    assert summary['evidence_ref_preserved'] is True


def test_evidence_reporter_handles_missing_file():
    assert EvidenceReporter().load('/missing/evidence.json') == []
