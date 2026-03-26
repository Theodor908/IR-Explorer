"""Animation step generators for Learn Mode demos."""

import json
import math
import os
from ir_explorer.core.preprocessing import (
    tokenize, remove_stopwords, stem, stem_all, STOPWORDS,
    configurable_pipeline, PipelineConfig,
)
from ir_explorer.core.retrieval import tfidf_rank
from ir_explorer.core.evaluation import precision_recall_curve
from ir_explorer.core.crawler import build_graph_from_corpus, crawl_bfs, LinkGraph
from ir_explorer.core.link_analysis import pagerank
from ir_explorer.ui.theme import (
    BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT, ACCENT_DIM,
    ANIM_HIGHLIGHT, ANIM_FADEOUT, ANIM_ADDED,
    ERROR, SUCCESS,
    FONT_FAMILY,
)

W, H = 580, 350

_BOOL_QUERY = "quantum AND inflation"
_TFIDF_QUERY = "eternal inflation"
_EVAL_QUERY = "eternal inflation"
# chosen to produce a non-trivial PR curve shape
_EVAL_RELEVANT = {"d9", "d6", "d1", "d4"}


# gentler than the user-configurable list to avoid over-stemming in demos
_LESSON_SUFFIXES = [
    "ing", "ness", "ment", "ies", "ful", "less", "ly", "ed", "er", "es", "s",
]


def _lesson_stem(token):
    for suf in _LESSON_SUFFIXES:
        if token.endswith(suf) and len(token) > len(suf) + 2:
            return token[:-len(suf)]
    return token


def _lesson_stem_all(tokens):
    return [_lesson_stem(t) for t in tokens]


class _LessonData:
    """Singleton: lesson-private corpus/index, isolated from user's Explore data."""

    _instance = None

    def __init__(self):
        from ir_explorer.core.corpus import Corpus
        from ir_explorer.core.index import InvertedIndex

        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets"
        )

        self.corpus = Corpus()
        self.corpus.load_from_json(os.path.join(assets_dir, "default_corpus.json"))

        self.config = PipelineConfig()
        self.index = InvertedIndex()
        self.index.build(self.corpus.docs, config=self.config)

        link_path = os.path.join(assets_dir, "corpora", "link_structure_corpus.json")
        with open(link_path, "r", encoding="utf-8") as f:
            link_data = json.load(f)
        self.link_graph = LinkGraph.from_adjacency(link_data.get("links", {}))
        for doc_id in link_data.get("documents", {}):
            self.link_graph.add_node(doc_id)
        self.link_nodes = sorted(link_data["documents"].keys())

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def generate_animation(action_key, app, highlight=None):
    """Returns list of (draw_fn, duration_ms) for the given action."""
    ld = _LessonData.get()

    highlight = highlight or list(ld.corpus.docs.keys())[:3]

    builders = {
        "tokenize_doc": _anim_tokenize,
        "remove_stopwords": _anim_stopwords,
        "apply_stemming": _anim_stemming,
        "build_index": _anim_build_index,
        "boolean_search": _anim_boolean,
        "tfidf_search": _anim_tfidf,
        "run_evaluation": _anim_evaluation,
        "run_crawl": _anim_crawl,
        "run_pagerank": _anim_pagerank,
    }

    if action_key not in builders:
        raise ValueError(f"Unknown animation action: {action_key}")

    return builders[action_key](ld, highlight)


def _duration(n_steps):
    return 300 if n_steps > 15 else 500


_MAX_VISIBLE = 18
_LINE_H = 14


def _viewport_offset(current_index, line_height=_LINE_H, start_y=60,
                     max_visible=_MAX_VISIBLE):
    """Y offset to keep current_index visible."""
    visible_bottom = start_y + max_visible * line_height
    item_y = start_y + current_index * line_height
    if item_y < visible_bottom:
        return 0
    return item_y - visible_bottom + line_height


def _draw_text_block(canvas, x, y, text, color=TEXT_PRIMARY, font_size=8,
                     max_width=250, tag=None):
    canvas.create_text(
        x, y, text=text, fill=color,
        font=(FONT_FAMILY, font_size), anchor="nw", width=max_width,
        tags=(tag,) if tag else (),
    )
    return y


