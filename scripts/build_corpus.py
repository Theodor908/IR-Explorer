"""
Post-processing helpers for building the IR corpus from extracted PDF sections.
"""

import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ir_explorer.core.pdf_reader import extract_sections

# Mapping of problematic unicode characters to ASCII equivalents
_UNICODE_REPLACEMENTS = {
    # Math symbols
    "\u2211": "sum",       # ∑
    "\u220F": "product",   # ∏
    "\u221A": "sqrt",      # √
    "\u221E": "inf",       # ∞
    "\u2202": "d",         # ∂
    "\u2206": "delta",     # Δ
    "\u2248": "~=",        # ≈
    "\u2260": "!=",        # ≠
    "\u2264": "<=",        # ≤
    "\u2265": ">=",        # ≥
    "\u00D7": "x",         # ×
    "\u00F7": "/",         # ÷
    "\u00B1": "+/-",       # ±
    "\u2229": "intersection",  # ∩
    "\u222A": "union",         # ∪
    "\u2208": "in",            # ∈
    "\u2209": "not in",        # ∉
    "\u2286": "subset",        # ⊆
    "\u2287": "superset",      # ⊇
    "\u2190": "<-",        # ←
    "\u2192": "->",        # →
    "\u2194": "<->",       # ↔
    "\u21D2": "=>",        # ⇒

    # Ligatures
    "\uFB01": "fi",        # fi
    "\uFB02": "fl",        # fl
    "\uFB00": "ff",        # ff
    "\uFB03": "ffi",       # ffi
    "\uFB04": "ffl",       # ffl

    # Smart quotes
    "\u2018": "'",         # '
    "\u2019": "'",         # '
    "\u201C": '"',         # "
    "\u201D": '"',         # "
    "\u201A": ",",         # ‚
    "\u201E": '"',         # „

    # Dashes
    "\u2013": "-",         # en dash
    "\u2014": "--",        # em dash
    "\u2012": "-",         # figure dash
    "\u2015": "--",        # horizontal bar

    # Other common replacements
    "\u2026": "...",       # …
    "\u00A0": " ",         # non-breaking space
    "\u2002": " ",         # en space
    "\u2003": " ",         # em space
    "\u00AD": "",          # soft hyphen
    "\u200B": "",          # zero-width space
    "\u2022": "*",         # bullet •
    "\u00B7": "*",         # middle dot ·
}

# Section titles to filter out (case-insensitive)
_FILTERED_TITLES = [
    "references",
    "bibliography",
    "acknowledgments",
    "acknowledgements",
    "appendix",
    "author info",
    "author information",
    "supplementary",
    "supplementary material",
    "supplementary materials",
    "table of contents",
    "contents",
    "index",
]


def clean_text(text: str) -> str:
    """Replace problematic unicode characters with ASCII equivalents.
    Collapse multiple spaces and strip whitespace."""
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    # Replace any remaining non-ASCII characters with space
    text = re.sub(r"[^\x20-\x7E\n\r\t]", " ", text)
    # Collapse multiple spaces into one
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def merge_short_sections(sections: list[dict], min_length: int = 200) -> list[dict]:
    """Merge adjacent sections shorter than min_length characters.
    If the last section is short after merging, merge it into the previous one."""
    if not sections:
        return []

    merged = [{"title": sections[0]["title"], "text": sections[0]["text"]}]

    for section in sections[1:]:
        if len(merged[-1]["text"]) < min_length:
            # Merge into previous
            merged[-1]["title"] = merged[-1]["title"] + " / " + section["title"]
            merged[-1]["text"] = merged[-1]["text"] + "\n\n" + section["text"]
        else:
            merged.append({"title": section["title"], "text": section["text"]})

    # If last section is still short and there's a previous one, merge into previous
    if len(merged) > 1 and len(merged[-1]["text"]) < min_length:
        merged[-2]["title"] = merged[-2]["title"] + " / " + merged[-1]["title"]
        merged[-2]["text"] = merged[-2]["text"] + "\n\n" + merged[-1]["text"]
        merged.pop()

    return merged


def filter_sections(sections: list[dict]) -> list[dict]:
    """Drop sections with titles matching common non-content sections
    (references, bibliography, acknowledgments, etc.). Case-insensitive."""
    filtered = []
    for section in sections:
        title_lower = section["title"].strip().lower()
        if title_lower not in _FILTERED_TITLES:
            filtered.append(section)
    return filtered


