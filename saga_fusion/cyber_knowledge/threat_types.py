from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class ThreatCategory(str, Enum):
    TROJAN = "trojan"
    SPYWARE = "spyware"
    RANSOMWARE = "ransomware"
    STEALER = "stealer"
    LOADER = "loader"
    DROPPER = "dropper"
    RAT = "rat"
    BOTNET = "botnet"
    ROOTKIT = "rootkit"
    WORM = "worm"
    CRYPTOMINER = "cryptominer"
    BACKDOOR = "backdoor"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ThreatClassification:
    category: ThreatCategory
    confidence: float
    matched_terms: tuple[str, ...] = ()
    defensive_summary: str = ""
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["category"] = self.category.value
        return payload
