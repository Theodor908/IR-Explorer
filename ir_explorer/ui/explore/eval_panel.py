"""Evaluation panel: relevance judgments and precision-recall curve."""

import tkinter as tk
from tkinter import ttk, messagebox

from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM,
    SUCCESS, WARNING, ERROR,
    FONT, FONT_BOLD, FONT_SMALL, style_canvas
)
from ir_explorer.ui.widgets.hint_box import HintBox
import json
from ir_explorer.core.retrieval import tfidf_rank
from ir_explorer.core.evaluation import (
    precision_at_k, average_precision, precision_recall_curve
)


class EvalPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._results = []       # list of (doc_id, score)
        self._relevant = set()   # doc_ids marked relevant by user
        self._build_ui()

    def _load_queries_file(self):
        """Load predefined queries from default_queries.json."""
        import os
        queries_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "default_queries.json"
        )
        if not os.path.exists(queries_path):
            return []
        with open(queries_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("queries", [])

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(top, text="Query:", font=FONT_BOLD).pack(side="left")
        self._query_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self._query_var, width=50)
        entry.pack(side="left", padx=8, fill="x", expand=True)
        entry.bind("<Return>", lambda e: self._run_query())

        ttk.Button(top, text="Run Query", command=self._run_query).pack(side="left", padx=4)
        ttk.Button(top, text="Compute Metrics", command=self._compute_metrics).pack(side="left", padx=4)

        # Predefined queries row
        predef_row = ttk.Frame(self)
        predef_row.pack(fill="x", padx=8, pady=(2, 2))

        ttk.Label(predef_row, text="Predefined:", font=FONT_BOLD).pack(side="left")

        self._predefined_queries = self._load_queries_file()
        query_labels = ["-- Select --"] + [
            f"{q['id']}: {q['description']}" for q in self._predefined_queries
        ]
        self._predef_var = tk.StringVar(value=query_labels[0])
        predef_combo = ttk.Combobox(
            predef_row, textvariable=self._predef_var,
            values=query_labels, state="readonly", width=50,
        )
        predef_combo.pack(side="left", padx=8)
        predef_combo.bind("<<ComboboxSelected>>", self._on_predef_selected)

        ttk.Button(
            predef_row, text="Run All Queries", command=self._run_all_predefined
        ).pack(side="left", padx=4)

        self._status_var = tk.StringVar(value="Enter a query and click Run Query.")
        ttk.Label(self, textvariable=self._status_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=8, pady=(4, 4))

        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        ttk.Label(left, text="Ranked Results  (check = relevant)", font=FONT_BOLD).pack(anchor="w")

        tree_frame = ttk.Frame(left)
        tree_frame.pack(fill="both", expand=True)

        cols = ("rank", "doc_id", "title", "score", "relevant")
        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                  selectmode="browse")
        self._tree.heading("rank",     text="#")
        self._tree.heading("doc_id",   text="ID")
        self._tree.heading("title",    text="Title")
        self._tree.heading("score",    text="Score")
        self._tree.heading("relevant", text="Relevant")
        self._tree.column("rank",     width=35,  stretch=False)
        self._tree.column("doc_id",   width=50,  stretch=False)
        self._tree.column("title",    width=260)
        self._tree.column("score",    width=70,  stretch=False)
        self._tree.column("relevant", width=70,  stretch=False)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="right")

        self._tree.bind("<ButtonRelease-1>", self._on_tree_click)

        right = ttk.Frame(pane)
        pane.add(right, weight=1)

        ttk.Label(right, text="Precision-Recall Curve", font=FONT_BOLD).pack(anchor="w")

        self._pr_canvas = tk.Canvas(right, height=220)
        style_canvas(self._pr_canvas)
        self._pr_canvas.pack(fill="both", expand=True)

        metrics_frame = ttk.Frame(right)
        metrics_frame.pack(fill="x", pady=(6, 4))

        self._p5_var  = tk.StringVar(value="P@5:  —")
        self._p10_var = tk.StringVar(value="P@10: —")
        self._ap_var  = tk.StringVar(value="AP:   —")
        for var in (self._p5_var, self._p10_var, self._ap_var):
            ttk.Label(metrics_frame, textvariable=var,
                      font=FONT_BOLD, foreground=ACCENT).pack(side="left", padx=12)

        self._hint = HintBox(self)
        self._hint.pack(fill="x", padx=8, pady=(4, 8))
        self._hint.set_hint(
            "How Evaluation Works",
            "1. Run a query to retrieve ranked documents using TF-IDF cosine similarity.\n"
            "2. Click a row in the results table to toggle its relevance (marked with ✓).\n"
            "3. Click 'Compute Metrics' to see P@5, P@10, Average Precision, and the "
            "Precision-Recall curve drawn on the canvas."
        )

    def _run_query(self):
        query = self._query_var.get().strip()
        if not query:
            return
        if not self.app.index.index:
            messagebox.showwarning("No Index", "Build the index first (Index tab).")
            return

        self._relevant.clear()

        # Auto-detect if query matches a predefined query
        predef_match = None
        for q in self._predefined_queries:
            if q["text"].strip() == query:
                predef_match = q
                break

        results = tfidf_rank(query, self.app.index, self.app.corpus.docs,
                             self.app.pipeline_config)
        self._results = results

        if predef_match:
            self._relevant = set(predef_match["relevant"])

        self._tree.delete(*self._tree.get_children())
        for rank, (doc_id, score) in enumerate(results, 1):
            if score <= 0:
                continue
            title = self.app.corpus.metadata.get(doc_id, {}).get("title", "")
            mark = "✓" if doc_id in self._relevant else ""
            self._tree.insert("", "end", iid=doc_id, values=(
                rank, doc_id, title, f"{score:.4f}", mark
            ))

        n = sum(1 for _, s in results if s > 0)
        if predef_match:
            self._status_var.set(
                f"Retrieved {n} documents. {len(self._relevant)} relevant docs auto-marked from {predef_match['id']}."
            )
        else:
            self._status_var.set(f"Retrieved {n} documents.  Click rows to mark relevant.")

        self._p5_var.set("P@5:  —")
        self._p10_var.set("P@10: —")
        self._ap_var.set("AP:   —")
        self._pr_canvas.delete("all")

    def _on_tree_click(self, event):
        row = self._tree.identify_row(event.y)
        if not row:
            return
        doc_id = row
        if doc_id in self._relevant:
            self._relevant.discard(doc_id)
            mark = ""
        else:
            self._relevant.add(doc_id)
            mark = "✓"
        current = self._tree.item(doc_id, "values")
        self._tree.item(doc_id, values=(current[0], current[1], current[2], current[3], mark))

    def _on_predef_selected(self, event=None):
        """Load selected predefined query: fill search box and mark relevant docs."""
        sel = self._predef_var.get()
        if sel.startswith("--"):
            return

        query_id = sel.split(":")[0].strip()
        query_data = None
        for q in self._predefined_queries:
            if q["id"] == query_id:
                query_data = q
                break
        if not query_data:
            return

        self._query_var.set(query_data["text"])
        self._run_query()

        self._relevant = set(query_data["relevant"])
        for item in self._tree.get_children():
            current = self._tree.item(item, "values")
            mark = "✓" if item in self._relevant else ""
            self._tree.item(item, values=(current[0], current[1], current[2], current[3], mark))

        self._status_var.set(
            f"Loaded {query_data['id']}: {len(self._relevant)} relevant docs marked. "
            f"Click 'Compute Metrics' to evaluate."
        )

    def _run_all_predefined(self):
        """Run all predefined queries and display summary in a popup."""
        if not self._predefined_queries:
            messagebox.showinfo("No Queries", "No predefined queries found.")
            return
        if not self.app.index.index:
            messagebox.showwarning("No Index", "Build the index first (Index tab).")
            return

        from ir_explorer.core.evaluation import mean_average_precision

        all_results = []
        map_pairs = []
        for q in self._predefined_queries:
            results = tfidf_rank(
                q["text"], self.app.index, self.app.corpus.docs,
                self.app.pipeline_config,
            )
            retrieved = [doc_id for doc_id, score in results if score > 0]
            relevant = set(q["relevant"])

            p5 = precision_at_k(retrieved, relevant, 5)
            p10 = precision_at_k(retrieved, relevant, 10)
            ap = average_precision(retrieved, relevant)
            all_results.append((q["id"], q["description"][:30], p5, p10, ap))
            map_pairs.append((retrieved, relevant))

        map_score = mean_average_precision(map_pairs)

        win = tk.Toplevel(self)
        win.title("All Queries -- Evaluation Results")
        win.geometry("700x450")
        win.configure(bg=BG_DEEP)

        cols = ("id", "description", "p5", "p10", "ap")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
        tree.heading("id", text="Query")
        tree.heading("description", text="Description")
        tree.heading("p5", text="P@5")
        tree.heading("p10", text="P@10")
        tree.heading("ap", text="AP")
        tree.column("id", width=50, stretch=False)
        tree.column("description", width=250)
        tree.column("p5", width=70, stretch=False)
        tree.column("p10", width=70, stretch=False)
        tree.column("ap", width=70, stretch=False)

        for qid, desc, p5, p10, ap in all_results:
            tree.insert("", "end", values=(qid, desc, f"{p5:.4f}", f"{p10:.4f}", f"{ap:.4f}"))

        tree.insert("", "end", values=("", "MAP", "", "", f"{map_score:.4f}"))
        tree.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(
            win, text=f"Mean Average Precision (MAP): {map_score:.4f}",
            font=FONT_BOLD, foreground=ACCENT,
        ).pack(pady=(0, 8))

    def _compute_metrics(self):
        if not self._results:
            messagebox.showwarning("No Results", "Run a query first.")
            return

        retrieved = [doc_id for doc_id, score in self._results if score > 0]
        relevant  = self._relevant

        p5  = precision_at_k(retrieved, relevant, 5)
        p10 = precision_at_k(retrieved, relevant, 10)
        ap  = average_precision(retrieved, relevant)

        self._p5_var.set(f"P@5:  {p5:.4f}")
        self._p10_var.set(f"P@10: {p10:.4f}")
        self._ap_var.set(f"AP:   {ap:.4f}")

        points = precision_recall_curve(retrieved, relevant)
        self._draw_pr_curve(points)

    def _draw_pr_curve(self, points):
        c = self._pr_canvas
        c.delete("all")
        c.update_idletasks()
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 40 or H < 40 or not points:
            return

        ml, mr, mt, mb = 45, 15, 15, 35   # margins
        pw = W - ml - mr
        ph = H - mt - mb

        c.create_line(ml, mt, ml, mt + ph, fill=TEXT_SECONDARY, width=1)
        c.create_line(ml, mt + ph, ml + pw, mt + ph, fill=TEXT_SECONDARY, width=1)

        c.create_text(ml + pw // 2, H - 6, text="Recall", fill=TEXT_SECONDARY, font=FONT_SMALL)
        c.create_text(10, mt + ph // 2, text="Precision", fill=TEXT_SECONDARY,
                      font=FONT_SMALL, angle=90)

        for i in range(0, 11, 2):
            frac = i / 10
            x = ml + int(frac * pw)
            y = mt + int((1 - frac) * ph)
            c.create_line(x, mt + ph, x, mt + ph + 4, fill=TEXT_SECONDARY)
            c.create_text(x, mt + ph + 10, text=f"{frac:.1f}", fill=TEXT_SECONDARY,
                          font=FONT_SMALL)
            c.create_line(ml - 4, y, ml, y, fill=TEXT_SECONDARY)
            c.create_text(ml - 8, y, text=f"{frac:.1f}", fill=TEXT_SECONDARY,
                          font=FONT_SMALL, anchor="e")

        coords = []
        for recall, precision in points:
            px = ml + int(recall * pw)
            py = mt + int((1 - precision) * ph)
            coords.append((px, py))

        if len(coords) >= 2:
            flat = []
            for px, py in coords:
                flat.extend([px, py])
            c.create_line(*flat, fill=ACCENT, width=2, smooth=False)

        for px, py in coords:
            c.create_oval(px - 3, py - 3, px + 3, py + 3,
                          fill=ACCENT, outline=BG_DEEP)
