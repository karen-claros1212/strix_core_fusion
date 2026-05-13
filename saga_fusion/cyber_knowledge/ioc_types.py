from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any
import re


class IoCType(str, Enum):
    HASH = "hash"
    DOMAIN = "domain"
    IP = "ip"
    URL = "url"
    FILE_PATH = "file_path"
    PROCESS_NAME = "process_name"


@dataclass(frozen=True)
class IoC:
    value: str
    ioc_type: IoCType
    source: str = "reported"
    confidence: float = 0.5
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        value = str(self.value or "").strip()
        if not value:
            raise ValueError("IoC value is required")
        object.__setattr__(self, "value", self._sanitize(value))
        object.__setattr__(self, "confidence", max(0.0, min(1.0, float(self.confidence))))

    @staticmethod
    def _sanitize(value: str) -> str:
        # Metadata-safe normalization only; no fetching, resolving, or execution.
        return value.replace("\x00", "").strip()[:300]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["ioc_type"] = self.ioc_type.value
        return payload


_HASH_RE = re.compile(r"^[A-Fa-f0-9]{32}$|^[A-Fa-f0-9]{40}$|^[A-Fa-f0-9]{64}$")
_IP_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def infer_ioc_type(value: str) -> IoCType:
    text = str(value or "").strip()
    low = text.lower()
    if _HASH_RE.match(text):
        return IoCType.HASH
    if low.startswith(("http://", "https://")):
        return IoCType.URL
    if _IP_RE.match(text):
        return IoCType.IP
    if "/" in text or "\\" in text:
        return IoCType.FILE_PATH
    if "." in text and " " not in text:
        return IoCType.DOMAIN
    return IoCType.PROCESS_NAME
