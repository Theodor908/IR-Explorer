"""Discovers and loads lesson YAML definitions."""
import os
import yaml

_DEFINITIONS_DIR = os.path.join(os.path.dirname(__file__), "definitions")

def list_lessons():
    lessons = []
    if not os.path.isdir(_DEFINITIONS_DIR):
        return lessons
    for fname in sorted(os.listdir(_DEFINITIONS_DIR)):
        if fname.endswith((".yaml", ".yml")):
            path = os.path.join(_DEFINITIONS_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            lessons.append({"id": data["id"], "title": data["title"], "filename": fname, "path": path})
    return lessons

def load_lesson(lesson_id):
    if not os.path.isdir(_DEFINITIONS_DIR):
        raise ValueError(f"Lesson '{lesson_id}' not found")
    for fname in os.listdir(_DEFINITIONS_DIR):
        if not fname.endswith((".yaml", ".yml")): continue
        path = os.path.join(_DEFINITIONS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data.get("id") == lesson_id: return data
    raise ValueError(f"Lesson '{lesson_id}' not found")
