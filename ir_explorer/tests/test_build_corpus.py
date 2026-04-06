import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.build_corpus import clean_text, merge_short_sections, filter_sections, cap_sections


def test_clean_text_replaces_unicode():
    text = "the sum \u2211 of values \ufb01nd"
    cleaned = clean_text(text)
    assert "\u2211" not in cleaned
    assert "\ufb01" not in cleaned
    assert "find" in cleaned or "fi" in cleaned


def test_clean_text_preserves_normal():
    assert clean_text("hello world") == "hello world"


def test_merge_short_sections():
    sections = [
        {"title": "A", "text": "short"},
        {"title": "B", "text": "also short"},
        {"title": "C", "text": "x" * 250},
    ]
    merged = merge_short_sections(sections, min_length=200)
    assert len(merged) <= 2
    assert any(len(s["text"]) >= 200 for s in merged)


def test_merge_short_sections_all_long():
    sections = [
        {"title": "A", "text": "x" * 300},
        {"title": "B", "text": "y" * 300},
    ]
    merged = merge_short_sections(sections, min_length=200)
    assert len(merged) == 2


def test_filter_sections_drops_references():
    sections = [
        {"title": "Introduction", "text": "x" * 300},
        {"title": "References", "text": "x" * 300},
        {"title": "Acknowledgments", "text": "x" * 300},
        {"title": "Results", "text": "x" * 300},
    ]
    filtered = filter_sections(sections)
    titles = [s["title"] for s in filtered]
    assert "References" not in titles
    assert "Acknowledgments" not in titles
    assert "Introduction" in titles
    assert "Results" in titles


def test_cap_sections():
    sections = [{"title": f"S{i}", "text": "x" * (100 + i * 50)} for i in range(10)]
    capped = cap_sections(sections, max_docs=5)
    assert len(capped) == 5
    # should keep the longest sections in their original order
    lengths = [len(s["text"]) for s in capped]
    assert sorted(lengths, reverse=True) == sorted(lengths, reverse=True)
    # verify these are indeed the top 5 longest
    all_lengths = sorted([len(s["text"]) for s in sections], reverse=True)
    assert sorted(lengths, reverse=True) == all_lengths[:5]
    # verify original order is preserved (ascending in this case)
    assert lengths == sorted(lengths)
