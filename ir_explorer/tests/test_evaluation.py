import pytest
from ir_explorer.core.evaluation import (
    precision_at_k, recall_at_k, average_precision,
    mean_average_precision, precision_recall_curve,
)

RELEVANT = {"d1", "d3", "d5"}
RETRIEVED = ["d1", "d2", "d3", "d4", "d5"]

def test_precision_at_k():
    assert precision_at_k(RETRIEVED, RELEVANT, 1) == 1.0
    assert precision_at_k(RETRIEVED, RELEVANT, 2) == 0.5
    assert precision_at_k(RETRIEVED, RELEVANT, 5) == 3 / 5

def test_recall_at_k():
    assert recall_at_k(RETRIEVED, RELEVANT, 1) == pytest.approx(1 / 3)
    assert recall_at_k(RETRIEVED, RELEVANT, 3) == pytest.approx(2 / 3)
    assert recall_at_k(RETRIEVED, RELEVANT, 5) == 1.0

def test_average_precision():
    ap = average_precision(RETRIEVED, RELEVANT)
    assert ap == pytest.approx((1.0 + 2/3 + 3/5) / 3)

def test_average_precision_no_relevant():
    assert average_precision(RETRIEVED, set()) == 0.0

def test_mean_average_precision():
    queries = [
        (["d1", "d2", "d3"], {"d1", "d3"}),
        (["d2", "d1"], {"d1"}),
    ]
    m = mean_average_precision(queries)
    assert 0.0 < m <= 1.0

def test_precision_recall_curve():
    points = precision_recall_curve(RETRIEVED, RELEVANT)
    assert len(points) == len(RETRIEVED)
    for recall, precision in points:
        assert 0.0 <= recall <= 1.0
        assert 0.0 <= precision <= 1.0

def test_precision_at_k_empty():
    assert precision_at_k([], RELEVANT, 5) == 0.0

def test_recall_at_k_empty_relevant():
    assert recall_at_k(RETRIEVED, set(), 5) == 0.0
