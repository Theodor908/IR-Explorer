"""Main application: root window, mode switching, shared state."""

import os
import tkinter as tk
from tkinter import ttk

from ir_explorer.ui.theme import BG_DEEP, setup_ttk_theme
from ir_explorer.ui.mode_switcher import ModeSwitcher
from ir_explorer.core.corpus import Corpus
from ir_explorer.core.index import InvertedIndex
from ir_explorer.core.preprocessing import PipelineConfig
from ir_explorer import settings

from ir_explorer.ui.explore.import_panel import ImportPanel
from ir_explorer.ui.explore.index_panel import IndexPanel
from ir_explorer.ui.explore.search_panel import SearchPanel
from ir_explorer.ui.explore.vocab_panel import VocabPanel
from ir_explorer.ui.explore.postings_panel import PostingsPanel
from ir_explorer.ui.explore.pipeline_panel import PipelinePanel
from ir_explorer.ui.explore.compare_panel import ComparePanel
from ir_explorer.ui.explore.eval_panel import EvalPanel
from ir_explorer.ui.explore.crawler_panel import CrawlerPanel
from ir_explorer.ui.explore.links_panel import LinksPanel

from ir_explorer.ui.learn.lesson_navigator import LessonNavigator
from ir_explorer.ui.learn.lesson_view import LessonView
from ir_explorer.lessons.engine import LessonEngine
from ir_explorer.lessons.registry import list_lessons, load_lesson


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IR Explorer \u2014 Educational IR Learning Tool")
        self.configure(bg=BG_DEEP)
        w, h = 1200, 800
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(900, 650)
        self._set_icon()
        setup_ttk_theme(self)

        self._settings = settings.load()
        self.corpus = Corpus()
        self.index = InvertedIndex()
        self.pipeline_config = PipelineConfig(
            **self._settings.get("pipeline_config", {})
        )
        saved_suffixes = self._settings.get("suffixes")
        if saved_suffixes is not None:
            from ir_explorer.core.preprocessing import set_suffixes
            set_suffixes(saved_suffixes)
        self._build_ui()

    def _set_icon(self):
        try:
            import sys
            # handle PyInstaller frozen path
            if getattr(sys, "frozen", False):
                base = sys._MEIPASS
            else:
                base = os.path.dirname(__file__)
            icon_dir = os.path.join(base, "ir_explorer", "assets") if getattr(sys, "frozen", False) else os.path.join(base, "assets")
            ico_path = os.path.join(icon_dir, "icon.ico")
            png_path = os.path.join(icon_dir, "icon.png")

            if sys.platform == "win32" and os.path.exists(ico_path):
                self.iconbitmap(default=ico_path)
            if os.path.exists(png_path):
                self._icon_img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, self._icon_img)
        except Exception:
            pass

    def _build_ui(self):
        self._menubar = tk.Menu(self, bg="#181a24", fg="#e0e2eb")
        self.config(menu=self._menubar)

        settings_menu = tk.Menu(self._menubar, tearoff=0, bg="#181a24", fg="#e0e2eb")
        self._menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(
            label="Stemmer Suffixes...", command=self._open_suffix_settings
        )

        self.mode_switcher = ModeSwitcher(
            self, on_mode_change=self._on_mode_change,
            initial=self._settings.get("active_mode", "learn")
        )
        self.mode_switcher.pack(fill="x", padx=4, pady=(4, 0))

        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True, padx=4, pady=4)

        self._explore_nb = ttk.Notebook(self._container)
        self.corpus_panel = ImportPanel(self._explore_nb, self)
        self._explore_nb.add(self.corpus_panel, text="  Corpus  ")
        self.index_panel = IndexPanel(self._explore_nb, self)
        self._explore_nb.add(self.index_panel, text="  Index  ")
        self.search_panel = SearchPanel(self._explore_nb, self)
        self._explore_nb.add(self.search_panel, text="  Search  ")
        self.vocab_panel = VocabPanel(self._explore_nb, self)
        self._explore_nb.add(self.vocab_panel, text="  Vocabulary  ")
        self.postings_panel = PostingsPanel(self._explore_nb, self)
        self._explore_nb.add(self.postings_panel, text="  Postings  ")
        self.pipeline_panel = PipelinePanel(self._explore_nb, self)
        self._explore_nb.add(self.pipeline_panel, text="  Pipeline  ")
        self.compare_panel = ComparePanel(self._explore_nb, self)
        self._explore_nb.add(self.compare_panel, text="  Compare  ")

        self.eval_panel = EvalPanel(self._explore_nb, self)
        self._explore_nb.add(self.eval_panel, text="  Evaluation  ")

        self.crawler_panel = CrawlerPanel(self._explore_nb, self)
        self._explore_nb.add(self.crawler_panel, text="  Crawler  ")

        self.links_panel = LinksPanel(self._explore_nb, self)
        self._explore_nb.add(self.links_panel, text="  Link Analysis  ")

        self._learn_nb = ttk.Frame(self._container)
        self._learn_engine = LessonEngine()
        self._learn_engine.load_progress()
        self._build_learn_mode()

        self._on_mode_change(self.mode_switcher.get_mode())

    def _on_mode_change(self, mode):
        self._explore_nb.pack_forget()
        self._learn_nb.pack_forget()
        if mode == "learn":
            self._learn_nb.pack(fill="both", expand=True)
        else:
            self._explore_nb.pack(fill="both", expand=True)
        self._settings["active_mode"] = mode
        settings.save(self._settings)

    def rebuild_index(self):
        self.index.build(self.corpus.docs, config=self.pipeline_config)

    def default_corpus_path(self):
        return os.path.join(os.path.dirname(__file__), "assets", "default_corpus.json")

    def _open_suffix_settings(self):
        from ir_explorer.ui.suffix_dialog import SuffixDialog
        SuffixDialog(self, on_apply=self._on_suffixes_changed)

    def _on_suffixes_changed(self, suffixes):
        self._settings["suffixes"] = suffixes
        settings.save(self._settings)

    # --- learn mode ---

    def _build_learn_mode(self):
        self._lesson_nav = LessonNavigator(
            self._learn_nb,
            on_select=self._on_lesson_selected,
        )
        self._lesson_nav.pack(side="left", fill="y", padx=0, pady=0, ipadx=0)

        sep = tk.Frame(self._learn_nb, bg="#2a2d3e", width=1)
        sep.pack(side="left", fill="y")

        self._lesson_view = LessonView(self._learn_nb)
        self._lesson_view.pack(side="left", fill="both", expand=True)
        self._lesson_view.set_nav_callbacks(self._on_lesson_back, self._on_lesson_next)

        lessons = list_lessons()
        self._lesson_nav.set_lessons(
            lessons,
            completed=self._learn_engine.completed_lessons,
        )

        if lessons:
            self._on_lesson_selected(lessons[0]["id"])

    def _on_lesson_selected(self, lesson_id):
        try:
            lesson_data = load_lesson(lesson_id)
        except ValueError:
            return
        self._learn_engine.load_lesson(lesson_data)
        self._lesson_nav.set_current(lesson_id)
        title = lesson_data.get("title", "")
        objective = lesson_data.get("objective", "")
        self._lesson_view.set_lesson_info(title, objective)
        self._on_lesson_next()

    def _on_lesson_next(self):
        step = self._learn_engine.next_step()
        if step is None:
            if self._learn_engine.current_lesson:
                lid = self._learn_engine.current_lesson["id"]
                self._learn_engine.mark_complete(lid)
                self._learn_engine.save_progress()
                lessons = list_lessons()
                lesson_ids = [l["id"] for l in lessons]
                try:
                    idx = lesson_ids.index(lid)
                    if idx + 1 < len(lesson_ids):
                        self._lesson_nav.set_lessons(
                            lessons,
                            completed=self._learn_engine.completed_lessons,
                        )
                        self._on_lesson_selected(lesson_ids[idx + 1])
                        return
                except ValueError:
                    pass
                self._lesson_nav.set_lessons(
                    lessons,
                    completed=self._learn_engine.completed_lessons,
                )
                self._lesson_nav.set_current(lid)
            return
        self._show_step(step)
        self._lesson_view.set_step_counter(
            self._learn_engine.current_step,
            self._learn_engine.total_steps(),
        )

    def _on_lesson_back(self):
        step = self._learn_engine.prev_step()
        if step is None:
            return
        self._show_step(step)
        self._lesson_view.set_step_counter(
            self._learn_engine.current_step,
            self._learn_engine.total_steps(),
        )

    def _show_step(self, step):
        stype = step.get("type", "theory")
        title = step.get("title", "")
        if stype == "theory":
            self._lesson_view.show_theory(title, step.get("content", ""))
        elif stype == "demo":
            action_key = step.get("action")
            highlight = step.get("highlight")
            animation_steps = None
            if action_key:
                try:
                    from ir_explorer.lessons.animations import generate_animation
                    animation_steps = generate_animation(action_key, self, highlight)
                except Exception:
                    animation_steps = None
            self._lesson_view.show_demo(
                title, step.get("narration", ""), animation_steps
            )
        elif stype == "experiment":
            self._lesson_view.show_experiment(title, step.get("prompt", ""))
        elif stype == "checkpoint":
            self._lesson_view.show_checkpoint(
                step.get("question", ""),
                step.get("reveal", ""),
            )
