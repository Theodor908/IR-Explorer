# ir_explorer/tests/test_retrieval.py
import pytest
from ir_explorer.core.index import InvertedIndex
from ir_explorer.core.retrieval import boolean_search, tfidf_rank

CORPUS = {
    "d1": "parallel universes multiverse inflation quantum",
    "d2": "quantum mechanics wave function decoherence",
    "d3": "inflation cosmological expansion universe big bang",
    "d4": "multiverse hierarchy levels parallel universes",
}

@pytest.fixture
def idx():
    i = InvertedIndex()
    i.build(CORPUS)
    return i

def test_boolean_and(idx):
    result = boolean_search("quantum AND inflation", idx)
    assert "d1" in result
    assert "d2" not in result

def test_boolean_or(idx):
    result = boolean_search("quantum OR inflation", idx)
    assert "d1" in result
    assert "d2" in result
    assert "d3" in result

def test_boolean_not(idx):
    result = boolean_search("quantum AND NOT decoherence", idx)
    assert "d1" in result
    assert "d2" not in result

def test_boolean_single_term(idx):
    result = boolean_search("multiverse", idx)
    assert "d1" in result
    assert "d4" in result

def test_tfidf_rank_returns_sorted(idx):
    results = tfidf_rank("quantum mechanics", idx, CORPUS)
    assert len(results) > 0
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)

def test_tfidf_rank_top_result(idx):
    results = tfidf_rank("decoherence wave function", idx, CORPUS)
    assert results[0][0] == "d2"

def test_tfidf_rank_empty_query(idx):
    results = tfidf_rank("", idx, CORPUS)
    assert all(s == 0.0 for _, s in results)

from ir_explorer.core.preprocessing import PipelineConfig

def test_tfidf_rank_with_stemming():
    config = PipelineConfig(apply_stemming=True)
    i = InvertedIndex()
    i.build(CORPUS, config=config)
    results = tfidf_rank("universes", i, CORPUS, config=config)
    assert len(results) > 0
    assert results[0][1] > 0.0

def test_boolean_search_with_config():
    config = PipelineConfig(apply_stemming=True)
    i = InvertedIndex()
    i.build(CORPUS, config=config)
    result = boolean_search("quantum", i, config=config)
    assert len(result) > 0
