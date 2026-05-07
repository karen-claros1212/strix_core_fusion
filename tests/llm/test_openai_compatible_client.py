from saga_fusion.llm.llm_config import LLMConfig
from saga_fusion.llm.openai_compatible_client import OpenAICompatibleClient


def test_openai_client_builds_chat_completion_payload():
    cfg = LLMConfig(enabled=True, base_url='http://local/v1', model='qwen', temperature=0.2, max_output_tokens=99)
    client = OpenAICompatibleClient(cfg)
    messages = [{'role': 'user', 'content': 'hola'}]
    payload = client.build_chat_completion_payload(messages)
    assert payload == {
        'model': 'qwen',
        'messages': messages,
        'temperature': 0.2,
        'max_tokens': 99,
    }


def test_openai_client_handles_timeout():
    cfg = LLMConfig(enabled=True, base_url='http://local/v1', model='qwen')
    def timeout_transport(payload, config):
        raise TimeoutError()
    client = OpenAICompatibleClient(cfg, transport=timeout_transport)
    response = client.chat_completion([{'role': 'user', 'content': 'hola'}])
    assert response.ok is False
    assert response.error == 'timeout'
