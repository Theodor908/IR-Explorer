"""Run all predefined queries under multiple pipeline configs and produce an evaluation report."""

import sys
import os
import io
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ir_explorer.core.corpus import Corpus
from ir_explorer.core.index import InvertedIndex
from ir_explorer.core.preprocessing import PipelineConfig
from ir_explorer.core.retrieval import tfidf_rank
from ir_explorer.core.evaluation import precision_at_k, average_precision, mean_average_precision


CONFIGS = [
    ("Baseline", PipelineConfig(remove_stopwords=False, apply_stemming=False,
                                tf_scheme="raw", idf_scheme="standard")),
    ("+Stopwords", PipelineConfig(remove_stopwords=True, apply_stemming=False,
                                  tf_scheme="log", idf_scheme="standard")),
    ("+Stemming", PipelineConfig(remove_stopwords=True, apply_stemming=True,
                                 tf_scheme="log", idf_scheme="standard")),
    ("Full", PipelineConfig(remove_stopwords=True, apply_stemming=True,
                            tf_scheme="log", idf_scheme="smoothed")),
]

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "..", "ir_explorer", "assets", "default_corpus.json")
QUERIES_PATH = os.path.join(os.path.dirname(__file__), "..", "ir_explorer", "assets", "default_queries.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
REPORT_PATH = os.path.join(RESULTS_DIR, "evaluation_report.md")


def evaluate_query(query_text, relevant_set, index, corpus_docs, config):
    """Run a single query and return metrics dict with keys: p5, p10, ap, num_retrieved, num_relevant."""
    ranked = tfidf_rank(query_text, index, corpus_docs, config)
    # Filter to docs with score > 0
    retrieved = [doc_id for doc_id, score in ranked if score > 0]
    p5 = precision_at_k(retrieved, relevant_set, 5)
    p10 = precision_at_k(retrieved, relevant_set, 10)
    ap = average_precision(retrieved, relevant_set)
    return {
        "p5": p5,
        "p10": p10,
        "ap": ap,
        "num_retrieved": len(retrieved),
        "num_relevant": len(relevant_set),
    }


def run_all_queries(queries, index, corpus_docs, config):
    """Run all queries, return (list_of_result_dicts, map_score)."""
    results = []
    ap_pairs = []
    for q in queries:
        relevant_set = set(q["relevant"])
        metrics = evaluate_query(q["text"], relevant_set, index, corpus_docs, config)
        metrics["id"] = q["id"]
        metrics["text"] = q["text"]
        results.append(metrics)
        # Collect (retrieved, relevant) pairs for MAP
        ranked = tfidf_rank(q["text"], index, corpus_docs, config)
        retrieved = [doc_id for doc_id, score in ranked if score > 0]
        ap_pairs.append((retrieved, relevant_set))
    map_score = mean_average_precision(ap_pairs)
    return results, map_score


def format_report_table(rows, map_score, config_name):
    """Format results as a markdown table string."""
    lines = []
    lines.append(f"### {config_name}")
    lines.append("")
    lines.append("| Query | P@5 | P@10 | AP | Retrieved | Relevant |")
    lines.append("|-------|-----|------|----|-----------|----------|")
    for r in rows:
        lines.append(
            f"| {r['id']}: {r['text'][:40]} | {r['p5']:.3f} | {r['p10']:.3f} | {r['ap']:.3f} | {r['num_retrieved']} | {r['num_relevant']} |"
        )
    lines.append("")
    lines.append(f"**MAP = {map_score:.4f}**")
    lines.append("")
    return "\n".join(lines)


def main():
    # Load corpus
    corpus = Corpus()
    corpus.load_from_json(os.path.normpath(CORPUS_PATH))
    print(f"Loaded corpus: {len(corpus.docs)} documents")

    # Load queries
    with open(os.path.normpath(QUERIES_PATH), "r", encoding="utf-8") as f:
        queries = json.load(f)["queries"]
    print(f"Loaded {len(queries)} queries")
    print()

    report_sections = []
    report_sections.append("# Evaluation Report\n")

    map_summary = []

    for config_name, config in CONFIGS:
        print(f"=== {config_name} ===")
        index = InvertedIndex()
        index.build(corpus.docs, config)
        results, map_score = run_all_queries(queries, index, corpus.docs, config)

        table = format_report_table(results, map_score, config_name)
        print(table)
        report_sections.append(table)
        map_summary.append((config_name, map_score))

    # MAP comparison table
    comparison = []
    comparison.append("## MAP Comparison\n")
    comparison.append("| Configuration | MAP |")
    comparison.append("|---------------|-----|")
    for name, score in map_summary:
        comparison.append(f"| {name} | {score:.4f} |")
    comparison.append("")
    comparison_text = "\n".join(comparison)
    print(comparison_text)
    report_sections.append(comparison_text)

    # Write report
    os.makedirs(os.path.normpath(RESULTS_DIR), exist_ok=True)
    with open(os.path.normpath(REPORT_PATH), "w", encoding="utf-8") as f:
        f.write("\n".join(report_sections))
    print(f"\nReport written to {os.path.normpath(REPORT_PATH)}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
