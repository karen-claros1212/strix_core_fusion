import pytest
from saga_fusion.runtime.runtime_safety import SagaRuntimeSafety

@pytest.fixture
def safety():
    return SagaRuntimeSafety(workspace_root="/workspace")

def test_validate_working_directory(safety):
    assert safety.validate_working_directory("/workspace/test") is True
    assert safety.validate_working_directory("/other/test") is False

def test_validate_file_operation(safety):
    assert safety.validate_file_operation("/workspace/file.txt") is True
    assert safety.validate_file_operation("../etc/passwd") is False
    assert safety.validate_file_operation("~/.ssh/id_rsa") is False

def test_classify_runtime_action(safety):
    assert safety.classify_runtime_action("rm -rf /") == "DANGEROUS_DELETE"
    assert safety.classify_runtime_action("echo hola") == "SAFE"
