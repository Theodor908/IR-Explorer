"""Lesson state machine: navigation, progress tracking, persistence."""
import json
import os

class LessonEngine:
    def __init__(self, progress_path=None):
        self.current_lesson = None
        self.current_step = 0
        self._step_index = -1
        self.completed_lessons = []
        self._progress_path = progress_path or self._default_progress_path()

    def load_lesson(self, lesson_data):
        self.current_lesson = lesson_data
        self.current_step = 0
        self._step_index = -1

    def total_steps(self):
        if not self.current_lesson: return 0
        return len(self.current_lesson.get("steps", []))

    def next_step(self):
        if not self.current_lesson: return None
        steps = self.current_lesson.get("steps", [])
        if self._step_index < len(steps) - 1:
            self._step_index += 1
            self.current_step = self._step_index + 1
            return steps[self._step_index]
        return None

    def prev_step(self):
        if not self.current_lesson or self._step_index <= 0: return None
        self._step_index -= 1
        self.current_step = self._step_index + 1
        return self.current_lesson["steps"][self._step_index]

    def get_current_step(self):
        if not self.current_lesson or self._step_index < 0: return None
        steps = self.current_lesson.get("steps", [])
        if 0 <= self._step_index < len(steps): return steps[self._step_index]
        return None

    def is_complete(self):
        if not self.current_lesson: return False
        return self._step_index >= len(self.current_lesson.get("steps", [])) - 1

    def reset(self):
        self.current_step = 0
        self._step_index = -1

    def mark_complete(self, lesson_id):
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)

    def save_progress(self):
        data = {
            "completed_lessons": self.completed_lessons,
            "current_lesson": self.current_lesson["id"] if self.current_lesson else None,
            "current_step": self.current_step,
        }
        try:
            dirname = os.path.dirname(self._progress_path)
            if dirname: os.makedirs(dirname, exist_ok=True)
            with open(self._progress_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception: pass

    def load_progress(self):
        try:
            with open(self._progress_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.completed_lessons = data.get("completed_lessons", [])
        except Exception:
            self.completed_lessons = []

    @staticmethod
    def _default_progress_path():
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "IRExplorer", "progress.json")
