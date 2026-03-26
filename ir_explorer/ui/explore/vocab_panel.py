"""Vocabulary panel: term frequency charts, Zipf's law, stopword impact."""

import math
import tkinter as tk
from tkinter import ttk

from collections import Counter
from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM,
    FONT, FONT_BOLD, FONT_SMALL, style_canvas
)
from ir_explorer.core.preprocessing import tokenize, remove_stopwords, STOPWORDS


class VocabPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Button(ctrl, text="Analyze", command=self._analyze).pack(side="left")

        ttk.Label(ctrl, text="Top N:").pack(side="left", padx=(16, 4))
        self._topn_var = tk.IntVar(value=20)
        ttk.Spinbox(ctrl, from_=5, to=100, width=5,
                     textvariable=self._topn_var).pack(side="left")

        self._stopword_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text="Remove stopwords",
                        variable=self._stopword_var).pack(side="left", padx=16)

        self._stats_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self._stats_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        chart_pane = ttk.PanedWindow(self, orient="horizontal")
        chart_pane.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        left = ttk.Frame(chart_pane)
        chart_pane.add(left, weight=1)
        ttk.Label(left, text="Term Frequency (Top N)",
                  font=FONT_BOLD).pack(anchor="w")
        self._bar_canvas = tk.Canvas(left)
        style_canvas(self._bar_canvas)
        self._bar_canvas.pack(fill="both", expand=True)

        right = ttk.Frame(chart_pane)
        chart_pane.add(right, weight=1)
        ttk.Label(right, text="Zipf's Law (log-log)",
                  font=FONT_BOLD).pack(anchor="w")
        self._zipf_canvas = tk.Canvas(right)
        style_canvas(self._zipf_canvas)
        self._zipf_canvas.pack(fill="both", expand=True)

    def _analyze(self):
        if not self.app.corpus.docs:
            return

        remove_stop = self._stopword_var.get()
        top_n = self._topn_var.get()

        all_tokens = []
        for text in self.app.corpus.docs.values():
            tokens = tokenize(text)
            if remove_stop:
                tokens = remove_stopwords(tokens)
            all_tokens.extend(tokens)

        freq = Counter(all_tokens)
        total = len(all_tokens)
        vocab_size = len(freq)
        hapax = sum(1 for f in freq.values() if f == 1)

        label = "stopwords removed" if remove_stop else "stopwords included"
        self._stats_var.set(
            f"Total tokens: {total:,} | "
            f"Vocabulary: {vocab_size:,} | "
            f"Hapax legomena: {hapax:,} ({100*hapax/vocab_size:.1f}%) | "
            f"({label})"
        )

        top_terms = freq.most_common(top_n)
        self._draw_bar_chart(top_terms)
        self._draw_zipf(freq)

    def _draw_bar_chart(self, top_terms):
        c = self._bar_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50 or h < 50 or not top_terms:
            return

        margin_left = 100
        margin_right = 10
        margin_top = 10
        margin_bottom = 10
        bar_area_w = w - margin_left - margin_right
        bar_area_h = h - margin_top - margin_bottom
        n = len(top_terms)
        bar_h = max(2, (bar_area_h - n) / n)
        max_freq = top_terms[0][1]

        for i, (term, freq) in enumerate(top_terms):
            y = margin_top + i * (bar_h + 1)
            bar_w = (freq / max_freq) * bar_area_w
            c.create_rectangle(
                margin_left, y, margin_left + bar_w, y + bar_h,
                fill=ACCENT, outline=""
            )
            c.create_text(
                margin_left - 4, y + bar_h / 2,
                text=term, anchor="e", fill=TEXT_PRIMARY, font=FONT_SMALL
            )
            c.create_text(
                margin_left + bar_w + 4, y + bar_h / 2,
                text=str(freq), anchor="w", fill=TEXT_SECONDARY, font=FONT_SMALL
            )

    def _draw_zipf(self, freq):
        c = self._zipf_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50 or h < 50 or not freq:
            return

        margin = 50
        plot_w = w - 2 * margin
        plot_h = h - 2 * margin

        ranked = sorted(freq.values(), reverse=True)
        n = len(ranked)
        if n < 2:
            return

        max_log_rank = math.log(n)
        max_log_freq = math.log(ranked[0])
        min_log_freq = math.log(max(ranked[-1], 1))

        c.create_line(margin, margin, margin, h - margin,
                      fill=TEXT_SECONDARY, width=1)
        c.create_line(margin, h - margin, w - margin, h - margin,
                      fill=TEXT_SECONDARY, width=1)
        c.create_text(w / 2, h - 5, text="log(rank)", fill=TEXT_SECONDARY,
                      font=FONT_SMALL)
        c.create_text(10, h / 2, text="log(freq)", fill=TEXT_SECONDARY,
                      font=FONT_SMALL, angle=90)

        log_range = max_log_freq - min_log_freq
        if log_range == 0:
            log_range = 1

        for rank, f in enumerate(ranked, 1):
            lr = math.log(rank)
            lf = math.log(max(f, 1))
            x = margin + (lr / max_log_rank) * plot_w
            y = (h - margin) - ((lf - min_log_freq) / log_range) * plot_h
            c.create_oval(x - 2, y - 2, x + 2, y + 2, fill=ACCENT, outline="")
