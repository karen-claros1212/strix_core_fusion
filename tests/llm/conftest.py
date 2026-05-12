import os

# Unit/regression tests must never reach a live OpenAI-compatible gateway from
# developer shell environment variables. Tests that exercise enabled LLM paths
# pass an explicit LLMConfig and stub client/transport.
os.environ["STRIX_LLM_ENABLED"] = "false"
