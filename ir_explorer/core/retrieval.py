"""Boolean search and TF-IDF ranked retrieval."""

import math
import re
from collections import Counter
import numpy as np

from ir_explorer.core.preprocessing import PipelineConfig, configurable_pipeline


def boolean_search(query, index, config=None):
    """Evaluate a Boolean query (supports AND, OR, AND NOT).
    Returns sorted list of matching doc_ids."""
    if config is None:
        config = PipelineConfig()
    query = query.strip()
    if not query:
        return []

    all_docs = set()
    for postings in index.index.values():
        all_docs.update(postings)

    if " AND NOT " in query.upper():
        parts = re.split(r"\s+AND\s+NOT\s+", query, flags=re.IGNORECASE)
        left = _resolve_term(parts[0].strip().lower(), index, config)
        right = _resolve_term(parts[1].strip().lower(), index, config)
        result = left - right
    elif " AND " in query.upper():
        parts = re.split(r"\s+AND\s+", query, flags=re.IGNORECASE)
        sets = [_resolve_term(p.strip().lower(), index, config) for p in parts]
        result = sets[0]
        for s in sets[1:]:
            result &= s
    elif " OR " in query.upper():
        parts = re.split(r"\s+OR\s+", query, flags=re.IGNORECASE)
        result = set()
        for p in parts:
            result |= _resolve_term(p.strip().lower(), index, config)
    else:
        result = _resolve_term(query.lower(), index, config)

    sort_key = lambda x: int(x[1:]) if x[1:].isdigit() else 0
    return sorted(result, key=sort_key)


def _resolve_term(term, index, config=None):
    if config is None:
        config = PipelineConfig()
    tokens = configurable_pipeline(term, config)
    if not tokens:
        return set()
    sets = [set(index.get_postings(t)) for t in tokens]
    result = sets[0]
    for s in sets[1:]:
        result &= s
    return result


def tfidf_rank(query, index, corpus_docs, config=None):
    """Rank documents by TF-IDF cosine similarity to query."""
    if config is None:
        config = PipelineConfig()
    q_tokens = configurable_pipeline(query, config)
    if not q_tokens:
        sort_key = lambda x: int(x[1:]) if x[1:].isdigit() else 0
        return [(d, 0.0) for d in sorted(corpus_docs.keys(), key=sort_key)]

    vocab = index.vocabulary()
    if not vocab:
        return []
    term_to_i = {t: i for i, t in enumerate(vocab)}
    N = len(corpus_docs)

    def idf(term):
        d = index.df(term)
        if d == 0:
            return 0.0
        if config.idf_scheme == "smoothed":
            return math.log((N + 1) / (d + 1)) + 1
        return math.log(N / d)

    def compute_tf(freq):
        if config.tf_scheme == "raw":
            return freq
        elif config.tf_scheme == "boolean":
            return 1 if freq > 0 else 0
        return 1 + math.log(freq) if freq > 0 else 0

    def tfidf_vec(tf_dict):
        vec = np.zeros(len(vocab))
        for term, freq in tf_dict.items():
            if term in term_to_i:
                vec[term_to_i[term]] = compute_tf(freq) * idf(term)
        return vec

    q_tf = Counter(q_tokens)
    q_vec = tfidf_vec(q_tf)

    results = []
    for doc_id in corpus_docs:
        d_tf = index.term_freq(doc_id)
        d_vec = tfidf_vec(d_tf)
        na = np.linalg.norm(q_vec)
        nb = np.linalg.norm(d_vec)
        if na == 0 or nb == 0:
            score = 0.0
        else:
            score = float(np.dot(q_vec, d_vec) / (na * nb))
        results.append((doc_id, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
