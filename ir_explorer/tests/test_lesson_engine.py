import pytest
import json
from ir_explorer.lessons.engine import LessonEngine

@pytest.fixture
def sample_lesson():
    return {
        "id": "01_test",
        "title": "Test Lesson",
        "objective": "Test objective",
        "prerequisites": [],
        "corpus": "default",
        "steps": [
            {"type": "theory", "title": "Step 1", "content": "Theory text"},
            {"type": "demo", "title": "Step 2", "action": "tokenize_doc", "narration": "Watch"},
            {"type": "experiment", "title": "Step 3", "prompt": "Try it", "widget": "toggle_stopwords", "observe": ["vocab_size"]},
            {"type": "checkpoint", "title": "Step 4", "question": "What?", "reveal": "Answer"},
        ]
    }

def test_engine_init():
    engine = LessonEngine()
    assert engine.current_lesson is None
    assert engine.current_step == 0

def test_load_lesson(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    assert engine.current_lesson["id"] == "01_test"
    assert engine.current_step == 0
    assert engine.total_steps() == 4

def test_next_step(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    step = engine.next_step()
    assert step["type"] == "theory"
    step = engine.next_step()
    assert step["type"] == "demo"

def test_prev_step(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    engine.next_step()
    engine.next_step()
    step = engine.prev_step()
    assert step["type"] == "theory"

def test_prev_step_at_beginning(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    step = engine.prev_step()
    assert step is None

def test_is_complete(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    assert not engine.is_complete()
    for _ in range(4):
        engine.next_step()
    assert engine.is_complete()

def test_reset(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    engine.next_step()
    engine.next_step()
    engine.reset()
    assert engine.current_step == 0

def test_get_current_step(sample_lesson):
    engine = LessonEngine()
    engine.load_lesson(sample_lesson)
    assert engine.get_current_step() is None
    engine.next_step()
    step = engine.get_current_step()
    assert step["type"] == "theory"

def test_progress_save_load(tmp_path, sample_lesson):
    path = tmp_path / "progress.json"
    engine = LessonEngine(progress_path=str(path))
    engine.load_lesson(sample_lesson)
    engine.next_step()
    engine.next_step()
    engine.mark_complete("01_test")
    engine.save_progress()
    engine2 = LessonEngine(progress_path=str(path))
    engine2.load_progress()
    assert "01_test" in engine2.completed_lessons

def test_progress_corrupted_file(tmp_path):
    path = tmp_path / "progress.json"
    path.write_text("not json!!!")
    engine = LessonEngine(progress_path=str(path))
    engine.load_progress()
    assert engine.completed_lessons == []

def test_progress_missing_file(tmp_path):
    path = tmp_path / "nonexistent.json"
    engine = LessonEngine(progress_path=str(path))
    engine.load_progress()
    assert engine.completed_lessons == []
