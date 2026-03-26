"""Simulated web crawler with LinkGraph for educational visualization."""

from collections import deque
from ir_explorer.core.preprocessing import tokenize, remove_stopwords


class LinkGraph:

    def __init__(self):
        self._adj = {}

    def add_node(self, node):
        if node not in self._adj:
            self._adj[node] = set()

    def add_edge(self, source, target):
        self.add_node(source)
        self.add_node(target)
        self._adj[source].add(target)

    def nodes(self):
        return set(self._adj.keys())

    def neighbors(self, node):
        return self._adj.get(node, set())

    def in_neighbors(self, node):
        return {n for n, adj in self._adj.items() if node in adj}

    def number_of_edges(self):
        return sum(len(targets) for targets in self._adj.values())

    def adjacency(self):
        return {n: sorted(adj) for n, adj in self._adj.items()}

    @classmethod
    def from_adjacency(cls, adj_dict):
        g = cls()
        for source, targets in adj_dict.items():
            g.add_node(source)
            for target in targets:
                g.add_edge(source, target)
        return g


def build_graph_from_corpus(corpus_docs, threshold=2):
    doc_terms = {}
    for doc_id, text in corpus_docs.items():
        doc_terms[doc_id] = set(remove_stopwords(tokenize(text)))
    g = LinkGraph()
    doc_ids = sorted(corpus_docs.keys())
    for d in doc_ids:
        g.add_node(d)
    for i, d1 in enumerate(doc_ids):
        for d2 in doc_ids[i + 1:]:
            shared = len(doc_terms[d1] & doc_terms[d2])
            if shared >= threshold:
                g.add_edge(d1, d2)
                g.add_edge(d2, d1)
    return g


def crawl_bfs(graph, seed, max_depth=3, max_pages=20):
    visited = set()
    queue = deque([(seed, 0)])
    while queue and len(visited) < max_pages:
        current, depth = queue.popleft()
        if current in visited or depth > max_depth:
            continue
        visited.add(current)
        frontier = list(queue)
        yield {
            "current": current,
            "visited": set(visited),
            "frontier": [n for n, _ in frontier],
            "depth": depth,
        }
        for neighbor in sorted(graph.neighbors(current)):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))


def crawl_dfs(graph, seed, max_depth=3, max_pages=20):
    visited = set()
    stack = [(seed, 0)]
    while stack and len(visited) < max_pages:
        current, depth = stack.pop()
        if current in visited or depth > max_depth:
            continue
        visited.add(current)
        yield {
            "current": current,
            "visited": set(visited),
            "frontier": [n for n, _ in stack],
            "depth": depth,
        }
        for neighbor in sorted(graph.neighbors(current), reverse=True):
            if neighbor not in visited:
                stack.append((neighbor, depth + 1))
