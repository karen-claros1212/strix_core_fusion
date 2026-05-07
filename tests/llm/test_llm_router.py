from saga_fusion.llm.llm_config import LLMConfig
from saga_fusion.llm.llm_router import LLMRouter


class FailingBrain:
    def build_mission_from_natural_language(self, text, context=None):
        raise RuntimeError('boom')


def test_llm_router_fallback_when_disabled():
    router = LLMRouter(config=LLMConfig(enabled=False))
    mission = router.build_mission_from_natural_language('status services')
    assert mission['source'] == 'fallback'
    assert mission['action_type'] == 'status'
    assert mission['target'] == 'services'


def test_llm_router_fallback_when_llm_fails():
    cfg = LLMConfig(enabled=True, base_url='http://local/v1', model='qwen')
    router = LLMRouter(config=cfg, brain_service=FailingBrain())
    mission = router.build_mission_from_natural_language('scan localhost')
    assert mission['source'] == 'fallback'
    assert mission['action_type'] == 'scan'
    assert mission['llm_error'] == 'RuntimeError'
