"""Parameter controls and observable metrics display for experiment steps."""
import tkinter as tk
from tkinter import ttk

from ir_explorer.ui.theme import (
    BG_PANEL, BG_PANEL_ALT, BG_DEEP, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, ACCENT_DIM, SUCCESS,
    LEARN_ACCENT, LEARN_ACCENT_DIM,
    BUTTON_BG, BUTTON_HOVER,
    FONT, FONT_BOLD, FONT_SMALL,
)


class ExperimentPrompt(ttk.Frame):

    # Map widget keys to human-readable labels
    _WIDGET_LABELS = {
        "toggle_stopwords": "Toggle Stopwords",
        "toggle_stemming": "Toggle Stemming",
        "toggle_case": "Toggle Lowercasing",
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="TFrame")
        self._controls = {}       # widget_key -> tk widget
        self._metric_labels = {}  # metric_key -> tk.Label
        self._build()

    def _build(self):
        ctrl_hdr = tk.Label(
            self, text="Controls",
            bg=BG_PANEL, fg=TEXT_SECONDARY,
            font=FONT_SMALL, anchor="w", padx=8, pady=(8, 2),
        )
        ctrl_hdr.pack(fill="x")

        self._ctrl_frame = tk.Frame(self, bg=BG_PANEL)
        self._ctrl_frame.pack(fill="x", padx=8, pady=4)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", pady=4)

        obs_hdr = tk.Label(
            self, text="Observables",
            bg=BG_PANEL, fg=TEXT_SECONDARY,
            font=FONT_SMALL, anchor="w", padx=8, pady=(2, 2),
        )
        obs_hdr.pack(fill="x")

        self._obs_frame = tk.Frame(self, bg=BG_PANEL)
        self._obs_frame.pack(fill="x", padx=8, pady=4)

    def setup_widget(self, widget_key, command):
        for w in self._ctrl_frame.winfo_children():
            w.destroy()
        self._controls.clear()

        label_text = self._WIDGET_LABELS.get(widget_key, widget_key.replace("_", " ").title())

        var = tk.BooleanVar(value=False)

        def _toggle():
            command(var.get())

        cb = tk.Checkbutton(
            self._ctrl_frame,
            text=label_text,
            variable=var,
            command=_toggle,
            bg=BG_PANEL, fg=TEXT_PRIMARY,
            activebackground=BG_PANEL_ALT, activeforeground=TEXT_PRIMARY,
            selectcolor=LEARN_ACCENT_DIM,
            font=FONT, relief="flat", bd=0,
            cursor="hand2",
        )
        cb.pack(anchor="w", pady=2)
        self._controls[widget_key] = (var, cb)

    def set_observables(self, metrics_dict):
        for w in self._obs_frame.winfo_children():
            w.destroy()
        self._metric_labels.clear()

        for key, value in (metrics_dict or {}).items():
            row = tk.Frame(self._obs_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=1)

            k_lbl = tk.Label(
                row, text=f"{key}:",
                bg=BG_PANEL, fg=TEXT_SECONDARY,
                font=FONT_SMALL, anchor="w", width=20,
            )
            k_lbl.pack(side="left")

            v_lbl = tk.Label(
                row, text=str(value),
                bg=BG_PANEL, fg=SUCCESS,
                font=FONT_BOLD, anchor="w",
            )
            v_lbl.pack(side="left")
            self._metric_labels[key] = v_lbl
