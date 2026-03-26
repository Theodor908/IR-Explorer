"""Synthetic IR corpus generator."""

import random

_SHARED_POOL = [
    "information", "retrieval", "document", "query", "search", "index", "term",
    "frequency", "corpus", "text", "relevance", "ranking", "model", "system",
    "collection", "token", "word", "match", "score", "result", "user", "data",
    "content", "keyword", "analysis", "process", "method", "approach", "set",
    "vector", "weight", "similarity", "feature", "field", "value", "list",
    "type", "item", "record", "length",
]

_TOPIC_POOLS = {
    "indexing": [
        "inverted", "postings", "list", "block", "merge", "compression",
        "bitmap", "positional", "skip", "pointer", "dictionary", "hash",
        "trie", "btree", "segment", "shard", "partition", "cache", "buffer",
        "disk", "memory", "flush", "update", "delete", "insert", "build",
        "rebuild", "incremental", "batch", "crawl", "parse", "tokenize",
        "normalize", "stem", "stopword", "filter", "pipeline", "worker",
        "thread", "parallel", "distributed", "cluster", "node", "replica",
        "primary", "secondary", "backup", "restore", "checkpoint",
    ],
    "ranking": [
        "bm25", "tfidf", "okapi", "lm", "smoothing", "dirichlet", "jelinek",
        "mercer", "language", "probability", "prior", "posterior", "bayesian",
        "cosine", "dot", "product", "norm", "idf", "tf", "pagerank",
        "authority", "hub", "hyperlink", "citation", "boost", "field",
        "title", "body", "anchor", "url", "freshness", "quality", "spam",
        "click", "feedback", "learning", "supervised", "lambdamart",
        "gradient", "boosting", "forest", "regression", "linear", "neural",
        "dense", "sparse", "hybrid",
    ],
    "web": [
        "crawler", "spider", "robot", "sitemap", "url", "link", "anchor",
        "href", "domain", "subdomain", "protocol", "http", "https", "html",
        "javascript", "css", "render", "headless", "browser", "fetch",
        "parse", "extract", "dedup", "near", "duplicate", "fingerprint",
        "shingle", "minhash", "lsh", "frontier", "schedule", "politeness",
        "delay", "timeout", "retry", "redirect", "canonical", "noindex",
        "robots", "disallow", "allow", "crawl", "recrawl", "freshness",
        "sitemap", "rss", "feed", "api", "scrape", "proxy",
    ],
    "evaluation": [
        "precision", "recall", "f1", "ndcg", "map", "mrr", "trec",
        "qrel", "assessor", "judge", "relevance", "grade", "binary",
        "graded", "pooling", "depth", "cutoff", "interpolated", "average",
        "bpref", "rbp", "inferred", "topic", "run", "baseline", "system",
        "statistical", "significance", "ttest", "bootstrap", "confidence",
        "interval", "variance", "bias", "error", "gain", "ideal", "dcg",
        "cumulative", "discounted", "rank", "position", "order", "judgement",
        "pool", "incomplete", "reliable",
    ],
    "nlp": [
        "tokenization", "stemming", "lemmatization", "stopword", "ngram",
        "bigram", "trigram", "pos", "tagging", "parsing", "dependency",
        "constituent", "named", "entity", "recognition", "coreference",
        "resolution", "sentiment", "classification", "embedding", "word2vec",
        "glove", "fasttext", "bert", "transformer", "attention", "encoder",
        "decoder", "pretrained", "finetune", "contextual", "representation",
        "semantic", "syntactic", "morphology", "vocabulary", "subword",
        "bpe", "wordpiece", "sentencepiece", "language", "model", "neural",
        "deep", "learning", "lstm", "rnn",
    ],
}

_TOPIC_KEYS = list(_TOPIC_POOLS.keys())


def generate_corpus(num_docs, avg_length=50, vocab_overlap=0.5, seed=None):
    """
    Generate a synthetic IR corpus.

    Parameters
    ----------
    num_docs : int
        Number of documents to generate.
    avg_length : int
        Average number of words per document.
    vocab_overlap : float
        Fraction of each document drawn from the shared pool (0.0–1.0).
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict
        ``{"documents": {doc_id: {"text": str, "title": str, "source": str}}}``
    """
    rng = random.Random(seed)
    documents = {}

    for i in range(num_docs):
        length = max(10, int(rng.gauss(avg_length, avg_length * 0.2)))
        shared_count = int(length * vocab_overlap)
        topic_count = length - shared_count

        topic_key = _TOPIC_KEYS[i % len(_TOPIC_KEYS)]
        topic_pool = _TOPIC_POOLS[topic_key]

        shared_words = [rng.choice(_SHARED_POOL) for _ in range(shared_count)]
        topic_words = [rng.choice(topic_pool) for _ in range(topic_count)]

        words = shared_words + topic_words
        rng.shuffle(words)

        doc_id = f"doc_{i}"
        documents[doc_id] = {
            "text": " ".join(words),
            "title": f"Generated Doc {i}",
            "source": "Generator",
        }

    return {"documents": documents}
