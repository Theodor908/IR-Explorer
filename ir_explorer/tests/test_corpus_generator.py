import pytest
from ir_explorer.core.corpus_generator import generate_corpus

def test_generate_returns_correct_format():
    result = generate_corpus(num_docs=5, avg_length=50, vocab_overlap=0.5, seed=42)
    assert "documents" in result
    assert len(result["documents"]) == 5

def test_generate_doc_structure():
    result = generate_corpus(num_docs=3, avg_length=30, seed=1)
    for doc_id, doc in result["documents"].items():
        assert "text" in doc
        assert "title" in doc
        assert "source" in doc
        assert doc["source"] == "Generator"
        assert len(doc["text"].split()) >= 10

def test_generate_reproducible():
    r1 = generate_corpus(num_docs=5, avg_length=50, seed=42)
    r2 = generate_corpus(num_docs=5, avg_length=50, seed=42)
    for doc_id in r1["documents"]:
        assert r1["documents"][doc_id]["text"] == r2["documents"][doc_id]["text"]

def test_generate_different_seeds_differ():
    r1 = generate_corpus(num_docs=5, avg_length=50, seed=1)
    r2 = generate_corpus(num_docs=5, avg_length=50, seed=2)
    texts1 = [d["text"] for d in r1["documents"].values()]
    texts2 = [d["text"] for d in r2["documents"].values()]
    assert texts1 != texts2

def test_generate_min_doc_length():
    result = generate_corpus(num_docs=3, avg_length=5, seed=42)
    for doc in result["documents"].values():
        assert len(doc["text"].split()) >= 10

def test_generate_high_overlap():
    result = generate_corpus(num_docs=5, avg_length=50, vocab_overlap=1.0, seed=42)
    assert len(result["documents"]) == 5

def test_generate_low_overlap():
    result = generate_corpus(num_docs=5, avg_length=50, vocab_overlap=0.0, seed=42)
    assert len(result["documents"]) == 5
