import pytest
from ir_explorer.core.crawler import LinkGraph
from ir_explorer.core.link_analysis import hits, pagerank

@pytest.fixture
def simple_graph():
    g = LinkGraph()
    for n in ["d1", "d2", "d3", "d4"]:
        g.add_node(n)
    g.add_edge("d1", "d2")
    g.add_edge("d1", "d3")
    g.add_edge("d1", "d4")
    g.add_edge("d2", "d4")
    g.add_edge("d3", "d4")
    return g

def test_hits_returns_per_iteration(simple_graph):
    result = hits(simple_graph, iterations=5)
    assert len(result) == 5
    auth, hub = result[-1]
    assert set(auth.keys()) == {"d1", "d2", "d3", "d4"}

def test_hits_authority_scores(simple_graph):
    result = hits(simple_graph, iterations=20)
    auth, hub = result[-1]
    assert auth["d4"] == max(auth.values())

def test_hits_hub_scores(simple_graph):
    result = hits(simple_graph, iterations=20)
    auth, hub = result[-1]
    assert hub["d1"] == max(hub.values())

def test_pagerank_returns_per_iteration(simple_graph):
    result = pagerank(simple_graph, damping=0.85, iterations=5)
    assert len(result) == 5
    scores = result[-1]
    assert set(scores.keys()) == {"d1", "d2", "d3", "d4"}

def test_pagerank_scores_sum_to_one(simple_graph):
    result = pagerank(simple_graph, damping=0.85, iterations=20)
    scores = result[-1]
    assert sum(scores.values()) == pytest.approx(1.0, abs=0.01)

def test_pagerank_authority_has_highest_score(simple_graph):
    result = pagerank(simple_graph, damping=0.85, iterations=20)
    scores = result[-1]
    assert scores["d4"] == max(scores.values())

def test_hits_single_node():
    g = LinkGraph()
    g.add_node("d1")
    result = hits(g, iterations=3)
    assert len(result) == 3

def test_pagerank_single_node():
    g = LinkGraph()
    g.add_node("d1")
    result = pagerank(g, iterations=3)
    assert result[-1]["d1"] == pytest.approx(1.0, abs=0.01)
