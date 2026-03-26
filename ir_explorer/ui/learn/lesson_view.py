"""Main lesson area displaying step content and navigation."""
import tkinter as tk
from tkinter import ttk

from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, BG_PANEL_ALT, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, ACCENT_DIM, SUCCESS,
    LEARN_ACCENT, LEARN_ACCENT_DIM,
    BUTTON_BG, BUTTON_HOVER,
    FONT, FONT_BOLD, FONT_HEADING, FONT_SMALL,
    style_text,
)


class LessonView(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="TFrame")
        self._back_fn = None
        self._next_fn = None
        self._build()

    def _build(self):
        self._info_bar = tk.Frame(self, bg=BG_PANEL_ALT)
        self._info_bar.pack(fill="x", side="top", padx=0, pady=0)

        self._lbl_title = tk.Label(
            self._info_bar, text="",
            bg=BG_PANEL_ALT, fg=TEXT_PRIMARY,
            font=FONT_HEADING, anchor="w", padx=10, pady=4,
        )
        self._lbl_title.pack(fill="x", side="top")

        self._lbl_objective = tk.Label(
            self._info_bar, text="",
            bg=BG_PANEL_ALT, fg=TEXT_SECONDARY,
            font=FONT_SMALL, anchor="w", padx=10, pady=2,
        )
        self._lbl_objective.pack(fill="x", side="top")

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

        self._counter_bar = tk.Frame(self, bg=BG_PANEL)
        self._counter_bar.pack(fill="x", side="top")
        self._lbl_counter = tk.Label(
            self._counter_bar, text="",
            bg=BG_PANEL, fg=TEXT_SECONDARY,
            font=FONT_SMALL, anchor="e", padx=10, pady=3,
        )
        self._lbl_counter.pack(fill="x", side="top")

        self._content_outer = tk.Frame(self, bg=BG_PANEL)
        self._content_outer.pack(fill="both", expand=True)

        self._content_canvas = tk.Canvas(
            self._content_outer, bg=BG_PANEL, highlightthickness=0, bd=0
        )
        self._content_sb = ttk.Scrollbar(
            self._content_outer, orient="vertical",
            command=self._content_canvas.yview,
        )
        self._content_canvas.configure(yscrollcommand=self._content_sb.set)
        self._content_sb.pack(side="right", fill="y")
        self._content_canvas.pack(side="left", fill="both", expand=True)

        self._content_frame = tk.Frame(self._content_canvas, bg=BG_PANEL)
        self._cwin = self._content_canvas.create_window(
            (0, 0), window=self._content_frame, anchor="nw"
        )
        self._content_frame.bind("<Configure>", self._on_frame_cfg)
        self._content_canvas.bind("<Configure>", self._on_canvas_cfg)

        sep2 = tk.Frame(self, bg=BORDER, height=1)
        sep2.pack(fill="x", side="bottom")

        self._nav_bar = tk.Frame(self, bg=BG_PANEL_ALT)
        self._nav_bar.pack(fill="x", side="bottom")

        self._btn_back = tk.Button(
            self._nav_bar, text="◀  Back",
            bg=BUTTON_BG, fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER, activeforeground=TEXT_PRIMARY,
            font=FONT_BOLD, relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2",
            command=self._do_back,
        )
        self._btn_back.pack(side="left", padx=8, pady=6)

        self._btn_next = tk.Button(
            self._nav_bar, text="Next  ▶",
            bg=LEARN_ACCENT_DIM, fg=TEXT_PRIMARY,
            activebackground=LEARN_ACCENT, activeforeground=TEXT_PRIMARY,
            font=FONT_BOLD, relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2",
            command=self._do_next,
        )
        self._btn_next.pack(side="right", padx=8, pady=6)

    def _on_frame_cfg(self, event=None):
        self._content_canvas.configure(scrollregion=self._content_canvas.bbox("all"))

    def _on_canvas_cfg(self, event=None):
        self._content_canvas.itemconfig(self._cwin, width=event.width)

    def set_lesson_info(self, title, objective):
        self._lbl_title.configure(text=title)
        self._lbl_objective.configure(text=f"Objective: {objective}")

    def set_step_counter(self, current, total):
        if current and total:
            self._lbl_counter.configure(text=f"Step {current} of {total}")
        else:
            self._lbl_counter.configure(text="")

    def set_nav_callbacks(self, back_fn, next_fn):
        self._back_fn = back_fn
        self._next_fn = next_fn

    def _do_back(self):
        if self._back_fn:
            self._back_fn()

    def _do_next(self):
        if self._next_fn:
            self._next_fn()

    def _clear_content(self):
        for w in self._content_frame.winfo_children():
            if hasattr(w, 'stop'):
                w.stop()
            w.destroy()

    def _section_label(self, text, color=None):
        lbl = tk.Label(
            self._content_frame,
            text=text,
            bg=BG_PANEL, fg=color or TEXT_PRIMARY,
            font=FONT_HEADING, anchor="w",
            wraplength=0,
        )
        lbl.pack(fill="x", padx=16, pady=(12, 2))

    def _body_text(self, content):
        txt = tk.Text(
            self._content_frame,
            wrap="word",
            padx=16, pady=8,
        )
        style_text(txt)
        txt.configure(bg=BG_DEEP, relief="flat")
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        # rough line count for auto-height
        lines = content.count("\n") + 1
        for line in content.split("\n"):
            lines += max(0, len(line) // 80)
        txt.configure(height=min(lines + 2, 40))
        txt.pack(fill="x", padx=16, pady=(0, 12))

    def show_theory(self, title, content):
        self._clear_content()
        tag = tk.Label(
            self._content_frame,
            text="THEORY",
            bg=ACCENT_DIM, fg=TEXT_PRIMARY,
            font=FONT_SMALL, padx=8, pady=2,
        )
        tag.pack(anchor="w", padx=16, pady=(14, 0))
        self._section_label(title, color=TEXT_PRIMARY)
        self._body_text(content)

    def show_demo(self, title, narration, animation_steps=None):
        self._clear_content()
        tag = tk.Label(
            self._content_frame,
            text="DEMO",
            bg=LEARN_ACCENT_DIM, fg=TEXT_PRIMARY,
            font=FONT_SMALL, padx=8, pady=2,
        )
        tag.pack(anchor="w", padx=16, pady=(14, 0))
        self._section_label(title)
        self._body_text(narration)

        if animation_steps:
            from ir_explorer.ui.widgets.animated_canvas import AnimatedCanvas
            anim = AnimatedCanvas(self._content_frame, width=580, height=350)
            anim.pack(fill="x", padx=16, pady=(4, 12))
            anim.load_steps(animation_steps)
            anim.play()
        else:
            hint = tk.Label(
                self._content_frame,
                text="Switch to Explore mode to interact with this concept hands-on.",
                bg=BG_PANEL_ALT, fg=TEXT_SECONDARY,
                font=FONT_SMALL, padx=12, pady=8,
                wraplength=700, justify="left",
            )
            hint.pack(fill="x", padx=16, pady=(0, 12))

    def show_experiment(self, title, prompt):
        self._clear_content()
        tag = tk.Label(
            self._content_frame,
            text="EXPERIMENT",
            bg=BG_PANEL_ALT, fg=SUCCESS,
            font=FONT_SMALL, padx=8, pady=2,
        )
        tag.pack(anchor="w", padx=16, pady=(14, 0))
        self._section_label(title)
        self._body_text(prompt)
        hint = tk.Label(
            self._content_frame,
            text="Try this in Explore mode: load a corpus, build the index, and experiment with the tabs.",
            bg=BG_PANEL_ALT, fg=TEXT_SECONDARY,
            font=FONT_SMALL, padx=12, pady=8,
            wraplength=700, justify="left",
        )
        hint.pack(fill="x", padx=16, pady=(0, 12))

    def show_checkpoint(self, question, reveal):
        self._clear_content()
        tag = tk.Label(
            self._content_frame,
            text="CHECKPOINT",
            bg=BG_PANEL_ALT, fg=ACCENT,
            font=FONT_SMALL, padx=8, pady=2,
        )
        tag.pack(anchor="w", padx=16, pady=(14, 0))
        self._section_label("Checkpoint Question")
        q_lbl = tk.Label(
            self._content_frame,
            text=question,
            bg=BG_PANEL, fg=TEXT_PRIMARY,
            font=FONT_BOLD, anchor="w", padx=16, pady=6,
            wraplength=700, justify="left",
        )
        q_lbl.pack(fill="x")

        reveal_frame = tk.Frame(self._content_frame, bg=BG_PANEL)
        reveal_frame.pack(fill="x", padx=16, pady=(8, 4))

        answer_var = tk.StringVar(value="")
        answer_lbl = tk.Label(
            reveal_frame,
            textvariable=answer_var,
            bg=BG_PANEL_ALT, fg=SUCCESS,
            font=FONT, anchor="w", padx=12, pady=6,
            wraplength=680, justify="left",
        )

        def _reveal():
            answer_var.set(reveal)
            answer_lbl.pack(fill="x", pady=(4, 0))
            reveal_btn.configure(state="disabled")

        reveal_btn = tk.Button(
            reveal_frame,
            text="Reveal Answer",
            bg=ACCENT_DIM, fg=TEXT_PRIMARY,
            activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
            font=FONT_BOLD, relief="flat", bd=0, padx=12, pady=5,
            cursor="hand2",
            command=_reveal,
        )
        reveal_btn.pack(anchor="w")
