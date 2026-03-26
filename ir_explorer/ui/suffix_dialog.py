"""Suffix settings dialog."""

import tkinter as tk
from tkinter import ttk, messagebox
from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, BG_PANEL_ALT, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, ACCENT_DIM, SUCCESS, ERROR,
    BUTTON_BG, BUTTON_HOVER,
    FONT, FONT_BOLD, FONT_HEADING,
    style_listbox,
)
from ir_explorer.core.preprocessing import (
    get_suffixes, set_suffixes, reset_suffixes, _DEFAULT_SUFFIXES,
)


class SuffixDialog(tk.Toplevel):

    def __init__(self, parent, on_apply=None):
        super().__init__(parent)
        self.title("Stemmer Suffix Settings")
        self.configure(bg=BG_PANEL)
        self.geometry("420x500")
        self.resizable(False, False)
        self._on_apply = on_apply

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._load_current()

    def _build_ui(self):
        # Title
        tk.Label(
            self, text="Stemmer Suffix Rules",
            bg=BG_PANEL, fg=TEXT_PRIMARY, font=FONT_HEADING,
        ).pack(fill="x", padx=12, pady=(12, 4))

        tk.Label(
            self, text="Suffixes are tried longest-first. A suffix is stripped only if\n"
                       "the remaining stem has more than 2 characters.",
            bg=BG_PANEL, fg=TEXT_SECONDARY, font=FONT,
            justify="left",
        ).pack(fill="x", padx=12, pady=(0, 8))

        list_frame = tk.Frame(self, bg=BG_PANEL)
        list_frame.pack(fill="both", expand=True, padx=12, pady=4)

        self._listbox = tk.Listbox(
            list_frame, selectmode="extended", width=30,
        )
        style_listbox(self._listbox)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        edit_frame = tk.Frame(self, bg=BG_PANEL)
        edit_frame.pack(fill="x", padx=12, pady=4)

        tk.Label(edit_frame, text="New suffix:", bg=BG_PANEL, fg=TEXT_PRIMARY,
                 font=FONT).pack(side="left")
        self._entry_var = tk.StringVar()
        self._entry = tk.Entry(
            edit_frame, textvariable=self._entry_var, width=15,
            bg=BG_DEEP, fg=TEXT_PRIMARY, font=FONT,
            insertbackground=TEXT_PRIMARY, relief="flat",
            highlightbackground=BORDER, highlightthickness=1,
        )
        self._entry.pack(side="left", padx=(8, 4))
        self._entry.bind("<Return>", lambda e: self._add_suffix())

        tk.Button(
            edit_frame, text="Add", bg=SUCCESS, fg=BG_DEEP,
            font=FONT_BOLD, relief="flat", padx=8, pady=2,
            command=self._add_suffix,
        ).pack(side="left", padx=4)

        tk.Button(
            edit_frame, text="Remove Selected", bg=ERROR, fg=TEXT_PRIMARY,
            font=FONT_BOLD, relief="flat", padx=8, pady=2,
            command=self._remove_selected,
        ).pack(side="left", padx=4)

        btn_frame = tk.Frame(self, bg=BG_PANEL)
        btn_frame.pack(fill="x", padx=12, pady=(8, 12))

        tk.Button(
            btn_frame, text="Reset to Defaults",
            bg=BUTTON_BG, fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER, activeforeground=TEXT_PRIMARY,
            font=FONT, relief="flat", padx=10, pady=4,
            command=self._reset_defaults,
        ).pack(side="left")

        tk.Button(
            btn_frame, text="Cancel",
            bg=BUTTON_BG, fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER, activeforeground=TEXT_PRIMARY,
            font=FONT, relief="flat", padx=10, pady=4,
            command=self.destroy,
        ).pack(side="right", padx=(4, 0))

        tk.Button(
            btn_frame, text="Apply",
            bg=ACCENT_DIM, fg=TEXT_PRIMARY,
            activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
            font=FONT_BOLD, relief="flat", padx=14, pady=4,
            command=self._apply,
        ).pack(side="right")

        preview_frame = tk.Frame(self, bg=BG_PANEL)
        preview_frame.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(preview_frame, text="Preview:", bg=BG_PANEL, fg=TEXT_SECONDARY,
                 font=FONT).pack(side="left")
        self._preview_var = tk.StringVar()
        tk.Label(preview_frame, textvariable=self._preview_var,
                 bg=BG_PANEL, fg=ACCENT, font=FONT).pack(side="left", padx=4)

        self._entry_var.trace_add("write", self._update_preview)

    def _load_current(self):
        self._listbox.delete(0, "end")
        for suf in get_suffixes():
            self._listbox.insert("end", suf)

    def _add_suffix(self):
        suf = self._entry_var.get().strip().lower()
        if not suf:
            return
        if not suf.isalpha():
            messagebox.showwarning("Invalid", "Suffix must contain only letters.",
                                   parent=self)
            return
        current = list(self._listbox.get(0, "end"))
        if suf in current:
            messagebox.showinfo("Duplicate", f"'{suf}' is already in the list.",
                                parent=self)
            return
        self._listbox.insert("end", suf)
        self._entry_var.set("")
        self._sort_list()

    def _remove_selected(self):
        selected = list(self._listbox.curselection())
        for idx in reversed(selected):
            self._listbox.delete(idx)

    def _reset_defaults(self):
        self._listbox.delete(0, "end")
        for suf in _DEFAULT_SUFFIXES:
            self._listbox.insert("end", suf)

    def _sort_list(self):
        items = list(self._listbox.get(0, "end"))
        items.sort(key=len, reverse=True)
        self._listbox.delete(0, "end")
        for item in items:
            self._listbox.insert("end", item)

    def _apply(self):
        suffixes = list(self._listbox.get(0, "end"))
        set_suffixes(suffixes)
        if self._on_apply:
            self._on_apply(suffixes)
        self.destroy()

    def _update_preview(self, *args):
        test_word = self._entry_var.get().strip().lower()
        if not test_word:
            self._preview_var.set("")
            return
        example = f"e.g. 'inform{test_word}' → 'inform'"
        self._preview_var.set(example)
