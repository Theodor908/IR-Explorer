"""Search panel: Boolean and TF-IDF retrieval with result preview."""

import tkinter as tk
from tkinter import ttk, messagebox

from ir_explorer.ui.theme import (
    BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM,
    FONT, FONT_BOLD, style_text
)
from ir_explorer.core.retrieval import boolean_search, tfidf_rank
from ir_explorer.core.preprocessing import tokenize, STOPWORDS


class SearchPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._query_terms = set()
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(top, text="Query:", font=FONT_BOLD).pack(side="left")
        self._query_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self._query_var, width=50)
        entry.pack(side="left", padx=8, fill="x", expand=True)
        entry.bind("<Return>", lambda e: self._search())

        self._mode_var = tk.StringVar(value="tfidf")
        ttk.Radiobutton(top, text="TF-IDF", variable=self._mode_var,
                        value="tfidf").pack(side="left", padx=4)
        ttk.Radiobutton(top, text="Boolean", variable=self._mode_var,
                        value="boolean").pack(side="left", padx=4)

        ttk.Button(top, text="Search", command=self._search).pack(side="right")

        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        left = ttk.Frame(pane)
        pane.add(left, weight=1)
        self._result_tree = ttk.Treeview(
            left, columns=("doc_id", "title", "score"), show="headings"
        )
        self._result_tree.heading("doc_id", text="ID")
        self._result_tree.heading("title", text="Title")
        self._result_tree.heading("score", text="Score")
        self._result_tree.column("doc_id", width=40, stretch=False)
        self._result_tree.column("title", width=300)
        self._result_tree.column("score", width=70, stretch=False)
        self._result_tree.pack(fill="both", expand=True)
        self._result_tree.bind("<<TreeviewSelect>>", self._on_result_select)

        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._preview = tk.Text(right, wrap="word", state="disabled")
        style_text(self._preview)
        self._preview.tag_configure("highlight", background=ACCENT_DIM,
                                     foreground=TEXT_PRIMARY)
        self._preview.pack(fill="both", expand=True)

    def _search(self):
        query = self._query_var.get().strip()
        if not query:
            return
        if not self.app.index.index:
            messagebox.showwarning("No Index", "Build the index first (Index tab).")
            return

        self._result_tree.delete(*self._result_tree.get_children())

        mode = self._mode_var.get()
        if mode == "boolean":
            doc_ids = boolean_search(query, self.app.index)
            for doc_id in doc_ids:
                title = self.app.corpus.metadata.get(doc_id, {}).get("title", "")
                self._result_tree.insert("", "end", iid=doc_id,
                                         values=(doc_id, title, "\u2014"))
        else:
            results = tfidf_rank(query, self.app.index, self.app.corpus.docs)
            for doc_id, score in results:
                if score <= 0:
                    continue
                title = self.app.corpus.metadata.get(doc_id, {}).get("title", "")
                self._result_tree.insert("", "end", iid=doc_id,
                                         values=(doc_id, title, f"{score:.4f}"))

        self._query_terms = set(
            t for t in tokenize(query) if t not in STOPWORDS
        )

    def _on_result_select(self, event):
        sel = self._result_tree.selection()
        if not sel:
            return
        doc_id = sel[0]
        text = self.app.corpus.docs.get(doc_id, "")

        self._preview.configure(state="normal")
        self._preview.delete("1.0", "end")
        self._preview.insert("1.0", text)

        for term in self._query_terms:
            start = "1.0"
            while True:
                pos = self._preview.search(term, start, stopindex="end",
                                            nocase=True)
                if not pos:
                    break
                end_pos = f"{pos}+{len(term)}c"
                self._preview.tag_add("highlight", pos, end_pos)
                start = end_pos

        self._preview.configure(state="disabled")
