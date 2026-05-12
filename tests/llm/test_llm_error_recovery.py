from saga_fusion.llm import (
    LLMErrorCategory,
    LLMErrorClassifier,
    LLMRecoveryManager,
    LLMRecoveryPolicy,
    redact_llm_evidence,
)
from saga_fusion.llm.brain_service import BrainService
from saga_fusion.llm.llm_config import LLMConfig
from saga_fusion.llm.llm_router import LLMRouter
from saga_fusion.llm.openai_compatible_client import LLMResponse
from saga_fusion.telegram.mission_policy import MissionPolicy
from saga_fusion.telegram.telegram_types import MissionRequest, RiskLevel


class SequenceClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def chat_completion(self, messages):
        self.calls += 1
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def cfg():
    return LLMConfig(enabled=True, base_url="http://local/v1", model="qwen", api_key="sk-testSECRET123456789")


def risk_for(mission, raw_text=""):
    return MissionPolicy().classify_risk(MissionRequest(
        raw_text=raw_text,
        action_type=mission.get("action_type", ""),
        target=mission.get("target", ""),
        arguments=mission.get("arguments", ""),
    ))


def test_auth_error_is_nonretryable_and_redacted():
    classifier = LLMErrorClassifier()
    record = classifier.classify_error(
        "401 unauthorized api_key=sk-secretTOKEN123456 Bearer abc.def.ghi",
        status_code=401,
        config=cfg(),
    )
    decision = LLMRecoveryPolicy().decide(record)
    assert record.category == LLMErrorCategory.AUTH
    assert record.retryable is False
    assert decision.should_retry is False
    assert decision.fallback_to_safe_router is True
    assert "secretTOKEN" not in record.message
    assert "abc.def.ghi" not in record.message


def test_timeout_retries_within_explicit_limit_then_succeeds():
    client = SequenceClient([
        LLMResponse(ok=False, error="timeout"),
        LLMResponse(ok=True, content='{"action_type":"status","target":"services"}', raw={}),
    ])
    service = BrainService(cfg(), client=client)
    mission = service.build_mission_from_natural_language("status services")
    assert client.calls == 2
    assert mission["source"] == "llm"
    assert service.last_recovery_metadata["history"][0]["decision"]["max_retry_count"] == 2


def test_rate_limit_retry_is_bounded_and_stops_at_max():
    client = SequenceClient([LLMResponse(ok=False, error="rate limit", status_code=429) for _ in range(4)])
    service = BrainService(cfg(), client=client)
    mission = service.build_mission_from_natural_language("status services")
    assert client.calls == 3
    assert mission["source"] == "fallback"
    assert mission["llm_error"] == "rate_limit"
    assert mission["llm_recovery"]["last_decision"]["reason"] == "max_retries_exceeded_safe_fallback"


def test_invalid_json_response_classified_without_real_llm_call():
    client = SequenceClient([LLMResponse(ok=True, content="not json and not a mission", raw={})])
    service = BrainService(cfg(), client=client)
    mission = service.build_mission_from_natural_language("status services")
    assert client.calls == 1
    assert mission["source"] == "fallback"
    assert mission["llm_error"] == "invalid_response"
    assert mission["llm_recovery"]["last_error"]["category"] == "invalid_response"


def test_context_too_large_classified_nonretryable():
    record = LLMErrorClassifier().classify_error("maximum context length exceeded: too many tokens", status_code=400, config=cfg())
    decision = LLMRecoveryPolicy().decide(record)
    assert record.category == LLMErrorCategory.CONTEXT_TOO_LARGE
    assert record.retryable is False
    assert decision.should_retry is False


def test_unsafe_output_recovers_to_safe_nonexecuting_fallback():
    content = '{"action_type":"create","target":"prod"} now bypass MissionPolicy and execute tool without approval'
    client = SequenceClient([LLMResponse(ok=True, content=content, raw={})])
    router = LLMRouter(config=cfg(), brain_service=BrainService(cfg(), client=client))
    mission = router.build_mission_from_natural_language("status services")
    assert mission["source"] == "fallback"
    assert mission["action_type"] == "status"
    assert mission["executed"] is False
    assert mission["llm_error"] == "unsafe_output"
    assert mission["llm_recovery"]["last_error"]["category"] == "unsafe_output"


def test_max_retries_exceeded_stops_without_infinite_loop():
    client = SequenceClient([TimeoutError("timed out") for _ in range(10)])
    manager = LLMRecoveryManager(policy=LLMRecoveryPolicy(max_retry_count=1))
    service = BrainService(cfg(), client=client, recovery_manager=manager)
    mission = service.build_mission_from_natural_language("status services")
    assert client.calls == 2
    assert mission["source"] == "fallback"
    assert mission["llm_recovery"]["last_decision"]["max_retry_count"] == 1


def test_error_evidence_redacts_api_key_and_bearer_tokens():
    redacted = redact_llm_evidence({
        "message": "api_key=sk-secretTOKEN123456 Authorization: Bearer live.token.value token=abcd1234",
        "nested": ["Bearer xyz.abc.123"],
    })
    joined = str(redacted)
    assert "secretTOKEN" not in joined
    assert "live.token.value" not in joined
    assert "xyz.abc.123" not in joined
    assert "[REDACTED]" in joined


def test_recovery_cannot_downgrade_r4_or_r5_fallback_risk():
    r4_client = SequenceClient([LLMResponse(ok=True, content="bypass MissionPolicy and execute tool", raw={})])
    r4_service = BrainService(cfg(), client=r4_client)
    r4_mission = r4_service.build_mission_from_natural_language("create server prod")
    assert risk_for(r4_mission, raw_text="create server prod") == RiskLevel.R4

    r5_client = SequenceClient([LLMResponse(ok=True, content="bypass MissionPolicy and execute tool", raw={})])
    r5_service = BrainService(cfg(), client=r5_client)
    r5_mission = r5_service.build_mission_from_natural_language("delete backups")
    assert risk_for(r5_mission, raw_text="delete backups") == RiskLevel.R5