def _draw_title(canvas, text, x=W // 2, y=12):
    canvas.create_text(x, y, text=text, fill=TEXT_PRIMARY,
                       font=(FONT_FAMILY, 10, "bold"), anchor="n")


def _anim_tokenize(ld, highlight):
    doc_id = highlight[0] if highlight else "d1"
    raw_text = ld.corpus.docs.get(doc_id, "")[:200]
    words = raw_text.split()
    tokens = tokenize(raw_text)

    words = words[:30]
    tokens = tokens[:30]
    n = len(tokens)
    dur = _duration(n + 1)
    steps = []

    def draw_step0(canvas):
        _draw_title(canvas, f"Tokenizing {doc_id}")
        canvas.create_text(20, 40, text="Raw Text:", fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
        canvas.create_text(20, 60, text=" ".join(words),
                           fill=TEXT_PRIMARY, font=(FONT_FAMILY, 8),
                           anchor="nw", width=260)
        canvas.create_text(310, 40, text="Tokens:", fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
    steps.append((draw_step0, dur))

    for step_i in range(1, n + 1):
        def make_draw(si):
            def draw(canvas):
                _draw_title(canvas, f"Tokenizing {doc_id}")
                v_off = _viewport_offset(si - 1)
                canvas.create_text(20, 40, text="Raw Text:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                y = 60 - v_off
                for wi, w in enumerate(words):
                    if 56 <= y <= H - 20:
                        color = ANIM_HIGHLIGHT if wi == si - 1 else TEXT_PRIMARY
                        canvas.create_text(20, y, text=w, fill=color,
                                           font=(FONT_FAMILY, 8), anchor="nw")
                    y += _LINE_H
                canvas.create_text(310, 40, text="Tokens:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                ty = 60 - v_off
                for ti in range(si):
                    if 40 <= ty <= H - 20:
                        color = ANIM_ADDED if ti == si - 1 else TEXT_PRIMARY
                        canvas.create_text(310, ty, text=tokens[ti], fill=color,
                                           font=(FONT_FAMILY, 8), anchor="nw")
                    ty += _LINE_H
            return draw
        steps.append((make_draw(step_i), dur))

    return steps


def _anim_stopwords(ld, highlight):
    doc_id = highlight[0] if highlight else "d1"
    tokens = tokenize(ld.corpus.docs.get(doc_id, ""))[:30]
    n = len(tokens)
    dur = _duration(n + 1)
    steps = []

    for step_i in range(1, n + 1):
        def make_draw(si):
            def draw(canvas):
                _draw_title(canvas, f"Removing stopwords from {doc_id}")
                v_off = _viewport_offset(si - 1)
                canvas.create_text(20, 40, text="Tokens:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                y = 60 - v_off
                for ti in range(n):
                    if 56 <= y <= H - 20:
                        if ti < si:
                            is_stop = tokens[ti] in STOPWORDS
                            color = ANIM_FADEOUT if is_stop else ANIM_ADDED
                            prefix = "\u2717 " if is_stop else "\u2713 "
                        else:
                            color = TEXT_SECONDARY
                            prefix = "  "
                        canvas.create_text(20, y, text=f"{prefix}{tokens[ti]}",
                                           fill=color, font=(FONT_FAMILY, 8),
                                           anchor="nw")
                    y += _LINE_H
                processed = tokens[:si]
                kept = [t for t in processed if t not in STOPWORDS]
                removed = [t for t in processed if t in STOPWORDS]
                canvas.create_text(310, 40, text=f"Kept: {len(kept)}", fill=ANIM_ADDED,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                canvas.create_text(310, 58, text=f"Removed: {len(removed)}", fill=ANIM_FADEOUT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                canvas.create_text(310, 85, text="Kept tokens:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                k_off = _viewport_offset(len(kept) - 1, start_y=105)
                ky = 105 - k_off
                for t in kept:
                    if 85 <= ky <= H - 20:
                        canvas.create_text(310, ky, text=t, fill=TEXT_PRIMARY,
                                           font=(FONT_FAMILY, 8), anchor="nw")
                    ky += _LINE_H
            return draw
        steps.append((make_draw(step_i), dur))

    return steps


def _anim_stemming(ld, highlight):
    doc_id = highlight[0] if highlight else "d1"
    raw = tokenize(ld.corpus.docs.get(doc_id, ""))
    tokens = [t for t in raw if t not in STOPWORDS]
    seen = set()
    unique = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    unique = unique[:25]
    n = len(unique)
    dur = _duration(n)
    steps = []

    for step_i in range(1, n + 1):
        def make_draw(si):
            def draw(canvas):
                _draw_title(canvas, f"Stemming tokens from {doc_id}")
                v_off = _viewport_offset(si - 1)
                canvas.create_text(20, 40, text="Before:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                canvas.create_text(200, 40, text="After:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                y = 60 - v_off
                for ti in range(n):
                    if 56 <= y <= H - 20:
                        token = unique[ti]
                        stemmed = _lesson_stem(token)
                        changed = stemmed != token
                        if ti < si:
                            if changed:
                                stem_part = stemmed
                                suffix = token[len(stemmed):]
                                canvas.create_text(20, y, text=stem_part,
                                                   fill=TEXT_PRIMARY,
                                                   font=(FONT_FAMILY, 8), anchor="nw")
                                sx = 20 + len(stem_part) * 7
                                canvas.create_text(sx, y, text=suffix,
                                                   fill=ERROR,
                                                   font=(FONT_FAMILY, 8), anchor="nw")
                            else:
                                canvas.create_text(20, y, text=token,
                                                   fill=ANIM_FADEOUT,
                                                   font=(FONT_FAMILY, 8), anchor="nw")
                            color = ANIM_ADDED if changed else ANIM_FADEOUT
                            canvas.create_text(200, y, text=stemmed, fill=color,
                                               font=(FONT_FAMILY, 8), anchor="nw")
                        else:
                            canvas.create_text(20, y, text=unique[ti],
                                               fill=TEXT_SECONDARY,
                                               font=(FONT_FAMILY, 8), anchor="nw")
                    y += _LINE_H
            return draw
        steps.append((make_draw(step_i), dur))

    return steps


def _anim_build_index(ld, highlight):
    highlight = highlight or list(ld.corpus.docs.keys())[:3]
    n = len(highlight)
    dur = _duration(n)
    steps = []

    cumulative_index = {}

    for step_i in range(n):
        doc_id = highlight[step_i]
        text = ld.corpus.docs.get(doc_id, "")
        doc_tokens = configurable_pipeline(text, ld.config)
        new_terms = set()
        for t in set(doc_tokens):
            if t not in cumulative_index:
                cumulative_index[t] = set()
                new_terms.add(t)
            cumulative_index[t].add(doc_id)

        snapshot = {t: set(docs) for t, docs in cumulative_index.items()}
        current_doc = doc_id
        new_t = set(new_terms)

        def make_draw(snap, cur_doc, new_terms_set, si):
            def draw(canvas):
                _draw_title(canvas, "Building Inverted Index")
                canvas.create_text(20, 40, text="Docs:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                y = 58
                for di, did in enumerate(highlight):
                    color = ANIM_HIGHLIGHT if did == cur_doc else (
                        ANIM_ADDED if di <= si else TEXT_SECONDARY)
                    canvas.create_text(20, y, text=did, fill=color,
                                       font=(FONT_FAMILY, 7), anchor="nw")
                    y += 13

                canvas.create_text(90, 40, text="Term", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                canvas.create_text(250, 40, text="Postings", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                sorted_terms = sorted(snap.keys())
                scroll_start = 0
                if new_terms_set:
                    for idx, t in enumerate(sorted_terms):
                        if t in new_terms_set:
                            scroll_start = max(0, idx - _MAX_VISIBLE // 2)
                            break
                visible_terms = sorted_terms[scroll_start:scroll_start + _MAX_VISIBLE]
                y = 58
                if scroll_start > 0:
                    canvas.create_text(90, y, text=f"... ({scroll_start} above)",
                                       fill=TEXT_SECONDARY,
                                       font=(FONT_FAMILY, 7), anchor="nw")
                    y += 12
                for term in visible_terms:
                    tc = ANIM_ADDED if term in new_terms_set else TEXT_PRIMARY
                    canvas.create_text(90, y, text=term, fill=tc,
                                       font=(FONT_FAMILY, 7), anchor="nw")
                    postings_str = ", ".join(sorted(snap[term]))
                    canvas.create_text(250, y, text=f"[{postings_str}]",
                                       fill=TEXT_PRIMARY,
                                       font=(FONT_FAMILY, 7), anchor="nw")
                    y += 12
                remaining = len(sorted_terms) - scroll_start - len(visible_terms)
                if remaining > 0:
                    canvas.create_text(90, y, text=f"... ({remaining} below)",
                                       fill=TEXT_SECONDARY,
                                       font=(FONT_FAMILY, 7), anchor="nw")

                canvas.create_text(20, H - 25,
                                   text=f"Terms: {len(snap)}  |  Processing: {cur_doc}",
                                   fill=TEXT_SECONDARY,
                                   font=(FONT_FAMILY, 8), anchor="nw")
            return draw
        steps.append((make_draw(snapshot, current_doc, new_t, step_i), dur))

    return steps


def _anim_boolean(ld, highlight):
    if not ld.index.index:
        ld.index.build(ld.corpus.docs, config=ld.config)

    postings_q = sorted(ld.index.get_postings("quantum"))
    postings_i = sorted(ld.index.get_postings("inflation"))
    intersection = sorted(set(postings_q) & set(postings_i))

    dur = 500
    steps = []

    def draw1(canvas):
        _draw_title(canvas, "Boolean Search: quantum AND inflation")
        canvas.create_text(W // 2, 60, text='query = "quantum AND inflation"',
                           fill=ANIM_HIGHLIGHT, font=(FONT_FAMILY, 11, "bold"),
                           anchor="n")
        canvas.create_text(W // 2, 90, text="Step 1: Parse query into terms",
                           fill=TEXT_SECONDARY, font=(FONT_FAMILY, 9), anchor="n")
    steps.append((draw1, dur))

    def draw2(canvas):
        _draw_title(canvas, "Boolean Search: quantum AND inflation")
        canvas.create_text(20, 50, text='postings("quantum"):', fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
        x = 20
        for d in postings_q:
            canvas.create_rectangle(x, 75, x + 45, 95, fill=ACCENT_DIM, outline="")
            canvas.create_text(x + 22, 85, text=d, fill=TEXT_PRIMARY,
                               font=(FONT_FAMILY, 8))
            x += 55
    steps.append((draw2, dur))

    def draw3(canvas):
        _draw_title(canvas, "Boolean Search: quantum AND inflation")
        canvas.create_text(20, 50, text='postings("quantum"):', fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
        x = 20
        for d in postings_q:
            canvas.create_rectangle(x, 75, x + 45, 95, fill=ACCENT_DIM, outline="")
            canvas.create_text(x + 22, 85, text=d, fill=TEXT_PRIMARY,
                               font=(FONT_FAMILY, 8))
            x += 55
        canvas.create_text(20, 115, text='postings("inflation"):', fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
        x = 20
        for d in postings_i:
            canvas.create_rectangle(x, 140, x + 45, 160, fill=ACCENT_DIM, outline="")
            canvas.create_text(x + 22, 150, text=d, fill=TEXT_PRIMARY,
                               font=(FONT_FAMILY, 8))
            x += 55
    steps.append((draw3, dur))

    def draw4(canvas):
        _draw_title(canvas, "Boolean Search: quantum AND inflation")
        canvas.create_text(20, 50, text='postings("quantum"):', fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
        x = 20
        for d in postings_q:
            color = ANIM_ADDED if d in intersection else ANIM_FADEOUT
            canvas.create_rectangle(x, 75, x + 45, 95, fill=color, outline="")
            canvas.create_text(x + 22, 85, text=d, fill=TEXT_PRIMARY
                               if d in intersection else BG_DEEP,
                               font=(FONT_FAMILY, 8))
            x += 55
        canvas.create_text(20, 115, text='postings("inflation"):', fill=ACCENT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
        x = 20
        for d in postings_i:
            color = ANIM_ADDED if d in intersection else ANIM_FADEOUT
            canvas.create_rectangle(x, 140, x + 45, 160, fill=color, outline="")
            canvas.create_text(x + 22, 150, text=d, fill=TEXT_PRIMARY
                               if d in intersection else BG_DEEP,
                               font=(FONT_FAMILY, 8))
            x += 55
        canvas.create_text(20, 185, text="AND = Intersection:", fill=ANIM_HIGHLIGHT,
                           font=(FONT_FAMILY, 9, "bold"), anchor="nw")
    steps.append((draw4, dur))

    def draw5(canvas):
        _draw_title(canvas, "Boolean Search: quantum AND inflation")
        canvas.create_text(W // 2, 80, text="Result:", fill=ACCENT,
                           font=(FONT_FAMILY, 11, "bold"), anchor="n")
        x = (W - len(intersection) * 55) // 2
        for d in intersection:
            canvas.create_rectangle(x, 110, x + 45, 135, fill=ANIM_ADDED, outline="")
            canvas.create_text(x + 22, 122, text=d, fill=TEXT_PRIMARY,
                               font=(FONT_FAMILY, 9, "bold"))
            x += 55
        canvas.create_text(W // 2, 165,
                           text=f"{len(intersection)} documents contain both terms",
                           fill=TEXT_SECONDARY, font=(FONT_FAMILY, 9), anchor="n")
    steps.append((draw5, dur))

    return steps


def _anim_tfidf(ld, highlight):
    if not ld.index.index:
        ld.index.build(ld.corpus.docs, config=ld.config)

    results = tfidf_rank(_TFIDF_QUERY, ld.index, ld.corpus.docs,
                         config=ld.config)
    results = results[:8]
    max_score = results[0][1] if results and results[0][1] > 0 else 1.0
    n = len(results)
    dur = _duration(n + 2)
    steps = []

    q_tokens = configurable_pipeline(_TFIDF_QUERY, ld.config)

    def draw_query(canvas):
        _draw_title(canvas, f'TF-IDF Search: "{_TFIDF_QUERY}"')
        y = 50
        for t in q_tokens:
            idf_val = math.log(len(ld.corpus.docs) / max(ld.index.df(t), 1))
            canvas.create_text(20, y, text=f"{t}  (IDF={idf_val:.2f})",
                               fill=ACCENT, font=(FONT_FAMILY, 9), anchor="nw")
            y += 20
    steps.append((draw_query, dur))

    for step_i in range(1, n + 1):
        def make_draw(si):
            def draw(canvas):
                _draw_title(canvas, f'TF-IDF Search: "{_TFIDF_QUERY}"')
                bar_y = 50
                bar_max_w = 350
                for ri in range(n):
                    doc_id, score = results[ri]
                    label = f"{doc_id}"
                    canvas.create_text(20, bar_y + 7, text=label,
                                       fill=TEXT_PRIMARY,
                                       font=(FONT_FAMILY, 8), anchor="nw")
                    if ri < si:
                        bw = max(2, int(bar_max_w * score / max_score))
                        color = ANIM_ADDED if ri == si - 1 else ACCENT
                        canvas.create_rectangle(65, bar_y, 65 + bw, bar_y + 18,
                                               fill=color, outline="")
                        canvas.create_text(70 + bw, bar_y + 7,
                                           text=f"{score:.3f}",
                                           fill=TEXT_SECONDARY,
                                           font=(FONT_FAMILY, 7), anchor="nw")
                    else:
                        canvas.create_rectangle(65, bar_y, 67, bar_y + 18,
                                               fill=ANIM_FADEOUT, outline="")
                    bar_y += 28
            return draw
        steps.append((make_draw(step_i), dur))

    def draw_final(canvas):
        _draw_title(canvas, f'TF-IDF Search: "{_TFIDF_QUERY}" — Ranked Results')
        bar_y = 50
        bar_max_w = 350
        for ri, (doc_id, score) in enumerate(results):
            canvas.create_text(20, bar_y + 7, text=doc_id, fill=TEXT_PRIMARY,
                               font=(FONT_FAMILY, 8), anchor="nw")
            bw = max(2, int(bar_max_w * score / max_score))
            color = ANIM_ADDED if ri == 0 else ACCENT
            canvas.create_rectangle(65, bar_y, 65 + bw, bar_y + 18,
                                   fill=color, outline="")
            canvas.create_text(70 + bw, bar_y + 7, text=f"{score:.3f}",
                               fill=TEXT_SECONDARY,
                               font=(FONT_FAMILY, 7), anchor="nw")
            bar_y += 28
    steps.append((draw_final, dur))

    return steps


def _anim_evaluation(ld, highlight):
    if not ld.index.index:
        ld.index.build(ld.corpus.docs, config=ld.config)

    results = tfidf_rank(_EVAL_QUERY, ld.index, ld.corpus.docs,
                         config=ld.config)
    retrieved = [doc_id for doc_id, _ in results[:10]]
    pr_points = precision_recall_curve(retrieved, _EVAL_RELEVANT)
    n = len(retrieved)
    dur = _duration(n)

    ax_x, ax_y, ax_w, ax_h = 300, 50, 250, 250

    steps = []
    for step_i in range(1, n + 1):
        def make_draw(si):
            def draw(canvas):
                _draw_title(canvas, f'Evaluation: "{_EVAL_QUERY}"')
                canvas.create_text(20, 40, text="Ranked results:", fill=ACCENT,
                                   font=(FONT_FAMILY, 9, "bold"), anchor="nw")
                y = 60
                for ri in range(si):
                    doc_id = retrieved[ri]
                    is_rel = doc_id in _EVAL_RELEVANT
                    marker = "\u25cf" if is_rel else "\u25cb"
                    color = ANIM_ADDED if is_rel else ANIM_FADEOUT
                    canvas.create_text(20, y,
                                       text=f"{ri+1}. {marker} {doc_id}",
                                       fill=color, font=(FONT_FAMILY, 8),
                                       anchor="nw")
                    y += 16

                canvas.create_rectangle(ax_x, ax_y, ax_x + ax_w, ax_y + ax_h,
                                       outline=TEXT_SECONDARY, width=1)
                canvas.create_text(ax_x + ax_w // 2, ax_y + ax_h + 15,
                                   text="Recall", fill=TEXT_SECONDARY,
                                   font=(FONT_FAMILY, 8))
                canvas.create_text(ax_x - 15, ax_y + ax_h // 2,
                                   text="P", fill=TEXT_SECONDARY,
                                   font=(FONT_FAMILY, 8))
                prev_px, prev_py = None, None
                for pi in range(si):
                    recall, precision = pr_points[pi]
                    px = ax_x + int(recall * ax_w)
                    py = ax_y + ax_h - int(precision * ax_h)
                    color = ACCENT if pi < si - 1 else ANIM_HIGHLIGHT
                    canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                                      fill=color, outline="")
                    if prev_px is not None:
                        canvas.create_line(prev_px, prev_py, px, py,
                                          fill=ACCENT, width=1)
                    prev_px, prev_py = px, py

                recall, precision = pr_points[si - 1]
                canvas.create_text(20, H - 25,
                                   text=f"P@{si}={precision:.2f}  R@{si}={recall:.2f}",
                                   fill=TEXT_SECONDARY,
                                   font=(FONT_FAMILY, 9), anchor="nw")
            return draw
        steps.append((make_draw(step_i), dur))

    return steps


def _anim_crawl(ld, highlight):
    graph, nodes = ld.link_graph, ld.link_nodes
    seed = highlight[0] if highlight and highlight[0] in graph.nodes() else "d1"
    crawl_steps = list(crawl_bfs(graph, seed, max_depth=3, max_pages=10))

    nodes = sorted(graph.nodes())
    n_nodes = len(nodes)
    positions = {}
    cx, cy, r = W // 2, H // 2 + 10, min(W, H) // 2 - 50
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n_nodes - math.pi / 2
        positions[node] = (cx + int(r * math.cos(angle)),
                           cy + int(r * math.sin(angle)))

    dur = _duration(len(crawl_steps) + 1)
    steps = []

    def draw_initial(canvas):
        _draw_title(canvas, "BFS Web Crawl — Graph Overview")
        for n1 in nodes:
            for n2 in graph.neighbors(n1):
                if n2 in positions and n1 in positions:
                    x1, y1 = positions[n1]
                    x2, y2 = positions[n2]
                    canvas.create_line(x1, y1, x2, y2,
                                      fill=ANIM_FADEOUT, width=1)
        for node in nodes:
            x, y = positions[node]
            color = ANIM_HIGHLIGHT if node == seed else ANIM_FADEOUT
            canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                              fill=color, outline="")
            canvas.create_text(x, y, text=node,
                               fill=TEXT_PRIMARY if node == seed else BG_DEEP,
                               font=(FONT_FAMILY, 7, "bold"))
        canvas.create_text(20, H - 20,
                           text=f"Seed: {seed} | Ready to crawl",
                           fill=TEXT_SECONDARY,
                           font=(FONT_FAMILY, 8), anchor="nw")
    steps.append((draw_initial, dur))

    for step_i, cstep in enumerate(crawl_steps):
        visited = set(cstep["visited"])
        current = cstep["current"]
        frontier = set(cstep.get("frontier", []))

        def make_draw(vis, cur, front):
            def draw(canvas):
                _draw_title(canvas, "BFS Web Crawl")
                for n1 in nodes:
                    for n2 in graph.neighbors(n1):
                        if n2 in positions and n1 in positions:
                            x1, y1 = positions[n1]
                            x2, y2 = positions[n2]
                            canvas.create_line(x1, y1, x2, y2,
                                              fill=ANIM_FADEOUT, width=1)
                for node in nodes:
                    x, y = positions[node]
                    if node == cur:
                        color = ACCENT
                    elif node in vis:
                        color = ANIM_ADDED
                    elif node in front:
                        color = ANIM_HIGHLIGHT
                    else:
                        color = ANIM_FADEOUT
                    canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                      fill=color, outline="")
                    canvas.create_text(x, y, text=node, fill=TEXT_PRIMARY
                                       if color != ANIM_FADEOUT else BG_DEEP,
                                       font=(FONT_FAMILY, 7, "bold"))
                canvas.create_text(20, H - 20,
                                   text=f"Visited: {len(vis)} | Current: {cur}",
                                   fill=TEXT_SECONDARY,
                                   font=(FONT_FAMILY, 8), anchor="nw")
            return draw
        steps.append((make_draw(visited, current, frontier), dur))

    return steps


def _anim_pagerank(ld, highlight):
    graph, nodes = ld.link_graph, ld.link_nodes
    iterations = pagerank(graph, damping=0.85, iterations=10)
    nodes = sorted(graph.nodes())
    n_nodes = len(nodes)

    positions = {}
    cx, cy, r = W // 2, H // 2 + 10, min(W, H) // 2 - 50
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n_nodes - math.pi / 2
        positions[node] = (cx + int(r * math.cos(angle)),
                           cy + int(r * math.sin(angle)))

    dur = 500
    steps = []

    def draw_graph(canvas):
        _draw_title(canvas, "PageRank — Link Graph Overview")
        for n1 in nodes:
            for n2 in graph.neighbors(n1):
                if n2 in positions and n1 in positions:
                    x1, y1 = positions[n1]
                    x2, y2 = positions[n2]
                    canvas.create_line(x1, y1, x2, y2,
                                      fill=ANIM_FADEOUT, width=1)
        for node in nodes:
            x, y = positions[node]
            out_deg = len(graph.neighbors(node))
            in_deg = len(graph.in_neighbors(node))
            canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                              fill=ACCENT_DIM, outline="")
            canvas.create_text(x, y, text=node, fill=TEXT_PRIMARY,
                               font=(FONT_FAMILY, 7, "bold"))
            canvas.create_text(x, y + 20, text=f"in:{in_deg} out:{out_deg}",
                               fill=TEXT_SECONDARY,
                               font=(FONT_FAMILY, 6))
        canvas.create_text(20, H - 20,
                           text=f"{n_nodes} nodes | {graph.number_of_edges()} edges | Ready to run PageRank",
                           fill=TEXT_SECONDARY,
                           font=(FONT_FAMILY, 8), anchor="nw")
    steps.append((draw_graph, dur))

    for iter_i, scores in enumerate(iterations):
        max_score = max(scores.values()) if scores else 1.0
        max_node = max(scores, key=scores.get) if scores else ""

        def make_draw(sc, mx_s, mx_n, it):
            def draw(canvas):
                _draw_title(canvas, f"PageRank — Iteration {it + 1}")
                bar_y = 50
                bar_max_w = 380
                for node in nodes:
                    score = sc.get(node, 0)
                    canvas.create_text(20, bar_y + 7, text=node,
                                       fill=TEXT_PRIMARY,
                                       font=(FONT_FAMILY, 8), anchor="nw")
                    bw = max(2, int(bar_max_w * score / mx_s)) if mx_s > 0 else 2
                    color = ACCENT if node == mx_n else TEXT_SECONDARY
                    canvas.create_rectangle(65, bar_y, 65 + bw, bar_y + 18,
                                           fill=color, outline="")
                    canvas.create_text(70 + bw, bar_y + 7,
                                       text=f"{score:.4f}",
                                       fill=TEXT_SECONDARY,
                                       font=(FONT_FAMILY, 7), anchor="nw")
                    bar_y += 22
                    if bar_y > H - 30:
                        break
                canvas.create_text(20, H - 20,
                                   text=f"Highest: {mx_n} ({mx_s:.4f})",
                                   fill=ACCENT,
                                   font=(FONT_FAMILY, 8), anchor="nw")
            return draw
        steps.append((make_draw(dict(scores), max_score, max_node, iter_i), dur))

    return steps
