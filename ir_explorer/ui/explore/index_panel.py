"""Index panel: browse inverted index, filter terms, view postings."""

import tkinter as tk
from tkinter import ttk, messagebox

from ir_explorer.ui.theme import (
    BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT,
    FONT, FONT_BOLD, FONT_HEADING, style_text, style_listbox
)


class IndexPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Button(top, text="Build Index",
                   command=self._build_index).pack(side="left")
        self._stats_var = tk.StringVar(value="No index built")
        ttk.Label(top, textvariable=self._stats_var,
                  foreground=TEXT_SECONDARY).pack(side="left", padx=12)

        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        ttk.Label(left, text="Filter:", font=FONT).pack(anchor="w")
        self._filter_var = tk.StringVar()
        self._filter_var.trace_add("write", self._on_filter)
        filter_entry = ttk.Entry(left, textvariable=self._filter_var)
        filter_entry.pack(fill="x", pady=(0, 4))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True)
        self._term_list = tk.Listbox(list_frame)
        style_listbox(self._term_list)
        sb = ttk.Scrollbar(list_frame, orient="vertical",
                           command=self._term_list.yview)
        self._term_list.configure(yscrollcommand=sb.set)
        self._term_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._term_list.bind("<<ListboxSelect>>", self._on_term_select)

        right = ttk.Frame(pane)
        pane.add(right, weight=2)

        self._detail = tk.Text(right, wrap="word", state="disabled")
        style_text(self._detail)
        self._detail.pack(fill="both", expand=True)

        self._all_terms = []

    def _build_index(self):
        if not self.app.corpus.docs:
            messagebox.showwarning("No Corpus", "Load documents first.")
            return
        self.app.rebuild_index()
        self._refresh_term_list()
        stats = self.app.index.stats()
        self._stats_var.set(
            f"{stats['num_terms']} terms | "
            f"{stats['num_documents']} docs | "
            f"{stats['total_postings']} postings | "
            f"avg {stats['avg_postings_per_term']:.1f}/term"
        )

    def _refresh_term_list(self):
        self._all_terms = self.app.index.vocabulary()
        self._apply_filter()

    def _on_filter(self, *_):
        self._apply_filter()

    def _apply_filter(self):
        self._term_list.delete(0, "end")
        pattern = self._filter_var.get().lower()
        for term in self._all_terms:
            if pattern in term:
                self._term_list.insert("end", term)

    def _on_term_select(self, event):
        sel = self._term_list.curselection()
        if not sel:
            return
        term = self._term_list.get(sel[0])
        postings = self.app.index.get_postings(term)
        df = self.app.index.df(term)

        lines = [
            f"Term: {term}",
            f"Document Frequency (DF): {df}",
            f"Postings list: {postings}",
            "",
            "--- Document excerpts ---",
        ]
        for doc_id in postings:
            text = self.app.corpus.docs.get(doc_id, "")
            meta = self.app.corpus.metadata.get(doc_id, {})
            title = meta.get("title", doc_id)
            lower_text = text.lower()
            idx = lower_text.find(term)
            if idx >= 0:
                start = max(0, idx - 60)
                end = min(len(text), idx + len(term) + 60)
                snippet = "..." + text[start:end] + "..."
            else:
                snippet = text[:120] + "..."
            lines.append(f"\n[{doc_id}] {title}")
            lines.append(f"  {snippet}")

        self._detail.configure(state="normal")
        self._detail.delete("1.0", "end")
        self._detail.insert("1.0", "\n".join(lines))
        self._detail.configure(state="disabled")
