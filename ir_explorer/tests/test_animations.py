import pytest
from ir_explorer.lessons.animations import generate_animation

ALL_ACTIONS = [
    "tokenize_doc", "remove_stopwords", "apply_stemming",
    "build_index", "boolean_search", "tfidf_search",
    "run_evaluation", "run_crawl", "run_pagerank",
]


@pytest.mark.parametrize("action_key", ALL_ACTIONS)
def test_generate_animation_returns_steps(action_key):
    # app arg is ignored — animations use private lesson data
    steps = generate_animation(action_key, None, highlight=["d1", "d2", "d3"])
    assert isinstance(steps, list)
    assert len(steps) > 0
    assert len(steps) < 200


@pytest.mark.parametrize("action_key", ALL_ACTIONS)
def test_draw_fns_are_callable(action_key):
    steps = generate_animation(action_key, None, highlight=["d1"])
    for draw_fn, duration_ms in steps:
        assert callable(draw_fn)
        assert isinstance(duration_ms, int)
        assert duration_ms > 0


def test_unknown_action_raises():
    with pytest.raises(ValueError):
        generate_animation("nonexistent_action", None)


def test_private_data_isolated():
    """Animations use their own corpus, not whatever app passes."""
    steps = generate_animation("tokenize_doc", None, highlight=["d1"])
    assert len(steps) > 0
    # Calling with a different 'app' should produce identical results
    steps2 = generate_animation("tokenize_doc", "anything", highlight=["d1"])
    assert len(steps) == len(steps2)
