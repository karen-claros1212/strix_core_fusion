from saga_fusion.cyber_knowledge import MitreMapper


def test_maps_required_behaviors_to_attack_ids():
    mapper = MitreMapper()
    mapped = {m.behavior: m for m in mapper.map_behaviors([
        "persistence", "privilege escalation", "defense evasion", "credential access",
        "discovery", "lateral movement", "command and control", "exfiltration", "impact",
    ])}
    assert mapped["persistence"].tactic_id == "TA0003"
    assert mapped["credential access"].technique_id.startswith("T")
    assert mapped["command and control"].tactic_id == "TA0011"
    assert mapped["exfiltration"].defensive_note
    assert len(mapped) == 9
