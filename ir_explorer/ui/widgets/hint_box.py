"""Collapsible hint panel."""

import tkinter as tk
from tkinter import ttk
from ir_explorer.ui.theme import (
    BG_PANEL_ALT, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, FONT, FONT_BOLD
)

class HintBox(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._expanded = True
        self._title_var = tk.StringVar(value="")
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x")
        self._toggle_btn = ttk.Button(header, text="▼ Hint", width=8, command=self._toggle)
        self._toggle_btn.pack(side="left")
        self._title_label = ttk.Label(header, textvariable=self._title_var, font=FONT_BOLD, foreground=ACCENT)
        self._title_label.pack(side="left", padx=(8, 0))
        self._content_frame = ttk.Frame(self)
        self._content_frame.pack(fill="both", expand=True, pady=(4, 0))
        self._text = tk.Text(self._content_frame, wrap="word", height=4,
            bg=BG_PANEL_ALT, fg=TEXT_PRIMARY, font=FONT, relief="flat", borderwidth=0,
            state="disabled", highlightthickness=0)
        self._text.pack(fill="both", expand=True)

    def set_hint(self, title, text):
        self._title_var.set(title)
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.insert("1.0", text)
        self._text.configure(state="disabled")

    def clear(self):
        self._title_var.set("")
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def _toggle(self):
        if self._expanded:
            self._content_frame.pack_forget()
            self._toggle_btn.configure(text="▶ Hint")
        else:
            self._content_frame.pack(fill="both", expand=True, pady=(4, 0))
            self._toggle_btn.configure(text="▼ Hint")
        self._expanded = not self._expanded
