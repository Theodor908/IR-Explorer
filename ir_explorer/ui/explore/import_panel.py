"""Corpus panel: import, list, remove documents."""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, BG_PANEL_ALT, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM,
    BUTTON_BG, BUTTON_HOVER,
    FONT, FONT_BOLD, FONT_HEADING, style_frame, style_text
)
from ir_explorer.core.pdf_reader import extract_simple, extract_sections


class ImportPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Button(btn_bar, text="Import PDF",
                   command=self._import_pdf).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Import Text File",
                   command=self._import_txt).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Load Example Corpus",
                   command=self._load_example).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Generate Corpus",
                   command=self._generate_corpus).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Remove Selected",
                   command=self._remove_selected).pack(side="right", padx=(4, 0))
        ttk.Button(btn_bar, text="Clear All",
                   command=self._clear_all).pack(side="right", padx=4)

        self._status_var = tk.StringVar(value="No documents loaded")
        ttk.Label(self, textvariable=self._status_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        cols = ("doc_id", "title", "source", "words")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                 selectmode="extended")
        self.tree.heading("doc_id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("source", text="Source")
        self.tree.heading("words", text="Words")
        self.tree.column("doc_id", width=50, stretch=False)
        self.tree.column("title", width=400)
        self.tree.column("source", width=200)
        self.tree.column("words", width=70, stretch=False)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")

        edit_frame = tk.Frame(main_frame, bg=BG_DEEP)
        edit_frame.pack(fill="x", pady=(4, 0))

        edit_label = tk.Label(edit_frame, text="Document text (editable):",
                              bg=BG_DEEP, fg=TEXT_SECONDARY,
                              font=("Consolas", 8))
        edit_label.pack(anchor="w", padx=4, pady=(2, 0))

        self._preview = tk.Text(edit_frame, height=8, wrap="word")
        style_text(self._preview)
        self._preview.pack(fill="x")

        self._selected_doc_id = None
        self._preview.bind("<<Modified>>", self._on_text_modified)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for doc_id in self.app.corpus.doc_ids():
            meta = self.app.corpus.metadata[doc_id]
            words = self.app.corpus.word_count(doc_id)
            self.tree.insert("", "end", iid=doc_id, values=(
                doc_id, meta.get("title", ""), meta.get("source", ""), words
            ))
        n = len(self.app.corpus.docs)
        self._status_var.set(f"{n} document{'s' if n != 1 else ''} loaded")

    def _import_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not path:
            return

        win = tk.Toplevel(self)
        win.title("PDF Import Mode")
        win.configure(bg=BG_PANEL)
        win.geometry("380x250")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(
            win, text="How should the PDF be split?",
            bg=BG_PANEL, fg=TEXT_PRIMARY, font=("Consolas", 11, "bold"),
        ).pack(fill="x", padx=12, pady=(12, 4))

        tk.Label(
            win, text=os.path.basename(path),
            bg=BG_PANEL, fg=TEXT_SECONDARY, font=("Consolas", 9),
        ).pack(fill="x", padx=12, pady=(0, 8))

        mode_var = tk.StringVar(value="subtitles")
        modes = [
            ("Split on titles + subtitles (most documents)", "subtitles"),
            ("Split on major titles only (fewer, larger docs)", "titles"),
            ("Import as single document (no split)", "single"),
        ]
        for text, val in modes:
            tk.Radiobutton(
                win, text=text, variable=mode_var, value=val,
                bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=ACCENT_DIM,
                activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY,
                font=("Consolas", 9), anchor="w",
            ).pack(fill="x", padx=16, pady=2)

        btn_frame = tk.Frame(win, bg=BG_PANEL)
        btn_frame.pack(side="bottom", fill="x", padx=12, pady=(8, 12))

        tk.Button(
            btn_frame, text="Cancel", bg=BUTTON_BG, fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER, activeforeground=TEXT_PRIMARY,
            font=("Consolas", 9), relief="flat", padx=10, pady=4,
            command=win.destroy,
        ).pack(side="right", padx=(4, 0))

        def _do_import():
            mode = mode_var.get()
            win.destroy()
            try:
                if mode == "single":
                    text = extract_simple(path)
                    doc_id = self.app.corpus.next_id()
                    self.app.corpus.add(
                        doc_id, text,
                        title=os.path.basename(path),
                        source=os.path.basename(path)
                    )
                else:
                    sections = extract_sections(path, split_on=mode)
                    for sec in sections:
                        doc_id = self.app.corpus.next_id()
                        self.app.corpus.add(
                            doc_id, sec["text"],
                            title=sec["title"],
                            source=os.path.basename(path)
                        )
                self.refresh()
            except Exception as e:
                messagebox.showerror("Import Error", str(e))

        tk.Button(
            btn_frame, text="Import", bg=ACCENT_DIM, fg=TEXT_PRIMARY,
            activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
            font=("Consolas", 9, "bold"), relief="flat", padx=14, pady=4,
            command=_do_import,
        ).pack(side="right")

    def _import_txt(self):
        path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            doc_id = self.app.corpus.next_id()
            self.app.corpus.add(
                doc_id, text,
                title=os.path.basename(path),
                source=os.path.basename(path)
            )
            self.refresh()
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _load_example(self):
        corpora_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets", "corpora"
        )
        if not os.path.isdir(corpora_dir):
            messagebox.showerror("Error", "No example corpora found")
            return
        files = [f for f in os.listdir(corpora_dir) if f.endswith(".json")]
        if not files:
            messagebox.showerror("Error", "No example corpora found")
            return

        win = tk.Toplevel(self)
        win.title("Load Example Corpus")
        win.configure(bg=BG_PANEL)
        win.geometry("440x420")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(
            win, text="Load Example Corpus",
            bg=BG_PANEL, fg=TEXT_PRIMARY, font=("Consolas", 11, "bold"),
        ).pack(fill="x", padx=12, pady=(12, 4))

        tk.Label(
            win, text="Select a curated corpus designed to demonstrate\n"
                      "specific IR concepts. This replaces the current corpus.",
            bg=BG_PANEL, fg=TEXT_SECONDARY, font=("Consolas", 9),
            justify="left",
        ).pack(fill="x", padx=12, pady=(0, 8))

        list_frame = tk.Frame(win, bg=BG_PANEL)
        list_frame.pack(fill="both", expand=True, padx=12, pady=4)

        from ir_explorer.ui.theme import style_listbox as _style_lb
        lb = tk.Listbox(list_frame, selectmode="single")
        _style_lb(lb)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=scrollbar.set)
        lb.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sort so that academic_papers comes first
        files.sort(key=lambda f: (0 if f.startswith("academic") else 1, f))

        display_names = []
        for f in files:
            name = f.replace("_corpus.json", "").replace("_", " ").title()
            display_names.append(name)
            lb.insert("end", name)

        descriptions = {
            "Academic Papers": "80 documents from 15 landmark papers across 7 domains: AI, physics, "
                               "biology, climate science, information theory, neuroscience, and philosophy. "
                               "Includes 12 predefined evaluation queries with ground-truth relevance — "
                               "use the Evaluation tab to compute P@5, P@10, MAP, and PR curves.",
            "Synonyms": "8 documents with synonym groups (car/automobile/vehicle, big/large/enormous). "
                        "Demonstrates why stemming and vocabulary normalization matter.",
            "Link Structure": "10 documents about web IR topics with a hand-crafted citation graph. "
                              "Best for Crawler and Link Analysis tabs — produces interesting PageRank scores.",
        }

        def _on_load():
            sel = lb.curselection()
            if not sel:
                return
            path = os.path.join(corpora_dir, files[sel[0]])
            self.app.corpus.clear()
            self.app.corpus.load_from_json(path)
            self.refresh()
            win.destroy()

        # pack buttons first so they're never covered
        btn_frame = tk.Frame(win, bg=BG_PANEL)
        btn_frame.pack(side="bottom", fill="x", padx=12, pady=(8, 12))

        tk.Button(
            btn_frame, text="Cancel",
            bg=BUTTON_BG, fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER, activeforeground=TEXT_PRIMARY,
            font=("Consolas", 9), relief="flat", padx=10, pady=4,
            command=win.destroy,
        ).pack(side="right", padx=(4, 0))

        tk.Button(
            btn_frame, text="Load",
            bg=ACCENT_DIM, fg=TEXT_PRIMARY,
            activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
            font=("Consolas", 9, "bold"), relief="flat", padx=14, pady=4,
            command=_on_load,
        ).pack(side="right")

        desc_var = tk.StringVar(value="Select a corpus to see its description.")
        desc_frame = tk.Frame(win, bg=BG_PANEL_ALT, padx=8, pady=8)
        desc_frame.pack(side="bottom", fill="x", padx=12, pady=(4, 0))
        tk.Label(
            desc_frame, textvariable=desc_var,
            bg=BG_PANEL_ALT, fg=TEXT_PRIMARY, font=("Consolas", 9),
            wraplength=400, justify="left",
        ).pack(fill="x")

        def _on_select_change(event=None):
            sel = lb.curselection()
            if sel:
                name = display_names[sel[0]]
                desc_var.set(descriptions.get(name, ""))

        lb.bind("<<ListboxSelect>>", _on_select_change)
        lb.bind("<Double-1>", lambda e: _on_load())

    def _generate_corpus(self):
        from ir_explorer.core.corpus_generator import generate_corpus

        win = tk.Toplevel(self)
        win.title("Generate Corpus")
        win.configure(bg=BG_PANEL)
        win.geometry("420x400")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(
            win, text="Generate Synthetic Corpus",
            bg=BG_PANEL, fg=TEXT_PRIMARY, font=("Consolas", 11, "bold"),
        ).pack(fill="x", padx=12, pady=(12, 4))

        tk.Label(
            win, text="Create a corpus with controllable properties for\n"
                      "experimentation. This replaces the current corpus.",
            bg=BG_PANEL, fg=TEXT_SECONDARY, font=("Consolas", 9),
            justify="left",
        ).pack(fill="x", padx=12, pady=(0, 12))

        def _param_row(parent, label, desc, var, from_, to, resolution=1):
            frame = tk.Frame(parent, bg=BG_PANEL)
            frame.pack(fill="x", padx=12, pady=(0, 8))
            top = tk.Frame(frame, bg=BG_PANEL)
            top.pack(fill="x")
            tk.Label(top, text=label, bg=BG_PANEL, fg=TEXT_PRIMARY,
                     font=("Consolas", 9, "bold")).pack(side="left")
            readout = tk.Label(top, text=str(var.get()), bg=BG_PANEL,
                               fg=ACCENT, font=("Consolas", 9, "bold"))
            readout.pack(side="right")
            if desc:
                tk.Label(frame, text=desc, bg=BG_PANEL, fg=TEXT_SECONDARY,
                         font=("Consolas", 8), anchor="w").pack(fill="x")
            scale = ttk.Scale(frame, from_=from_, to=to, variable=var,
                              orient="horizontal")
            scale.pack(fill="x", pady=(2, 0))

            def _update(val):
                v = round(float(val) / resolution) * resolution
                readout.configure(text=str(int(v) if resolution >= 1 else f"{v:.2f}"))
            scale.configure(command=_update)
            return frame

        num_var = tk.IntVar(value=10)
        _param_row(win, "Number of documents", "How many documents to create (3-50)",
                   num_var, 3, 50)

        len_var = tk.IntVar(value=50)
        _param_row(win, "Average doc length", "Words per document (20-200)",
                   len_var, 20, 200)

        overlap_var = tk.IntVar(value=50)
        _param_row(win, "Vocabulary overlap %",
                   "0% = distinct topics per doc, 100% = all same vocabulary",
                   overlap_var, 0, 100)

        seed_frame = tk.Frame(win, bg=BG_PANEL)
        seed_frame.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(seed_frame, text="Random seed", bg=BG_PANEL, fg=TEXT_PRIMARY,
                 font=("Consolas", 9, "bold")).pack(side="left")
        seed_var = tk.IntVar(value=42)
        seed_entry = tk.Entry(
            seed_frame, textvariable=seed_var, width=8,
            bg=BG_DEEP, fg=TEXT_PRIMARY, font=("Consolas", 9),
            insertbackground=TEXT_PRIMARY, relief="flat",
            highlightbackground=BORDER, highlightthickness=1,
        )
        seed_entry.pack(side="right")
        tk.Label(seed_frame, text="For reproducibility in class",
                 bg=BG_PANEL, fg=TEXT_SECONDARY,
                 font=("Consolas", 8)).pack(side="left", padx=(8, 0))

        btn_frame = tk.Frame(win, bg=BG_PANEL)
        btn_frame.pack(fill="x", padx=12, pady=(12, 12))

        tk.Button(
            btn_frame, text="Cancel",
            bg=BUTTON_BG, fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER, activeforeground=TEXT_PRIMARY,
            font=("Consolas", 9), relief="flat", padx=10, pady=4,
            command=win.destroy,
        ).pack(side="right", padx=(4, 0))

        def _on_generate():
            result = generate_corpus(
                num_docs=int(num_var.get()),
                avg_length=int(len_var.get()),
                vocab_overlap=overlap_var.get() / 100.0,
                seed=int(seed_var.get())
            )
            self.app.corpus.clear()
            for doc_id, info in result["documents"].items():
                self.app.corpus.add(doc_id, info["text"],
                                    title=info["title"], source=info["source"])
            self.refresh()
            win.destroy()

        tk.Button(
            btn_frame, text="Generate",
            bg=ACCENT_DIM, fg=TEXT_PRIMARY,
            activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
            font=("Consolas", 9, "bold"), relief="flat", padx=14, pady=4,
            command=_on_generate,
        ).pack(side="right")

    def _remove_selected(self):
        for item in self.tree.selection():
            self.app.corpus.remove(item)
        self.refresh()

    def _clear_all(self):
        if not self.app.corpus.docs:
            return
        if messagebox.askyesno("Confirm", "Remove all documents?"):
            self.app.corpus.clear()
            self.refresh()

    def _on_select(self, event):
        self._save_current_edit()

        sel = self.tree.selection()
        self._preview.delete("1.0", "end")
        if sel:
            doc_id = sel[0]
            self._selected_doc_id = doc_id
            text = self.app.corpus.docs.get(doc_id, "")
            self._preview.insert("1.0", text)
            self._preview.configure(state="normal")
        else:
            self._selected_doc_id = None
            self._preview.configure(state="disabled")
        self._preview.edit_modified(False)

    def _on_text_modified(self, event=None):
        if not self._preview.edit_modified():
            return
        self._save_current_edit()
        self._preview.edit_modified(False)

    def _save_current_edit(self):
        if self._selected_doc_id and self._selected_doc_id in self.app.corpus.docs:
            new_text = self._preview.get("1.0", "end-1c")
            self.app.corpus.docs[self._selected_doc_id] = new_text
            try:
                meta = self.app.corpus.metadata[self._selected_doc_id]
                words = len(new_text.split())
                self.tree.item(self._selected_doc_id, values=(
                    self._selected_doc_id,
                    meta.get("title", ""),
                    meta.get("source", ""),
                    words,
                ))
            except tk.TclError:
                pass
