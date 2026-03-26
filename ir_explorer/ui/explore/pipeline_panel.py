"""Pipeline panel: step-by-step preprocessing visualization."""

import tkinter as tk
from tkinter import ttk

from ir_explorer.ui.theme import (
    BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, WARNING, SUCCESS,
    FONT, FONT_BOLD, FONT_HEADING, style_text
)
from ir_explorer.core.preprocessing import pipeline, STOPWORDS, stem


class PipelinePanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._doc_map = {}
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(top, text="Document:", font=FONT_BOLD).pack(side="left")
        self._doc_var = tk.StringVar(value="-- Load corpus & refresh --")
        self._doc_combo = ttk.Combobox(top, textvariable=self._doc_var,
                                        state="readonly", width=60)
        self._doc_combo.pack(side="left", padx=8)
        self._doc_combo.bind("<<ComboboxSelected>>", self._on_doc_change)

        ttk.Button(top, text="Refresh Docs",
                   command=self._refresh_docs).pack(side="left")

        self._stats_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self._stats_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        cols_frame = ttk.Frame(self)
        cols_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        cols_frame.columnconfigure(0, weight=1)
        cols_frame.columnconfigure(1, weight=1)
        cols_frame.columnconfigure(2, weight=1)

        headers = [
            ("Raw Tokens", "raw"),
            ("After Stopword Removal", "no_stop"),
            ("After Stemming", "stemmed")
        ]
        self._text_widgets = {}
        for col, (label, key) in enumerate(headers):
            ttk.Label(cols_frame, text=label, font=FONT_BOLD).grid(
                row=0, column=col, sticky="w", padx=4)
            text = tk.Text(cols_frame, wrap="word", width=30)
            style_text(text)
            text.grid(row=1, column=col, sticky="nsew", padx=4, pady=4)
            text.tag_configure("removed", foreground=WARNING,
                                overstrike=True)
            text.tag_configure("changed", foreground=SUCCESS)
            text.tag_configure("kept", foreground=TEXT_PRIMARY)
            self._text_widgets[key] = text

        cols_frame.rowconfigure(1, weight=1)

    def _refresh_docs(self):
        ids = self.app.corpus.doc_ids()
        if not ids:
            self._doc_combo["values"] = []
            self._doc_var.set("-- No documents loaded --")
            self._doc_map = {}
            return
        display = []
        for d in ids:
            title = self.app.corpus.metadata.get(d, {}).get("title", "")
            display.append(f"{d}: {title}")
        self._doc_combo["values"] = display
        self._doc_map = dict(zip(display, ids))
        if not self._doc_var.get() or self._doc_var.get() == "-- No documents loaded --":
            self._doc_var.set("-- Select a document --")

    def _on_doc_change(self, event=None):
        display = self._doc_var.get()
        doc_id = self._doc_map.get(display)
        if not doc_id:
            return

        text = self.app.corpus.docs[doc_id]
        result = pipeline(text)

        raw = result["raw"]
        no_stop = result["no_stop"]
        stemmed = result["stemmed"]

        reduction_stop = (1 - len(no_stop) / len(raw)) * 100 if raw else 0
        self._stats_var.set(
            f"Raw: {len(raw)} tokens | "
            f"After stopwords: {len(no_stop)} (-{reduction_stop:.0f}%) | "
            f"Stemmed: {len(stemmed)} tokens | "
            f"Unique raw: {len(set(raw))} | "
            f"Unique stemmed: {len(set(stemmed))}"
        )

        w = self._text_widgets["raw"]
        w.configure(state="normal")
        w.delete("1.0", "end")
        for token in raw:
            tag = "removed" if token in STOPWORDS else "kept"
            w.insert("end", token + "\n", tag)
        w.configure(state="disabled")

        w = self._text_widgets["no_stop"]
        w.configure(state="normal")
        w.delete("1.0", "end")
        for token in no_stop:
            w.insert("end", token + "\n", "kept")
        w.configure(state="disabled")

        w = self._text_widgets["stemmed"]
        w.configure(state="normal")
        w.delete("1.0", "end")
        for i, s_token in enumerate(stemmed):
            original = no_stop[i] if i < len(no_stop) else ""
            tag = "changed" if s_token != original else "kept"
            label = s_token if s_token == original else f"{s_token} (was: {original})"
            w.insert("end", label + "\n", tag)
        w.configure(state="disabled")
