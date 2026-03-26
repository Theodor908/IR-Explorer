"""Left sidebar showing lesson list with progress indicators."""
import tkinter as tk
from tkinter import ttk

from ir_explorer.ui.theme import (
    BG_PANEL, BG_PANEL_ALT, BG_DEEP,
    TEXT_PRIMARY, TEXT_SECONDARY,
    LEARN_ACCENT, LEARN_ACCENT_DIM, LEARN_ACCENT_HOVER,
    SUCCESS, BUTTON_BG, BUTTON_HOVER,
    FONT, FONT_BOLD, FONT_HEADING, BORDER,
)


class LessonNavigator(ttk.Frame):

    def __init__(self, parent, on_select=None):
        super().__init__(parent)
        self.configure(style="TFrame")
        self._on_select = on_select
        self._buttons = {}      # lesson_id -> tk.Button
        self._current_id = None
        self._build()

    def _build(self):
        hdr = tk.Label(
            self, text="Lessons",
            bg=BG_PANEL, fg=TEXT_PRIMARY,
            font=FONT_HEADING, anchor="w", padx=8, pady=6,
        )
        hdr.pack(fill="x", side="top")

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", side="top")

        self._canvas = tk.Canvas(self, bg=BG_PANEL, highlightthickness=0, bd=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._list_frame = tk.Frame(self._canvas, bg=BG_PANEL)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw"
        )
        self._list_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_frame_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def set_lessons(self, lessons, completed=None):
        completed = completed or []
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._buttons.clear()

        for lesson in lessons:
            lid = lesson["id"]
            title = lesson["title"]
            is_done = lid in completed

            label_text = (f"✓ {title}" if is_done else f"   {title}")
            fg = SUCCESS if is_done else TEXT_PRIMARY

            btn = tk.Button(
                self._list_frame,
                text=label_text,
                fg=fg,
                bg=BUTTON_BG,
                activebackground=BUTTON_HOVER,
                activeforeground=TEXT_PRIMARY,
                font=FONT,
                anchor="w",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
                cursor="hand2",
                command=lambda l=lid: self._select(l),
            )
            btn.pack(fill="x", pady=1, padx=2)
            self._buttons[lid] = btn

    def _select(self, lesson_id):
        self.set_current(lesson_id)
        if self._on_select:
            self._on_select(lesson_id)

    def set_current(self, lesson_id):
        if self._current_id and self._current_id in self._buttons:
            self._buttons[self._current_id].configure(bg=BUTTON_BG)

        self._current_id = lesson_id
        if lesson_id and lesson_id in self._buttons:
            self._buttons[lesson_id].configure(bg=LEARN_ACCENT_DIM)
