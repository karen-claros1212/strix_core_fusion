import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .llm_config import LLMConfig


@dataclass
class LLMResponse:
    ok: bool
    content: str = ""
    raw: dict | None = None
    error: str = ""
    status_code: int | None = None


class OpenAICompatibleClient:
    def __init__(self, config: LLMConfig, transport=None):
        self.config = config
        self.transport = transport

    def build_chat_completion_payload(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_output_tokens,
        }

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key and self.config.api_key != "local":
            headers["Authorization"] = "Bearer [REDACTED]"
        return headers

    def _real_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key and self.config.api_key != "local":
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def chat_completion(self, messages: list[dict[str, str]]) -> LLMResponse:
        payload = self.build_chat_completion_payload(messages)
        if self.transport is not None:
            try:
                data = self.transport(payload, self.config)
                return self._parse_response(data)
            except TimeoutError:
                return LLMResponse(ok=False, error="timeout")
            except Exception as exc:
                return LLMResponse(ok=False, error=f"transport_error:{type(exc).__name__}")

        if not self.config.base_url:
            return LLMResponse(ok=False, error="missing_base_url")

        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.base_url}/chat/completions",
            data=body,
            headers=self._real_headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
                parsed = self._parse_response(raw)
                parsed.status_code = response.status
                return parsed
        except (TimeoutError, socket.timeout):
            return LLMResponse(ok=False, error="timeout")
        except urllib.error.HTTPError as exc:
            return LLMResponse(ok=False, error="http_error", status_code=exc.code)
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, TimeoutError) or isinstance(reason, socket.timeout):
                return LLMResponse(ok=False, error="timeout")
            return LLMResponse(ok=False, error="endpoint_unavailable")
        except Exception as exc:
            return LLMResponse(ok=False, error=f"client_error:{type(exc).__name__}")

    def _parse_response(self, raw: dict) -> LLMResponse:
        try:
            content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
            return LLMResponse(ok=bool(content), content=content, raw=raw, error="" if content else "empty_response")
        except Exception:
            return LLMResponse(ok=False, raw=raw if isinstance(raw, dict) else None, error="invalid_response")
