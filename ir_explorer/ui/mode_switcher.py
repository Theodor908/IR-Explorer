"""Learn/Explore mode toggle header bar."""

import tkinter as tk
from tkinter import ttk
from ir_explorer.ui.theme import BG_DEEP, BG_PANEL, TEXT_PRIMARY, FONT_HEADING

class ModeSwitcher(ttk.Frame):
    def __init__(self, parent, on_mode_change=None, initial="learn", **kwargs):
        super().__init__(parent, **kwargs)
        self._mode = initial
        self._on_mode_change = on_mode_change
        self.configure(style="TFrame")
        ttk.Label(self, text="IR Explorer", font=FONT_HEADING).pack(side="left", padx=(12, 24))
        self._learn_btn = ttk.Button(self, text="Learn", command=lambda: self.set_mode("learn"))
        self._learn_btn.pack(side="left", padx=2)
        self._explore_btn = ttk.Button(self, text="Explore", command=lambda: self.set_mode("explore"))
        self._explore_btn.pack(side="left", padx=2)
        self._update_styles()

    def set_mode(self, mode):
        if mode == self._mode: return
        self._mode = mode
        self._update_styles()
        if self._on_mode_change: self._on_mode_change(mode)

    def get_mode(self): return self._mode

    def _update_styles(self):
        if self._mode == "learn":
            self._learn_btn.configure(style="ModeActive.TButton")
            self._explore_btn.configure(style="Mode.TButton")
        else:
            self._learn_btn.configure(style="Mode.TButton")
            self._explore_btn.configure(style="ModeActive.TButton")
