"""App settings persistence to %APPDATA%/IRExplorer/settings.json."""

import copy
import json
import os

_DEFAULTS = {
    "active_mode": "learn",
    "show_hints": True,
    "playback_speed": 1.0,
    "pipeline_config": {
        "remove_stopwords": True,
        "apply_stemming": False,
        "tf_scheme": "log",
        "idf_scheme": "standard",
    },
}

def _settings_dir():
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    return os.path.join(base, "IRExplorer")

def _settings_path():
    return os.path.join(_settings_dir(), "settings.json")

def load():
    try:
        with open(_settings_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = copy.deepcopy(_DEFAULTS)
        merged.update(data)
        if "pipeline_config" in data and isinstance(data["pipeline_config"], dict):
            pc = copy.deepcopy(_DEFAULTS["pipeline_config"])
            pc.update(data["pipeline_config"])
            merged["pipeline_config"] = pc
        return merged
    except Exception:
        return copy.deepcopy(_DEFAULTS)

def save(settings):
    try:
        d = _settings_dir()
        os.makedirs(d, exist_ok=True)
        with open(_settings_path(), "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

def defaults():
    return copy.deepcopy(_DEFAULTS)
