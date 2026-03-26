"""Postings panel: DF distribution histogram, sortable term table."""

import tkinter as tk
from tkinter import ttk
from collections import Counter

from ir_explorer.ui.theme import (
    BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM, SUCCESS, WARNING,
    FONT, FONT_BOLD, FONT_SMALL, style_canvas
)


class PostingsPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._sort_col = "df"
        self._sort_rev = True
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Button(top, text="Refresh", command=self._refresh).pack(side="left")
        self._stats_var = tk.StringVar(value="Build index first")
        ttk.Label(top, textvariable=self._stats_var,
                  foreground=TEXT_SECONDARY).pack(side="left", padx=12)

        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        left = ttk.Frame(pane)
        pane.add(left, weight=1)
        ttk.Label(left, text="Postings List Length Distribution",
                  font=FONT_BOLD).pack(anchor="w")
        self._hist_canvas = tk.Canvas(left)
        style_canvas(self._hist_canvas)
        self._hist_canvas.pack(fill="both", expand=True)

        right = ttk.Frame(pane)
        pane.add(right, weight=1)

        cols = ("term", "df")
        self._tree = ttk.Treeview(right, columns=cols, show="headings")
        self._tree.heading("term", text="Term",
                           command=lambda: self._sort_by("term"))
        self._tree.heading("df", text="DF",
                           command=lambda: self._sort_by("df"))
        self._tree.column("term", width=200)
        self._tree.column("df", width=60, stretch=False)

        sb = ttk.Scrollbar(right, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._term_data = []

    def _refresh(self):
        if not self.app.index.index:
            return

        stats = self.app.index.stats()
        self._stats_var.set(
            f"{stats['num_terms']} terms | "
            f"avg DF: {stats['avg_postings_per_term']:.2f} | "
            f"max DF: {stats['max_df_term']} ({stats['max_df_value']}) | "
            f"DF=1: {stats['df1_count']} ({stats['df1_pct']:.1f}%)"
        )

        self._term_data = [
            (term, self.app.index.df(term))
            for term in self.app.index.vocabulary()
        ]

        self._populate_tree()
        self._draw_histogram()

    def _populate_tree(self):
        self._tree.delete(*self._tree.get_children())
        data = sorted(self._term_data,
                      key=lambda x: x[0] if self._sort_col == "term" else x[1],
                      reverse=self._sort_rev)
        for term, df in data:
            tag = "rare" if df == 1 else "common" if df >= 5 else ""
            self._tree.insert("", "end", values=(term, df), tags=(tag,))

        self._tree.tag_configure("rare", foreground=WARNING)
        self._tree.tag_configure("common", foreground=SUCCESS)

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = col == "df"
        self._populate_tree()

    def _draw_histogram(self):
        c = self._hist_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50 or h < 50 or not self._term_data:
            return

        df_counts = Counter(df for _, df in self._term_data)
        if not df_counts:
            return

        max_df = max(df_counts.keys())
        max_count = max(df_counts.values())

        margin_left = 50
        margin_bottom = 30
        margin_top = 10
        margin_right = 10
        plot_w = w - margin_left - margin_right
        plot_h = h - margin_top - margin_bottom

        num_bars = max_df
        bar_w = max(2, plot_w / (num_bars + 1))

        c.create_line(margin_left, h - margin_bottom,
                      w - margin_right, h - margin_bottom,
                      fill=TEXT_SECONDARY)
        c.create_line(margin_left, margin_top,
                      margin_left, h - margin_bottom,
                      fill=TEXT_SECONDARY)

        c.create_text(w / 2, h - 5, text="DF value",
                      fill=TEXT_SECONDARY, font=FONT_SMALL)
        c.create_text(10, h / 2, text="# terms",
                      fill=TEXT_SECONDARY, font=FONT_SMALL, angle=90)

        for df_val in range(1, max_df + 1):
            count = df_counts.get(df_val, 0)
            x = margin_left + (df_val - 0.5) * bar_w
            bar_h = (count / max_count) * plot_h if max_count > 0 else 0
            y_top = h - margin_bottom - bar_h

            c.create_rectangle(x, y_top, x + bar_w - 2, h - margin_bottom,
                               fill=ACCENT, outline="")
            c.create_text(x + bar_w / 2, h - margin_bottom + 10,
                          text=str(df_val), fill=TEXT_SECONDARY, font=FONT_SMALL)
            if count > 0:
                c.create_text(x + bar_w / 2, y_top - 8,
                              text=str(count), fill=TEXT_PRIMARY, font=FONT_SMALL)
