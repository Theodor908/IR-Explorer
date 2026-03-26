"""Color constants and styling helpers."""

import tkinter as tk
from tkinter import ttk

# --- palette ---
BG_DEEP = "#0f1117"
BG_PANEL = "#181a24"
BG_PANEL_ALT = "#1e2130"
BORDER = "#2a2d3e"
TEXT_PRIMARY = "#e0e2eb"
TEXT_SECONDARY = "#7a7e94"
ACCENT = "#4f8ff7"
ACCENT_HOVER = "#6ba3ff"
ACCENT_DIM = "#2d4a7a"
SUCCESS = "#4ade80"
WARNING = "#f59e0b"
ERROR = "#ef4444"
BUTTON_BG = "#252838"
BUTTON_HOVER = "#2f3348"

# Learn Mode accent (indigo)
LEARN_ACCENT = "#6366f1"
LEARN_ACCENT_HOVER = "#818cf8"
LEARN_ACCENT_DIM = "#3730a3"

# Animation colors
ANIM_HIGHLIGHT = "#fbbf24"
ANIM_FADEOUT = "#4b5563"
ANIM_ADDED = "#4ade80"

FONT_FAMILY = "Consolas"
FONT_SIZE = 9
FONT = (FONT_FAMILY, FONT_SIZE)
FONT_BOLD = (FONT_FAMILY, FONT_SIZE, "bold")
FONT_SMALL = (FONT_FAMILY, FONT_SIZE - 1)
FONT_HEADING = (FONT_FAMILY, FONT_SIZE + 2, "bold")


