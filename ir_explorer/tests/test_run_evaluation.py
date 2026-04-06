import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.run_evaluation import evaluate_query, run_all_queries, format_report_table


def _make_mini_corpus():
    from ir_explorer.core.corpus import Corpus
    from ir_explorer.core.index import InvertedIndex
    from ir_explorer.core.preprocessing import PipelineConfig

    corpus = Corpus()
    corpus.add("d1", "neural network deep learning training", title="ML Intro")
    corpus.add("d2", "quantum mechanics wavefunction observation", title="QM Intro")
    corpus.add("d3", "deep learning convolutional neural network", title="CNN")

    config = PipelineConfig(remove_stopwords=True, apply_stemming=False,
                            tf_scheme="log", idf_scheme="standard")
    index = InvertedIndex()
    index.build(corpus.docs, config)
    return corpus, index, config


def test_evaluate_query():
    corpus, index, config = _make_mini_corpus()
    result = evaluate_query("neural network", {"d1", "d3"}, index, corpus.docs, config)
    assert "p5" in result
    assert "p10" in result
    assert "ap" in result
    assert 0.0 <= result["ap"] <= 1.0


def test_run_all_queries():
    corpus, index, config = _make_mini_corpus()
    queries = [
        {"id": "q1", "text": "neural network", "relevant": ["d1", "d3"]},
        {"id": "q2", "text": "quantum mechanics", "relevant": ["d2"]},
    ]
    results, map_score = run_all_queries(queries, index, corpus.docs, config)
    assert len(results) == 2
    assert 0.0 <= map_score <= 1.0


def test_format_report_table():
    rows = [
        {"id": "q1", "text": "test query", "p5": 0.8, "p10": 0.5, "ap": 0.65,
         "num_retrieved": 3, "num_relevant": 2},
    ]
    table = format_report_table(rows, map_score=0.65, config_name="Baseline")
    assert "Baseline" in table
    assert "MAP" in table
