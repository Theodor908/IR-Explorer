"""Text preprocessing: tokenization, stopword removal, stemming."""

import re
from dataclasses import dataclass

STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or "
    "that the to use with this not but can do if into also so than we they them "
    "their our which what there these those was were been how who all some any "
    "no more other such only same very will about between each after before "
    "over through just most would should could up out when where".split()
)

_DEFAULT_SUFFIXES = [
    "ation", "ition", "ing", "ness", "ment", "ous", "ive", "ity", "ies",
    "ical", "ally", "ble", "ful", "less", "ed", "ly", "er", "ses", "es", "s",
]

_SUFFIXES = list(_DEFAULT_SUFFIXES)


def get_suffixes():
    return list(_SUFFIXES)


def set_suffixes(suffixes):
    global _SUFFIXES
    _SUFFIXES = sorted(suffixes, key=len, reverse=True)


def reset_suffixes():
    global _SUFFIXES
    _SUFFIXES = list(_DEFAULT_SUFFIXES)


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS]


def stem(token):
    for suf in _SUFFIXES:
        if token.endswith(suf) and len(token) > len(suf) + 2:
            return token[:-len(suf)]
    return token


def stem_all(tokens):
    return [stem(t) for t in tokens]


def pipeline(text):
    raw = tokenize(text)
    no_stop = remove_stopwords(raw)
    stemmed = stem_all(no_stop)
    return {"raw": raw, "no_stop": no_stop, "stemmed": stemmed}


@dataclass
class PipelineConfig:
    remove_stopwords: bool = True
    apply_stemming: bool = False
    tf_scheme: str = "log"      # "raw", "log", "boolean"
    idf_scheme: str = "standard"  # "standard", "smoothed"


def configurable_pipeline(text, config=None):
    if config is None:
        config = PipelineConfig()
    tokens = tokenize(text)
    if config.remove_stopwords:
        tokens = remove_stopwords(tokens)
    if config.apply_stemming:
        tokens = stem_all(tokens)
    return tokens
