# ir_explorer/tests/test_corpus.py
import pytest
import json
from ir_explorer.core.corpus import Corpus

def test_add_document():
    c = Corpus()
    c.add("d1", "Hello world", title="Test", source="unit")
    assert "d1" in c.docs
    assert c.docs["d1"] == "Hello world"
    assert c.metadata["d1"]["title"] == "Test"

def test_add_duplicate_raises():
    c = Corpus()
    c.add("d1", "Hello world")
    with pytest.raises(ValueError):
        c.add("d1", "Duplicate")

def test_remove_document():
    c = Corpus()
    c.add("d1", "Hello world")
    c.remove("d1")
    assert "d1" not in c.docs
    assert "d1" not in c.metadata

def test_clear():
    c = Corpus()
    c.add("d1", "Hello")
    c.add("d2", "World")
    c.clear()
    assert len(c.docs) == 0
    assert len(c.metadata) == 0

def test_doc_ids_sorted():
    c = Corpus()
    c.add("d3", "Three")
    c.add("d1", "One")
    c.add("d2", "Two")
    assert c.doc_ids() == ["d1", "d2", "d3"]

def test_word_count():
    c = Corpus()
    c.add("d1", "one two three four five")
    assert c.word_count("d1") == 5

def test_next_id():
    c = Corpus()
    assert c.next_id() == "d1"
    c.add("d1", "text")
    c.add("d2", "text")
    assert c.next_id() == "d3"

def test_load_default(tmp_path):
    data = {
        "documents": {
            "d1": {"title": "T1", "source": "S1", "text": "hello world"}
        }
    }
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps(data))
    c = Corpus()
    c.load_from_json(str(path))
    assert "d1" in c.docs
    assert c.metadata["d1"]["title"] == "T1"

def test_load_corpus_with_links(tmp_path):
    data = {
        "documents": {
            "d1": {"title": "T1", "source": "S1", "text": "hello world"},
            "d2": {"title": "T2", "source": "S2", "text": "foo bar"},
        },
        "links": {"d1": ["d2"]}
    }
    path = tmp_path / "corpus_links.json"
    path.write_text(json.dumps(data))
    c = Corpus()
    c.load_from_json(str(path))
    assert c.links == {"d1": ["d2"]}

def test_load_corpus_without_links_defaults_empty(tmp_path):
    data = {
        "documents": {
            "d1": {"title": "T1", "source": "S1", "text": "hello world"},
        }
    }
    path = tmp_path / "corpus_no_links.json"
    path.write_text(json.dumps(data))
    c = Corpus()
    c.load_from_json(str(path))
    assert c.links == {}