def setup_ttk_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG_PANEL, foreground=TEXT_PRIMARY,
                     font=FONT, borderwidth=0)
    style.configure("TFrame", background=BG_PANEL)
    style.configure("TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY,
                     font=FONT)
    style.configure("TButton", background=BUTTON_BG, foreground=TEXT_PRIMARY,
                     font=FONT, padding=(8, 4))
    style.map("TButton",
              background=[("active", BUTTON_HOVER), ("pressed", ACCENT_DIM)])
    style.configure("TNotebook", background=BG_DEEP, borderwidth=0)
    style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_SECONDARY,
                     font=FONT, padding=(12, 6))
    style.map("TNotebook.Tab",
              background=[("selected", BG_PANEL_ALT)],
              foreground=[("selected", TEXT_PRIMARY)])
    style.configure("TEntry", fieldbackground=BG_DEEP, foreground=TEXT_PRIMARY,
                     font=FONT, insertcolor=TEXT_PRIMARY)
    style.configure("TCombobox", fieldbackground=BG_DEEP, foreground=TEXT_PRIMARY,
                     background=BUTTON_BG, font=FONT, arrowcolor=TEXT_PRIMARY)
    style.map("TCombobox",
              fieldbackground=[("readonly", BG_DEEP), ("disabled", BG_PANEL)],
              foreground=[("readonly", TEXT_PRIMARY), ("disabled", TEXT_SECONDARY)],
              selectbackground=[("readonly", ACCENT_DIM)],
              selectforeground=[("readonly", TEXT_PRIMARY)])
    # combobox dropdown listbox needs option_add
    root.option_add("*TCombobox*Listbox.background", BG_DEEP)
    root.option_add("*TCombobox*Listbox.foreground", TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT_DIM)
    root.option_add("*TCombobox*Listbox.selectForeground", TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.font", FONT)
    style.configure("TSpinbox", fieldbackground=BG_DEEP, foreground=TEXT_PRIMARY,
                     background=BUTTON_BG, font=FONT, arrowcolor=TEXT_PRIMARY,
                     insertcolor=TEXT_PRIMARY)
    style.map("TSpinbox",
              fieldbackground=[("readonly", BG_DEEP), ("disabled", BG_PANEL),
                               ("active", BG_DEEP), ("focus", BG_DEEP)],
              foreground=[("disabled", TEXT_SECONDARY)])
    # override all states to prevent white flash on check/radio
    style.configure("TCheckbutton", background=BG_PANEL, foreground=TEXT_PRIMARY,
                     font=FONT, indicatorbackground=BG_DEEP,
                     indicatorforeground=ACCENT)
    style.map("TCheckbutton",
              background=[("active", BG_PANEL), ("pressed", BG_PANEL),
                          ("hover", BG_PANEL), ("!active", BG_PANEL)],
              foreground=[("active", TEXT_PRIMARY), ("pressed", TEXT_PRIMARY),
                          ("hover", TEXT_PRIMARY), ("disabled", TEXT_SECONDARY)],
              indicatorbackground=[("active", BG_DEEP), ("pressed", BG_DEEP),
                                   ("selected", ACCENT_DIM)])
    style.configure("TRadiobutton", background=BG_PANEL, foreground=TEXT_PRIMARY,
                     font=FONT, indicatorbackground=BG_DEEP,
                     indicatorforeground=ACCENT)
    style.map("TRadiobutton",
              background=[("active", BG_PANEL), ("pressed", BG_PANEL),
                          ("hover", BG_PANEL)],
              foreground=[("active", TEXT_PRIMARY), ("pressed", TEXT_PRIMARY),
                          ("selected", ACCENT), ("disabled", TEXT_SECONDARY)],
              indicatorbackground=[("active", BG_DEEP), ("pressed", BG_DEEP),
                                   ("selected", ACCENT)],
              indicatorforeground=[("selected", TEXT_PRIMARY)])
    style.configure("Horizontal.TScale", background=BG_PANEL,
                     troughcolor=BG_DEEP, sliderthickness=14)
    style.map("Horizontal.TScale",
              background=[("active", BG_PANEL)])
    style.configure("Treeview", background=BG_DEEP, foreground=TEXT_PRIMARY,
                     fieldbackground=BG_DEEP, font=FONT, rowheight=22)
    style.configure("Treeview.Heading", background=BG_PANEL,
                     foreground=TEXT_SECONDARY, font=FONT_BOLD)
    style.map("Treeview", background=[("selected", ACCENT_DIM)],
              foreground=[("selected", TEXT_PRIMARY)])
    style.configure("Horizontal.TScrollbar", background=BUTTON_BG,
                     troughcolor=BG_DEEP, arrowcolor=ACCENT)
    style.configure("Vertical.TScrollbar", background=BUTTON_BG,
                     troughcolor=BG_DEEP, arrowcolor=ACCENT)
    style.configure("Learn.TButton", background=LEARN_ACCENT_DIM,
                     foreground=TEXT_PRIMARY, font=FONT_BOLD, padding=(12, 6))
    style.map("Learn.TButton",
              background=[("active", LEARN_ACCENT), ("pressed", LEARN_ACCENT_DIM)])
    style.configure("Mode.TButton", background=BUTTON_BG,
                     foreground=TEXT_SECONDARY, font=FONT_BOLD, padding=(12, 6))
    style.configure("ModeActive.TButton", background=ACCENT_DIM,
                     foreground=TEXT_PRIMARY, font=FONT_BOLD, padding=(12, 6))


def style_frame(frame):
    frame.configure(background=BG_PANEL)


def style_text(widget):
    widget.configure(bg=BG_DEEP, fg=TEXT_PRIMARY, font=FONT,
                     insertbackground=TEXT_PRIMARY, selectbackground=ACCENT_DIM,
                     relief="flat", borderwidth=1, highlightbackground=BORDER,
                     highlightthickness=1)


def style_listbox(lb):
    lb.configure(bg=BG_DEEP, fg=TEXT_PRIMARY, font=FONT,
                 selectbackground=ACCENT_DIM, selectforeground=TEXT_PRIMARY,
                 relief="flat", borderwidth=0, highlightbackground=BORDER,
                 highlightthickness=1)


def style_canvas(canvas):
    canvas.configure(bg=BG_DEEP, highlightthickness=0)
