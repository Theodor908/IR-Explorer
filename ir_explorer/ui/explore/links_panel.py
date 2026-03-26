"""Link Analysis panel: HITS / PageRank animation."""

import math
import tkinter as tk
from tkinter import ttk, messagebox

from ir_explorer.ui.theme import (
    BG_DEEP, BG_PANEL, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, ACCENT_DIM,
    SUCCESS, WARNING,
    FONT, FONT_BOLD, FONT_SMALL, style_canvas
)
from ir_explorer.ui.widgets.animated_canvas import AnimatedCanvas
from ir_explorer.ui.widgets.hint_box import HintBox
from ir_explorer.ui.widgets.param_slider import ParameterBar
from ir_explorer.core.crawler import build_graph_from_corpus, LinkGraph
from ir_explorer.core.link_analysis import hits, pagerank


class LinksPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._graph    = None
        self._nodes    = []
        self._positions = {}   # node → (xfrac, yfrac)
        self._build_ui()

    def _build_ui(self):
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(ctrl, text="Algorithm:", font=FONT_BOLD).pack(side="left")
        self._algo_var = tk.StringVar(value="PageRank")
        algo_combo = ttk.Combobox(ctrl, textvariable=self._algo_var,
                                  values=["PageRank", "HITS"],
                                  state="readonly", width=10)
        algo_combo.pack(side="left", padx=(4, 12))
        algo_combo.bind("<<ComboboxSelected>>", self._on_algo_change)

        self._params = ParameterBar(ctrl)
        self._params.pack(side="left", fill="x", expand=True)
        self._params.add_slider("iterations", "Iterations", from_=1, to=50, initial=20, resolution=1)
        self._damping_ctrl = self._params.add_slider(
            "damping", "Damping", from_=0.5, to=1.0, initial=0.85, resolution=0.01
        )

        ttk.Button(ctrl, text="Run", command=self._run).pack(side="left", padx=6)

        self._status_var = tk.StringVar(value="Load a corpus, choose settings, and click Run.")
        ttk.Label(self, textvariable=self._status_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=8, pady=(4, 4))

        self._anim = AnimatedCanvas(main, width=700, height=300)
        self._anim.pack(fill="both", expand=True)

        ttk.Label(main, text="Per-node scores at current iteration",
                  font=FONT_BOLD).pack(anchor="w", pady=(6, 0))
        self._bar_canvas = tk.Canvas(main, height=100)
        style_canvas(self._bar_canvas)
        self._bar_canvas.pack(fill="x")

        self._hint = HintBox(self)
        self._hint.pack(fill="x", padx=8, pady=(4, 8))
        self._hint.set_hint(
            "Link Analysis Algorithms",
            "PageRank: models a random surfer clicking links. A node's score = importance "
            "passed from nodes linking to it. The damping factor (d=0.85) means 85% chance "
            "of following a link, 15% chance of jumping randomly. Lower d = more uniform "
            "scores. Higher d = link structure matters more.\n\n"
            "HITS: computes two scores per node. Authority = how much valuable content "
            "(linked by many hubs). Hub = how well it curates links to authorities.\n\n"
            "Iterations: both algorithms iterate until scores stabilize. Watch how bars "
            "shift dramatically in early iterations then barely change as convergence is "
            "reached. More iterations = more precise, but 10-20 is usually enough.\n\n"
            "Tip: Load the 'Link Structure' example corpus for the best demonstration — "
            "it has an asymmetric link graph that produces interesting score differences."
        )

        # hook anim controls to also update bar chart
        self._anim.canvas.bind("<Configure>", lambda e: None)
        self._anim._btn_forward.configure(command=self._step_forward)
        self._anim._btn_back.configure(command=self._step_back)
        self._anim._btn_reset.configure(command=self._reset)
        self._anim._btn_play.configure(command=self._toggle_play)

        self._score_snapshots = []   # list of score dicts per step

    def _on_algo_change(self, event=None):
        algo = self._algo_var.get()
        scale = self._damping_ctrl._scale
        label_widget = self._damping_ctrl
        if algo == "HITS":
            scale.state(["disabled"])
        else:
            scale.state(["!disabled"])

    def _compute_positions(self):
        n = len(self._nodes)
        self._positions = {}
        if n == 0:
            return
        for i, node in enumerate(self._nodes):
            angle = 2 * math.pi * i / n - math.pi / 2
            self._positions[node] = (
                0.5 + 0.38 * math.cos(angle),
                0.5 + 0.38 * math.sin(angle),
            )

    def _run(self):
        if not self.app.corpus.docs:
            messagebox.showwarning("No Corpus", "Load a corpus first.")
            return

        if self.app.corpus.links:
            self._graph = LinkGraph.from_adjacency(self.app.corpus.links)
            for doc_id in self.app.corpus.docs:
                self._graph.add_node(doc_id)
        else:
            self._graph = build_graph_from_corpus(self.app.corpus.docs)
        self._nodes = sorted(self._graph.nodes())
        self._compute_positions()

        algo       = self._algo_var.get()
        iterations = int(self._params.get("iterations"))
        damping    = float(self._params.get("damping"))

        anim_steps = []
        self._score_snapshots = []

        n_nodes = len(self._nodes)
        uniform = {n: 1.0 / n_nodes for n in self._nodes} if n_nodes else {}
        anim_steps.append((lambda c: self._draw_graph(c, uniform, f"{algo} — Graph Overview"), 600))
        self._score_snapshots.append(uniform)

        if algo == "PageRank":
            results = pagerank(self._graph, damping=damping, iterations=iterations)
            for i, scores in enumerate(results, 1):
                label = f"PageRank  iteration {i}/{iterations}  (d={damping:.2f})"
                def make_draw(s, lbl):
                    def draw(c): self._draw_graph(c, s, lbl)
                    return draw
                anim_steps.append((make_draw(scores, label), 600))
                self._score_snapshots.append(scores)
        else:
            results = hits(self._graph, iterations=iterations)
            for i, (auth, hub) in enumerate(results, 1):
                label = f"HITS  iteration {i}/{iterations}"
                def make_draw(a, h, lbl):
                    def draw(c): self._draw_graph(c, a, lbl, hub_scores=h)
                    return draw
                anim_steps.append((make_draw(auth, hub, label), 600))
                self._score_snapshots.append(auth)

        self._anim.load_steps(anim_steps)
        self._status_var.set(
            f"{algo} complete: {iterations} iterations.  Use controls to step through."
        )

        self._draw_bar_chart(self._score_snapshots[0])

        # patch _draw_current so bar chart updates on nav
        orig_draw = self._anim._draw_current
        panel = self

        def patched_draw():
            orig_draw()
            idx = panel._anim._current
            if 0 <= idx < len(panel._score_snapshots):
                panel._draw_bar_chart(panel._score_snapshots[idx])
        self._anim._draw_current = patched_draw

    def _step_forward(self):
        self._anim.step_forward()
        self._refresh_bar()

    def _step_back(self):
        self._anim.step_back()
        self._refresh_bar()

    def _reset(self):
        self._anim.reset()
        if self._score_snapshots:
            self._draw_bar_chart(self._score_snapshots[0])

    def _toggle_play(self):
        self._anim._toggle_play()

    def _refresh_bar(self):
        idx = self._anim._current
        if 0 <= idx < len(self._score_snapshots):
            self._draw_bar_chart(self._score_snapshots[idx])

    def _draw_graph(self, canvas, scores, label, hub_scores=None):
        canvas.update_idletasks()
        W = canvas.winfo_width()  or 700
        H = canvas.winfo_height() or 300

        if not self._nodes:
            canvas.create_text(W // 2, H // 2, text="No graph – build first",
                               fill=TEXT_SECONDARY, font=FONT)
            return

        max_score = max(scores.values()) if scores else 1.0
        if max_score == 0:
            max_score = 1.0

        for node in self._nodes:
            x1f, y1f = self._positions.get(node, (0.5, 0.5))
            x1, y1 = x1f * W, y1f * H
            for neighbor in self._graph.neighbors(node):
                x2f, y2f = self._positions.get(neighbor, (0.5, 0.5))
                x2, y2 = x2f * W, y2f * H
                canvas.create_line(x1, y1, x2, y2, fill="#3a3e52", width=1,
                                   arrow=tk.LAST, arrowshape=(6, 8, 3))

        r = max(14, min(22, int(W / (len(self._nodes) + 2))))

        for node in self._nodes:
            xf, yf = self._positions.get(node, (0.5, 0.5))
            x, y = xf * W, yf * H

            intensity = scores.get(node, 0) / max_score
            r_ch = int(0x0f + intensity * (0x4f - 0x0f))
            g_ch = int(0x1a + intensity * (0x5f - 0x1a))
            b_ch = int(0x24 + intensity * (0xf7 - 0x24))
            color = f"#{r_ch:02x}{g_ch:02x}{b_ch:02x}"

            canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill=color, outline=ACCENT_DIM, width=2)
            canvas.create_text(x, y, text=str(node), fill=TEXT_PRIMARY,
                               font=FONT_SMALL)

            score_str = f"{scores.get(node, 0):.3f}"
            canvas.create_text(x, y + r + 8, text=score_str,
                               fill=TEXT_SECONDARY, font=FONT_SMALL)

        if label:
            canvas.create_text(W // 2, 10, text=label, fill=TEXT_SECONDARY,
                               font=FONT_SMALL, anchor="n")

    def _draw_bar_chart(self, scores):
        c = self._bar_canvas
        c.delete("all")
        c.update_idletasks()
        W = c.winfo_width()  or 700
        H = c.winfo_height() or 100

        if not scores or not self._nodes or W < 20 or H < 20:
            return

        ml, mr, mt, mb = 5, 5, 8, 18
        nodes = self._nodes
        n = len(nodes)
        bar_w = (W - ml - mr) / max(n, 1)
        max_score = max(scores.values()) if scores else 1.0
        if max_score == 0:
            max_score = 1.0

        for i, node in enumerate(nodes):
            s = scores.get(node, 0)
            bar_h = int((s / max_score) * (H - mt - mb))
            x = ml + i * bar_w
            y_top = mt + (H - mt - mb) - bar_h
            c.create_rectangle(x + 1, y_top, x + bar_w - 1, H - mb,
                               fill=ACCENT_DIM, outline="")
            if bar_w >= 16:
                c.create_text(x + bar_w / 2, H - mb + 4, text=str(node),
                             fill=TEXT_SECONDARY, font=FONT_SMALL, anchor="n")
            if bar_h > 14:
                c.create_text(x + bar_w / 2, y_top + 2, text=f"{s:.3f}",
                             fill=TEXT_PRIMARY, font=FONT_SMALL, anchor="n")