def cap_sections(sections: list[dict], max_docs: int = 6) -> list[dict]:
    """Keep top max_docs sections by text length, preserving their original order."""
    if len(sections) <= max_docs:
        return list(sections)

    # Get indices of top sections by text length
    indexed = [(i, len(s["text"])) for i, s in enumerate(sections)]
    indexed.sort(key=lambda x: x[1], reverse=True)
    top_indices = sorted(idx for idx, _ in indexed[:max_docs])

    return [sections[i] for i in top_indices]


PAPERS = [
    {"file": "1706.03762v7.pdf", "source": "Vaswani et al. (2017)", "max_docs": 6, "split_on": "titles"},
    {"file": "1810.04805v2.pdf", "source": "Devlin et al. (2019)", "max_docs": 6, "split_on": "subtitles"},
    {"file": "Deep Learning Review (Nature) - Yann LeCun, Yoshua Bengio, Geoffrey Hinton.pdf", "source": "LeCun, Bengio & Hinton (2015)", "max_docs": 6, "split_on": "subtitles"},
    {"file": "6572a8eb567d8.pdf", "source": "Keeling (1960)", "max_docs": 5, "split_on": "subtitles"},
    {"file": "Download.pdf", "source": "Hawking (1975)", "max_docs": 5, "split_on": "titles"},
    {"file": "original.pdf", "source": "Darwin (1859)", "max_docs": 6, "split_on": "titles"},
    {"file": "entropy.pdf", "source": "Shannon (1948)", "max_docs": 6, "split_on": "titles"},
    {"file": "Hebb_1949_The_Organization_of_Behavior.pdf", "source": "Hebb (1949)", "max_docs": 5, "split_on": "titles"},
    {"file": "IPCC_AR6_WGI_SPM.pdf", "source": "IPCC AR6 (2021)", "max_docs": 6, "split_on": "titles"},
    {"file": "specrel.pdf", "source": "Einstein (1905)", "max_docs": 6, "split_on": "titles"},
    {"file": "turing.pdf", "source": "Turing (1950)", "max_docs": 6, "split_on": "titles"},
    {"file": "WatsonCrick1953.pdf", "source": "Watson & Crick (1953)", "max_docs": 5, "split_on": "subtitles"},
]


def extract_paper(pdf_dir, config):
    """Extract and post-process sections from a single paper."""
    path = os.path.join(pdf_dir, config["file"])
    if not os.path.exists(path):
        print(f"WARNING: {config['file']} not found, skipping")
        return []

    sections = extract_sections(path, split_on=config.get("split_on", "titles"))

    for sec in sections:
        sec["text"] = clean_text(sec["text"])
        sec["title"] = clean_text(sec["title"])

    sections = filter_sections(sections)
    # Drop sections with very short text (likely OCR garbage or figure captions)
    sections = [s for s in sections if len(s["text"]) >= 300]
    sections = merge_short_sections(sections, min_length=200)
    sections = cap_sections(sections, max_docs=config.get("max_docs", 6))

    return sections


def build_corpus(pdf_dir, existing_corpus_path):
    """Build the full extended corpus JSON."""
    with open(existing_corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    documents = corpus["documents"]
    max_id = max(int(re.search(r"\d+", d).group()) for d in documents)
    next_id = max_id + 1

    for config in PAPERS:
        sections = extract_paper(pdf_dir, config)
        if not sections:
            continue

        print(f"\n{config['source']}: {len(sections)} sections extracted")
        for sec in sections:
            doc_id = f"d{next_id}"
            documents[doc_id] = {
                "title": sec["title"],
                "source": config["source"],
                "text": sec["text"],
            }
            print(f"  {doc_id}: {sec['title'][:60]} ({len(sec['text'])} chars)")
            next_id += 1

    return {"documents": documents}


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    project_root = os.path.join(os.path.dirname(__file__), "..")
    pdf_dir = project_root
    existing_corpus = os.path.join(project_root, "ir_explorer", "assets", "default_corpus.json")
    output_path = os.path.join(project_root, "ir_explorer", "assets", "default_corpus.json")

    corpus = build_corpus(pdf_dir, existing_corpus)
    total_docs = len(corpus["documents"])
    print(f"\n=== Total documents: {total_docs} ===")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    print(f"Written to {output_path}")
