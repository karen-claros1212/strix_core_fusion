import pytest
import time
from saga_fusion.runtime.process_guard import SagaProcessGuard

@pytest.fixture
def guard():
    return SagaProcessGuard()

def test_run_command_success(guard):
    result = guard.run_command("echo hola", timeout=10)
    assert result["exit_code"] == 0
    assert "hola" in result["stdout"]

def test_run_command_timeout(guard):
    result = guard.run_command("sleep 10", timeout=2)
    assert result["timed_out"] is True
    assert "[TIMEOUT]" in result["stdout"]
