"""Parameter controls: toggle, dropdown, slider."""

import tkinter as tk
from tkinter import ttk
from ir_explorer.ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, FONT, FONT_BOLD

class ParamToggle(ttk.Frame):
    def __init__(self, parent, label, initial=True, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._var = tk.BooleanVar(value=initial)
        self._command = command
        ttk.Label(self, text=label, font=FONT).pack(side="left", padx=(0, 4))
        self._btn = ttk.Checkbutton(self, variable=self._var, command=self._on_change)
        self._btn.pack(side="left")
    def get(self): return self._var.get()
    def set(self, value): self._var.set(value)
    def _on_change(self):
        if self._command: self._command(self._var.get())

class ParamDropdown(ttk.Frame):
    def __init__(self, parent, label, choices, initial=None, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._command = command
        ttk.Label(self, text=label, font=FONT).pack(side="left", padx=(0, 4))
        self._var = tk.StringVar(value=initial or choices[0])
        self._combo = ttk.Combobox(self, textvariable=self._var, values=choices, width=12, state="readonly")
        self._combo.pack(side="left")
        self._combo.bind("<<ComboboxSelected>>", self._on_change)
    def get(self): return self._var.get()
    def set(self, value): self._var.set(value)
    def _on_change(self, event=None):
        if self._command: self._command(self._var.get())

class ParamSlider(ttk.Frame):
    def __init__(self, parent, label, from_=0, to=100, initial=50, resolution=1, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._command = command
        self._resolution = resolution
        ttk.Label(self, text=label, font=FONT).pack(side="left", padx=(0, 4))
        self._var = tk.DoubleVar(value=initial)
        self._scale = ttk.Scale(self, from_=from_, to=to, variable=self._var, orient="horizontal", length=150, command=self._on_change)
        self._scale.pack(side="left", padx=4)
        self._readout = ttk.Label(self, text=str(initial), width=6)
        self._readout.pack(side="left")
    def get(self): return round(self._var.get() / self._resolution) * self._resolution
    def set(self, value):
        self._var.set(value)
        self._readout.configure(text=str(value))
    def _on_change(self, value=None):
        v = self.get()
        self._readout.configure(text=str(v))
        if self._command: self._command(v)

class ParameterBar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._controls = {}
    def add_toggle(self, key, label, initial=True, command=None):
        ctrl = ParamToggle(self, label, initial, command)
        ctrl.pack(side="left", padx=(0, 16))
        self._controls[key] = ctrl
        return ctrl
    def add_dropdown(self, key, label, choices, initial=None, command=None):
        ctrl = ParamDropdown(self, label, choices, initial, command)
        ctrl.pack(side="left", padx=(0, 16))
        self._controls[key] = ctrl
        return ctrl
    def add_slider(self, key, label, from_=0, to=100, initial=50, resolution=1, command=None):
        ctrl = ParamSlider(self, label, from_, to, initial, resolution, command)
        ctrl.pack(side="left", padx=(0, 16))
        self._controls[key] = ctrl
        return ctrl
    def get(self, key): return self._controls[key].get()
    def get_all(self): return {k: c.get() for k, c in self._controls.items()}
