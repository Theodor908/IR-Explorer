"""Retrieval evaluation metrics: precision, recall, MAP."""

def precision_at_k(retrieved, relevant, k):
    if k == 0:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    return sum(1 for d in top_k if d in relevant) / len(top_k)

def recall_at_k(retrieved, relevant, k):
    if not relevant:
        return 0.0
    top_k = retrieved[:k]
    return sum(1 for d in top_k if d in relevant) / len(relevant)

def average_precision(retrieved, relevant):
    if not relevant:
        return 0.0
    hits = 0
    sum_precision = 0.0
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            hits += 1
            sum_precision += hits / (i + 1)
    return sum_precision / len(relevant)

def mean_average_precision(queries):
    if not queries:
        return 0.0
    return sum(average_precision(r, rel) for r, rel in queries) / len(queries)

def precision_recall_curve(retrieved, relevant):
    if not relevant:
        return [(0.0, 0.0)] * len(retrieved)
    points = []
    hits = 0
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            hits += 1
        precision = hits / (i + 1)
        recall = hits / len(relevant)
        points.append((recall, precision))
    return points
