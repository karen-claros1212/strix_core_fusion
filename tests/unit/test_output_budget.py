import pytest
from saga_fusion.runtime.output_budget import SagaOutputBudget

@pytest.fixture
def budget():
    return SagaOutputBudget(max_chars=100, preserve_head=20, preserve_tail=20)

def test_short_output_no_truncation(budget):
    text = "A" * 50
    assert budget.truncate_output(text) == text

def test_long_output_truncation(budget):
    text = "A" * 200
    result = budget.truncate_output(text)
    assert "[TRUNCATED" in result
    assert len(result) < len(text)
    assert result.startswith("A" * 20)
    assert result.endswith("A" * 20)
