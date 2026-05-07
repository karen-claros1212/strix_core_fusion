from saga_fusion.llm.brain_service import BrainService
from saga_fusion.llm.llm_config import LLMConfig
from saga_fusion.llm.openai_compatible_client import LLMResponse


class StubClient:
    def chat_completion(self, messages):
        return LLMResponse(ok=True, content='{"action_type":"scan","target":"localhost","arguments":"localhost"}', raw={})


def test_brain_service_does_not_execute_tools():
    cfg = LLMConfig(enabled=True, base_url='http://local/v1', model='qwen')
    service = BrainService(cfg, client=StubClient())
    mission = service.build_mission_from_natural_language('scan localhost')
    assert mission['action_type'] == 'scan'
    assert service.executed_tools is False
