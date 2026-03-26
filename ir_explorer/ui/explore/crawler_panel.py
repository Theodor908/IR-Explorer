"""Crawler panel: BFS/DFS crawl animation on the link graph."""

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
from ir_explorer.core.crawler import build_graph_from_corpus, crawl_bfs, crawl_dfs, LinkGraph


_COL_DEFAULT  = "#2a2d3e"
_COL_VISITED  = SUCCESS
_COL_FRONTIER = WARNING
_COL_CURRENT  = ACCENT


class CrawlerPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._graph    = None
        self._nodes    = []
        self._positions = {}
        self._build_ui()

    def _build_ui(self):
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(ctrl, text="Seed:", font=FONT_BOLD).pack(side="left")
        self._seed_var = tk.StringVar(value="-- Select seed --")
        self._seed_combo = ttk.Combobox(ctrl, textvariable=self._seed_var,
                                        state="readonly", width=12)
        self._seed_combo.pack(side="left", padx=(4, 12))

        ttk.Label(ctrl, text="Strategy:", font=FONT_BOLD).pack(side="left")
        self._strategy_var = tk.StringVar(value="BFS")
        tk.Radiobutton(
            ctrl, text="BFS", variable=self._strategy_var, value="BFS",
            bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=ACCENT_DIM,
            activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY,
            font=FONT, indicatoron=True,
        ).pack(side="left", padx=2)
        tk.Radiobutton(
            ctrl, text="DFS", variable=self._strategy_var, value="DFS",
            bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=ACCENT_DIM,
            activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY,
            font=FONT, indicatoron=True,
        ).pack(side="left", padx=(2, 12))

        self._params = ParameterBar(ctrl)
        self._params.pack(side="left", fill="x", expand=True)
        self._params.add_slider("max_depth", "Depth", from_=1, to=10, initial=3, resolution=1)
        self._params.add_slider("max_pages", "Pages", from_=1, to=50, initial=20, resolution=1)

        ttk.Button(ctrl, text="Run", command=self._run).pack(side="left", padx=6)

        self._status_var = tk.StringVar(value="Load a corpus, choose settings, and click Run.")
        ttk.Label(self, textvariable=self._status_var,
                  foreground=TEXT_SECONDARY).pack(fill="x", padx=8, pady=2)

        self._anim = AnimatedCanvas(self, width=700, height=380)
        self._anim.pack(fill="both", expand=True, padx=8, pady=(4, 4))

        self._hint = HintBox(self)
        self._hint.pack(fill="x", padx=8, pady=(4, 8))
        self._hint.set_hint(
            "Web Crawler Simulation",
            "The crawler walks the link graph starting from a seed document.\n\n"
            "Colors: BLUE = current node being processed. GREEN = already visited. "
            "YELLOW = in the frontier (waiting to be visited). GRAY = not yet discovered.\n\n"
            "BFS explores level by level (all neighbors first, then their neighbors). "
            "DFS dives as deep as possible before backtracking.\n\n"
            "Max Depth: how many link-hops away from the seed the crawler will go. "
            "Depth 1 = only direct neighbors. Depth 3 = neighbors of neighbors of neighbors.\n\n"
            "Max Pages: the maximum number of documents the crawler will visit before stopping, "
            "regardless of depth. Simulates real crawlers that have resource limits."
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

        self._seed_combo["values"] = self._nodes
        seed = self._seed_var.get()
        if not seed or seed.startswith("--") or seed not in self._nodes:
            if self._nodes:
                seed = self._nodes[0]
                self._seed_var.set(seed)
            else:
                return

        strategy  = self._strategy_var.get()
        max_depth = int(self._params.get("max_depth"))
        max_pages = int(self._params.get("max_pages"))

        if strategy == "BFS":
            gen = crawl_bfs(self._graph, seed, max_depth=max_depth, max_pages=max_pages)
        else:
            gen = crawl_dfs(self._graph, seed, max_depth=max_depth, max_pages=max_pages)

        crawl_result = list(gen)

        anim_steps = []
        anim_steps.append((lambda c: self._draw_graph(c, set(), set(), None), 800))

        for step in crawl_result:
            visited  = step["visited"]
            frontier = set(step["frontier"])
            current  = step["current"]
            depth    = step["depth"]

            def make_draw(v, f, cur, d):
                def draw(c):
                    self._draw_graph(c, v, f, cur)
                    c.create_text(
                        10, 10,
                        text=f"Depth: {d}  Visited: {len(v)}",
                        anchor="nw", fill=TEXT_SECONDARY, font=FONT_SMALL
                    )
                return draw

            anim_steps.append((make_draw(visited, frontier, current, depth), 700))

        n_nodes = len(self._nodes)
        n_edges = self._graph.number_of_edges()
        self._anim.load_steps(anim_steps)
        self._status_var.set(
            f"{strategy} from '{seed}': {n_nodes} nodes, {n_edges} edges, "
            f"{len(crawl_result)} crawl steps (depth={max_depth}, pages={max_pages})"
        )

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

    def _draw_graph(self, canvas, visited, frontier, current):
        canvas.update_idletasks()
        W = canvas.winfo_width()  or 700
        H = canvas.winfo_height() or 380

        if not self._nodes:
            canvas.create_text(W // 2, H // 2, text="No graph",
                               fill=TEXT_SECONDARY, font=FONT)
            return

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

            if node == current:
                color = _COL_CURRENT
            elif node in visited:
                color = _COL_VISITED
            elif node in frontier:
                color = _COL_FRONTIER
            else:
                color = _COL_DEFAULT

            canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill=color, outline=BG_DEEP, width=2)
            canvas.create_text(x, y, text=str(node), fill=TEXT_PRIMARY,
                               font=FONT_SMALL)

        legend = [("Current", _COL_CURRENT), ("Visited", _COL_VISITED),
                  ("Frontier", _COL_FRONTIER), ("Unseen", _COL_DEFAULT)]
        lx, ly = 12, H - 18 * len(legend) - 4
        for label, col in legend:
            canvas.create_rectangle(lx, ly, lx + 12, ly + 12, fill=col, outline="")
            canvas.create_text(lx + 16, ly + 6, text=label, anchor="w",
                               fill=TEXT_SECONDARY, font=FONT_SMALL)
            ly += 18
