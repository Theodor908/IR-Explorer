# ir_explorer/tests/test_preprocessing.py
import pytest
from ir_explorer.core.preprocessing import tokenize, remove_stopwords, stem, pipeline, STOPWORDS


def test_tokenize_basic():
    assert tokenize("Hello, World! 123") == ["hello", "world", "123"]

def test_tokenize_empty():
    assert tokenize("") == []

def test_tokenize_preserves_numbers():
    assert tokenize("Level 4 multiverse") == ["level", "4", "multiverse"]

def test_remove_stopwords():
    tokens = ["the", "quantum", "universe", "is", "large"]
    result = remove_stopwords(tokens)
    assert "the" not in result
    assert "is" not in result
    assert "quantum" in result
    assert "universe" in result

def test_stem_suffix_stripping():
    assert stem("universes") == "univer"
    assert stem("branching") == "branch"

def test_stem_short_words_unchanged():
    assert stem("the") == "the"
    assert stem("is") == "is"

def test_pipeline_returns_all_stages():
    text = "The inflationary universe is expanding"
    result = pipeline(text)
    assert "raw" in result
    assert "no_stop" in result
    assert "stemmed" in result
    assert len(result["raw"]) >= len(result["no_stop"])
    assert len(result["no_stop"]) == len(result["stemmed"])

def test_pipeline_raw_matches_tokenize():
    text = "Parallel universes are predicted"
    result = pipeline(text)
    assert result["raw"] == tokenize(text)


from ir_explorer.core.preprocessing import PipelineConfig, configurable_pipeline

def test_pipeline_config_defaults():
    config = PipelineConfig()
    assert config.remove_stopwords is True
    assert config.apply_stemming is False
    assert config.tf_scheme == "log"
    assert config.idf_scheme == "standard"

def test_configurable_pipeline_default():
    result = configurable_pipeline("The quantum universe is large")
    assert "the" not in result
    assert "quantum" in result
    assert "universe" in result

def test_configurable_pipeline_no_stopwords_removal():
    config = PipelineConfig(remove_stopwords=False)
    result = configurable_pipeline("The quantum universe is large", config)
    assert "the" in result
    assert "quantum" in result

def test_configurable_pipeline_with_stemming():
    config = PipelineConfig(apply_stemming=True)
    result = configurable_pipeline("quantum universes expanding", config)
    # "universes" -> stem strips "es" suffix -> "univer"; "expanding" -> strips "ing" -> "expand"
    assert "univer" in result
    assert "expand" in result

def test_configurable_pipeline_both_off():
    config = PipelineConfig(remove_stopwords=False, apply_stemming=False)
    result = configurable_pipeline("The universe is large", config)
    assert "the" in result
    assert "universe" in result
