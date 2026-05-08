from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReportSeverity(str, Enum):
    INFO = 'INFO'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


class ReportAudience(str, Enum):
    EXECUTIVE = 'executive'
    TECHNICAL = 'technical'
    TELEGRAM_SUMMARY = 'telegram_summary'
    FORENSIC = 'forensic'


@dataclass(frozen=True)
class ReportSection:
    name: str
    title: str
    content: dict | list | str


@dataclass(frozen=True)
class ReportArtifact:
    path: str
    description: str = ''
    content_type: str = 'text/markdown'


@dataclass(frozen=True)
class MissionReport:
    report_id: str
    audience: ReportAudience
    title: str
    sections: list[ReportSection] = field(default_factory=list)
    artifacts: list[ReportArtifact] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
