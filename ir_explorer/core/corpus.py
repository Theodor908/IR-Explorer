"""Corpus model: stores documents and metadata."""

import json
import re


class Corpus:
    def __init__(self):
        self.docs = {}      # doc_id -> text
        self.metadata = {}   # doc_id -> {"title": ..., "source": ...}
        self.links = {}      # doc_id -> [linked doc_ids]

    def add(self, doc_id, text, title="", source=""):
        if doc_id in self.docs:
            raise ValueError(f"Document '{doc_id}' already exists")
        self.docs[doc_id] = text
        self.metadata[doc_id] = {"title": title, "source": source}

    def remove(self, doc_id):
        self.docs.pop(doc_id, None)
        self.metadata.pop(doc_id, None)

    def clear(self):
        self.docs.clear()
        self.metadata.clear()
        self.links.clear()

    def doc_ids(self):
        return sorted(self.docs.keys(), key=self._sort_key)

    def word_count(self, doc_id):
        return len(self.docs[doc_id].split())

    def next_id(self):
        if not self.docs:
            return "d1"
        max_n = max(int(re.search(r"\d+", d).group()) for d in self.docs)
        return f"d{max_n + 1}"

    def load_from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for doc_id, info in data["documents"].items():
            self.add(doc_id, info["text"],
                     title=info.get("title", ""),
                     source=info.get("source", ""))
        self.links = data.get("links", {})

    @staticmethod
    def _sort_key(doc_id):
        m = re.search(r"\d+", doc_id)
        return int(m.group()) if m else 0
