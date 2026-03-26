import pytest
from ir_explorer.core.crawler import LinkGraph, build_graph_from_corpus, crawl_bfs, crawl_dfs

def test_link_graph_add_nodes_and_edges():
    g = LinkGraph()
    g.add_node("d1")
    g.add_node("d2")
    g.add_edge("d1", "d2")
    assert g.nodes() == {"d1", "d2"}
    assert "d2" in g.neighbors("d1")
    assert g.number_of_edges() == 1

def test_link_graph_from_adjacency():
    adj = {"d1": ["d2", "d3"], "d2": ["d3"]}
    g = LinkGraph.from_adjacency(adj)
    assert "d1" in g.nodes()
    assert "d2" in g.neighbors("d1")
    assert "d3" in g.neighbors("d1")
    assert g.number_of_edges() == 3

def test_build_graph_from_corpus():
    corpus = {
        "d1": "quantum universe inflation multiverse parallel",
        "d2": "quantum mechanics wave function decoherence",
        "d3": "inflation cosmological expansion universe",
    }
    g = build_graph_from_corpus(corpus)
    assert len(g.nodes()) == 3
    assert g.number_of_edges() > 0

def test_crawl_bfs_basic():
    g = LinkGraph()
    for n in ["d1", "d2", "d3", "d4"]:
        g.add_node(n)
    g.add_edge("d1", "d2")
    g.add_edge("d1", "d3")
    g.add_edge("d2", "d4")
    steps = list(crawl_bfs(g, "d1", max_depth=2, max_pages=10))
    visited = [s["current"] for s in steps]
    assert visited[0] == "d1"
    assert "d2" in visited
    assert "d3" in visited

def test_crawl_bfs_max_pages():
    g = LinkGraph()
    for n in ["d1", "d2", "d3", "d4"]:
        g.add_node(n)
    g.add_edge("d1", "d2")
    g.add_edge("d1", "d3")
    g.add_edge("d2", "d4")
    steps = list(crawl_bfs(g, "d1", max_depth=10, max_pages=2))
    assert len(steps) == 2

def test_crawl_dfs_basic():
    g = LinkGraph()
    for n in ["d1", "d2", "d3"]:
        g.add_node(n)
    g.add_edge("d1", "d2")
    g.add_edge("d2", "d3")
    steps = list(crawl_dfs(g, "d1", max_depth=3, max_pages=10))
    visited = [s["current"] for s in steps]
    assert visited[0] == "d1"
    assert "d2" in visited
    assert "d3" in visited

def test_crawl_step_has_state():
    g = LinkGraph()
    g.add_node("d1")
    g.add_node("d2")
    g.add_edge("d1", "d2")
    steps = list(crawl_bfs(g, "d1", max_depth=2, max_pages=10))
    step = steps[0]
    assert "current" in step
    assert "visited" in step
    assert "frontier" in step
