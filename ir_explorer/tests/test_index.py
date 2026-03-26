# ir_explorer/tests/test_index.py
import pytest
from ir_explorer.core.index import InvertedIndex

SAMPLE_CORPUS = {
    "d1": "the quantum universe is large and expanding",
    "d2": "quantum mechanics explains the atomic realm",
    "d3": "the universe contains many galaxies",
}

def test_build_creates_index():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    assert len(idx.index) > 0

def test_postings_list():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    postings = idx.get_postings("quantum")
    assert "d1" in postings
    assert "d2" in postings

def test_unknown_term_empty():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    assert idx.get_postings("nonexistent") == []

def test_df():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    assert idx.df("quantum") == 2
    assert idx.df("nonexistent") == 0

def test_vocabulary():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    vocab = idx.vocabulary()
    assert "quantum" in vocab
    assert "the" not in vocab
    assert "is" not in vocab

def test_stats():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    stats = idx.stats()
    assert stats["num_terms"] > 0
    assert stats["num_documents"] == 3
    assert stats["total_postings"] > 0
    assert "avg_postings_per_term" in stats
    assert "max_df_term" in stats

def test_term_frequencies():
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS)
    tf = idx.term_freq("d1")
    assert isinstance(tf, dict)
    assert tf.get("quantum", 0) >= 1

from ir_explorer.core.preprocessing import PipelineConfig

def test_build_with_stemming():
    config = PipelineConfig(apply_stemming=True)
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS, config=config)
    vocab = idx.vocabulary()
    assert "expand" in vocab
    assert "expanding" not in vocab

def test_build_without_stopword_removal():
    config = PipelineConfig(remove_stopwords=False)
    idx = InvertedIndex()
    idx.build(SAMPLE_CORPUS, config=config)
    vocab = idx.vocabulary()
    assert "the" in vocab
    assert "is" in vocab

def test_build_default_config_matches_original():
    idx1 = InvertedIndex()
    idx1.build(SAMPLE_CORPUS)
    idx2 = InvertedIndex()
    idx2.build(SAMPLE_CORPUS, config=PipelineConfig())
    assert set(idx1.vocabulary()) == set(idx2.vocabulary())
