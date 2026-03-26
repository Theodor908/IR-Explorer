"""Compare panel: Jaccard similarity, shared terms, pairwise heatmap."""

import tkinter as tk
from tkinter import ttk

from collections import Counter
from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM,
    FONT, FONT_BOLD, FONT_SMALL, style_text, style_canvas
)
from ir_explorer.core.preprocessing import tokenize, remove_stopwords


class ComparePanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._doc_map = {}
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(top, text="Doc A:", font=FONT_BOLD).pack(side="left")
        self._doc_a_var = tk.StringVar(value="-- Load corpus & refresh --")
        self._combo_a = ttk.Combobox(top, textvariable=self._doc_a_var,
                                      state="readonly", width=40)
        self._combo_a.pack(side="left", padx=(4, 16))

        ttk.Label(top, text="Doc B:", font=FONT_BOLD).pack(side="left")
        self._doc_b_var = tk.StringVar(value="-- Load corpus & refresh --")
        self._combo_b = ttk.Combobox(top, textvariable=self._doc_b_var,
                                      state="readonly", width=40)
        self._combo_b.pack(side="left", padx=4)

        ttk.Button(top, text="Compare", command=self._compare).pack(side="left", padx=16)
        ttk.Button(top, text="Refresh Docs",
                   command=self._refresh_docs).pack(side="left")

        self._stats_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self._stats_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        left = ttk.Frame(pane)
        pane.add(left, weight=1)
        ttk.Label(left, text="Comparison Detail", font=FONT_BOLD).pack(anchor="w")
        self._detail = tk.Text(left, wrap="word", state="disabled")
        style_text(self._detail)
        self._detail.pack(fill="both", expand=True)

        right = ttk.Frame(pane)
        pane.add(right, weight=1)
        ttk.Label(right, text="Pairwise Jaccard Heatmap", font=FONT_BOLD).pack(anchor="w")
        self._heat_canvas = tk.Canvas(right)
        style_canvas(self._heat_canvas)
        self._heat_canvas.pack(fill="both", expand=True)
        ttk.Button(right, text="Draw Heatmap",
                   command=self._draw_heatmap).pack(pady=4)

    def _refresh_docs(self):
        ids = self.app.corpus.doc_ids()
        if not ids:
            self._combo_a["values"] = []
            self._combo_b["values"] = []
            self._doc_a_var.set("-- No documents loaded --")
            self._doc_b_var.set("-- No documents loaded --")
            self._doc_map = {}
            return
        display = []
        for d in ids:
            title = self.app.corpus.metadata.get(d, {}).get("title", "")
            display.append(f"{d}: {title}")
        self._combo_a["values"] = display
        self._combo_b["values"] = display
        self._doc_map = dict(zip(display, ids))
        if not self._doc_a_var.get() or self._doc_a_var.get().startswith("--"):
            self._doc_a_var.set("-- Select document A --")
        if not self._doc_b_var.get() or self._doc_b_var.get().startswith("--"):
            self._doc_b_var.set("-- Select document B --")

    def _compare(self):
        da = self._doc_map.get(self._doc_a_var.get())
        db = self._doc_map.get(self._doc_b_var.get())
        if not da or not db:
            return

        tokens_a = set(remove_stopwords(tokenize(self.app.corpus.docs[da])))
        tokens_b = set(remove_stopwords(tokenize(self.app.corpus.docs[db])))

        shared = tokens_a & tokens_b
        union = tokens_a | tokens_b
        jaccard = len(shared) / len(union) if union else 0

        self._stats_var.set(
            f"Jaccard({da}, {db}) = {jaccard:.4f} | "
            f"Shared: {len(shared)} terms | "
            f"|A|={len(tokens_a)}, |B|={len(tokens_b)}, |A\u222aB|={len(union)}"
        )

        tf_a = Counter(remove_stopwords(tokenize(self.app.corpus.docs[da])))
        tf_b = Counter(remove_stopwords(tokenize(self.app.corpus.docs[db])))

        lines = [
            f"Shared terms ({len(shared)}):",
            f"  {'Term':<25} {'TF in ' + da:>10} {'TF in ' + db:>10}",
            f"  {'-'*25} {'-'*10} {'-'*10}",
        ]
        for term in sorted(shared):
            lines.append(f"  {term:<25} {tf_a[term]:>10} {tf_b[term]:>10}")

        lines.append(f"\nOnly in {da} ({len(tokens_a - tokens_b)}):")
        for term in sorted(tokens_a - tokens_b)[:20]:
            lines.append(f"  {term}")
        if len(tokens_a - tokens_b) > 20:
            lines.append(f"  ... and {len(tokens_a - tokens_b) - 20} more")

        lines.append(f"\nOnly in {db} ({len(tokens_b - tokens_a)}):")
        for term in sorted(tokens_b - tokens_a)[:20]:
            lines.append(f"  {term}")
        if len(tokens_b - tokens_a) > 20:
            lines.append(f"  ... and {len(tokens_b - tokens_a) - 20} more")

        self._detail.configure(state="normal")
        self._detail.delete("1.0", "end")
        self._detail.insert("1.0", "\n".join(lines))
        self._detail.configure(state="disabled")

    def _draw_heatmap(self):
        c = self._heat_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width()
        h = c.winfo_height()

        ids = self.app.corpus.doc_ids()
        n = len(ids)
        if n == 0 or w < 50 or h < 50:
            return

        token_sets = {
            d: set(remove_stopwords(tokenize(self.app.corpus.docs[d])))
            for d in ids
        }

        margin = 50
        cell_w = (w - margin) / n
        cell_h = (h - margin) / n

        for i, da in enumerate(ids):
            c.create_text(margin - 4, margin + i * cell_h + cell_h / 2,
                          text=da, anchor="e", fill=TEXT_PRIMARY, font=FONT_SMALL)
            c.create_text(margin + i * cell_w + cell_w / 2, margin - 4,
                          text=da, anchor="s", fill=TEXT_PRIMARY, font=FONT_SMALL)
            for j, db in enumerate(ids):
                s = token_sets[da] & token_sets[db]
                u = token_sets[da] | token_sets[db]
                jac = len(s) / len(u) if u else 0

                r = int(0x0f + jac * (0x4f - 0x0f))
                g = int(0x11 + jac * (0x8f - 0x11))
                b_val = int(0x17 + jac * (0xf7 - 0x17))
                color = f"#{r:02x}{g:02x}{b_val:02x}"

                x = margin + j * cell_w
                y = margin + i * cell_h
                c.create_rectangle(x, y, x + cell_w, y + cell_h,
                                   fill=color, outline=BG_DEEP)

                if n <= 15:
                    text_color = TEXT_PRIMARY if jac > 0.15 else TEXT_SECONDARY
                    c.create_text(x + cell_w / 2, y + cell_h / 2,
                                  text=f"{jac:.2f}", fill=text_color,
                                  font=FONT_SMALL)
