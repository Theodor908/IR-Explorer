"""Inverted index: build, lookup, stats."""

from collections import defaultdict, Counter
from ir_explorer.core.preprocessing import PipelineConfig, configurable_pipeline


class InvertedIndex:
    def __init__(self):
        self.index = {}          # term -> sorted list of doc_ids
        self.tf = {}             # doc_id -> Counter(term -> freq)
        self._doc_ids = []
        self._df = {}
        self._config = PipelineConfig()

    def build(self, corpus_docs, config=None):
        """Build index from {doc_id: text} dict."""
        if config is not None:
            self._config = config
        raw_index = defaultdict(set)
        self.tf = {}
        self._doc_ids = sorted(corpus_docs.keys(),
                               key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)

        for doc_id, text in corpus_docs.items():
            tokens = configurable_pipeline(text, self._config)
            self.tf[doc_id] = Counter(tokens)
            for term in set(tokens):
                raw_index[term].add(doc_id)

        sort_key = lambda x: int(x[1:]) if x[1:].isdigit() else 0
        self.index = {
            term: sorted(docs, key=sort_key)
            for term, docs in raw_index.items()
        }
        self._df = {term: len(docs) for term, docs in self.index.items()}

    def get_postings(self, term):
        return list(self.index.get(term, []))

    def df(self, term):
        return self._df.get(term, 0)

    def vocabulary(self):
        return sorted(self.index.keys())

    def term_freq(self, doc_id):
        return dict(self.tf.get(doc_id, {}))

    def stats(self):
        total_postings = sum(len(p) for p in self.index.values())
        num_terms = len(self.index)
        max_df_term = max(self.index.items(), key=lambda x: len(x[1]),
                          default=("", []))
        df1_count = sum(1 for p in self.index.values() if len(p) == 1)
        return {
            "num_terms": num_terms,
            "num_documents": len(self._doc_ids),
            "total_postings": total_postings,
            "avg_postings_per_term": total_postings / num_terms if num_terms else 0,
            "max_df_term": max_df_term[0],
            "max_df_value": len(max_df_term[1]),
            "df1_count": df1_count,
            "df1_pct": 100 * df1_count / num_terms if num_terms else 0,
        }
