"""Step-by-step animation engine wrapping tkinter Canvas."""

import tkinter as tk
from tkinter import ttk
from ir_explorer.ui.theme import BG_DEEP, TEXT_PRIMARY, ACCENT, FONT, style_canvas

class AnimatedCanvas(ttk.Frame):
    def __init__(self, parent, width=600, height=400, **kwargs):
        super().__init__(parent, **kwargs)
        self._steps = []
        self._current = -1
        self._playing = False
        self._speed = 1.0
        self._after_id = None

        self.canvas = tk.Canvas(self, width=width, height=height)
        style_canvas(self.canvas)
        self.canvas.pack(fill="both", expand=True)

        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", pady=(4, 0))
        self._btn_reset = ttk.Button(ctrl, text="⏮", width=3, command=self.reset)
        self._btn_reset.pack(side="left", padx=2)
        self._btn_back = ttk.Button(ctrl, text="◀", width=3, command=self.step_back)
        self._btn_back.pack(side="left", padx=2)
        self._btn_play = ttk.Button(ctrl, text="▶", width=3, command=self._toggle_play)
        self._btn_play.pack(side="left", padx=2)
        self._btn_forward = ttk.Button(ctrl, text="▶", width=3, command=self.step_forward)
        self._btn_forward.pack(side="left", padx=2)
        self._btn_end = ttk.Button(ctrl, text="⏭", width=3, command=self.go_to_end)
        self._btn_end.pack(side="left", padx=2)

        self._step_var = tk.StringVar(value="0 / 0")
        ttk.Label(ctrl, textvariable=self._step_var).pack(side="left", padx=(12, 4))

        ttk.Label(ctrl, text="Speed:").pack(side="right", padx=(4, 0))
        self._speed_var = tk.DoubleVar(value=1.0)
        speed_menu = ttk.Combobox(ctrl, textvariable=self._speed_var,
            values=["0.5", "1.0", "2.0", "4.0"], width=4, state="readonly")
        speed_menu.pack(side="right", padx=2)
        speed_menu.bind("<<ComboboxSelected>>", self._on_speed_change)

    def add_step(self, draw_fn, duration_ms=500):
        self._steps.append((draw_fn, duration_ms))
        self._update_counter()

    def load_steps(self, steps):
        self.clear_steps()
        for draw_fn, duration_ms in steps:
            self._steps.append((draw_fn, duration_ms))
        self._update_counter()
        if self._steps:
            self._current = 0
            self._draw_current()

    def clear_steps(self):
        self.stop()
        self._steps.clear()
        self._current = -1
        self.canvas.delete("all")
        self._update_counter()

    def step_forward(self):
        if self._current < len(self._steps) - 1:
            self._current += 1
            self._draw_current()

    def step_back(self):
        if self._current > 0:
            self._current -= 1
            self._draw_current()

    def go_to_end(self):
        self.stop()
        if self._steps:
            self._current = len(self._steps) - 1
            self._draw_current()

    def reset(self):
        self.stop()
        if self._steps:
            self._current = 0
            self._draw_current()
        else:
            self._current = -1
            self.canvas.delete("all")
            self._update_counter()

    def play(self):
        self._playing = True
        self._btn_play.configure(text="⏸")
        self._play_next()

    def stop(self):
        self._playing = False
        self._btn_play.configure(text="▶")
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _toggle_play(self):
        if self._playing: self.stop()
        else: self.play()

    def _play_next(self):
        if not self._playing: return
        if self._current >= len(self._steps) - 1:
            self.stop()
            return
        self.step_forward()
        _, duration = self._steps[self._current]
        delay = max(50, int(duration / self._speed))
        self._after_id = self.after(delay, self._play_next)

    def _draw_current(self):
        self.canvas.delete("all")
        if 0 <= self._current < len(self._steps):
            draw_fn, _ = self._steps[self._current]
            draw_fn(self.canvas)
        self._update_counter()

    def _update_counter(self):
        current = self._current + 1 if self._current >= 0 else 0
        self._step_var.set(f"{current} / {len(self._steps)}")

    def _on_speed_change(self, event=None):
        try: self._speed = float(self._speed_var.get())
        except ValueError: self._speed = 1.0
