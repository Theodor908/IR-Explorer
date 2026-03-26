"""HITS and PageRank algorithms with per-iteration results for animation."""

import math

def hits(graph, iterations=20):
    nodes = sorted(graph.nodes())
    if not nodes:
        return []
    n = len(nodes)
    auth = {node: 1.0 / n for node in nodes}
    hub = {node: 1.0 / n for node in nodes}
    results = []
    for _ in range(iterations):
        new_auth = {}
        for node in nodes:
            new_auth[node] = sum(hub.get(src, 0) for src in graph.in_neighbors(node))
        new_hub = {}
        for node in nodes:
            new_hub[node] = sum(new_auth.get(tgt, 0) for tgt in graph.neighbors(node))
        auth_norm = math.sqrt(sum(v ** 2 for v in new_auth.values())) or 1.0
        hub_norm = math.sqrt(sum(v ** 2 for v in new_hub.values())) or 1.0
        auth = {k: v / auth_norm for k, v in new_auth.items()}
        hub = {k: v / hub_norm for k, v in new_hub.items()}
        results.append((dict(auth), dict(hub)))
    return results

def pagerank(graph, damping=0.85, iterations=20):
    nodes = sorted(graph.nodes())
    if not nodes:
        return []
    n = len(nodes)
    scores = {node: 1.0 / n for node in nodes}
    results = []
    out_degree = {}
    for node in nodes:
        out_degree[node] = len(graph.neighbors(node))
    for _ in range(iterations):
        # dangling nodes (no outgoing edges) distribute rank evenly
        dangling_sum = sum(scores[node] for node in nodes if out_degree[node] == 0)
        new_scores = {}
        for node in nodes:
            rank_sum = dangling_sum / n
            for src in graph.in_neighbors(node):
                if out_degree[src] > 0:
                    rank_sum += scores[src] / out_degree[src]
            new_scores[node] = (1 - damping) / n + damping * rank_sum
        scores = new_scores
        results.append(dict(scores))
    return results
