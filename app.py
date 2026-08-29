from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
import gradio as gr
from slw.core import (
    expiring_block_schedule, live_counts, semantic_lifetime_width,
    linear_preservation_volume, semantic_state_volume, fixed_state_volume,
    clique_parity_metrics, path_index_metrics, slw_from_class_count,
    quotient_class_counts,
)


def expiring(stages, block_size, lifetime, core_states):
    s = expiring_block_schedule(int(stages), int(block_size), int(lifetime))
    core_states = int(core_states)
    lc = live_counts(s)
    qc = quotient_class_counts(s, core_states=core_states)
    df = pd.DataFrame({"stage": range(len(lc)), "unexpired_distinctions": lc, "future_class_bound": qc})
    retired = semantic_state_volume(s, core_states=core_states)
    fixed = fixed_state_volume(s, core_states=core_states)
    metrics = pd.DataFrame([{
        "distinctions": s.n_distinctions,
        "core_states": core_states,
        "SLW_bits": semantic_lifetime_width(s, core_states=core_states),
        "linear_lifetime_volume": linear_preservation_volume(s),
        "retired_state_volume": retired,
        "fixed_state_volume": fixed,
        "fixed/retired": fixed / retired,
    }])
    return metrics, df


def separation(n):
    n = int(n)
    return pd.DataFrame([
        {"family": "clique-parity", **clique_parity_metrics(n)},
        {"family": "path-index", **path_index_metrics(n)},
    ])


def query_compare(n):
    n = int(n)
    return pd.DataFrame([
        {"structure": "same sequential input", "query": "parity", "future_classes": 2, "SLW_bits": 1, "output_bits": 1},
        {"structure": "same sequential input", "query": "indexed bit", "future_classes": 2**n, "SLW_bits": n, "output_bits": 1},
    ])


def quotient_explorer(class_count):
    c = int(class_count)
    return pd.DataFrame([{"future_equivalence_classes": c, "SLW_bits": slw_from_class_count(c)}])


with gr.Blocks(title="Semantic Lifetime Width Lab") as demo:
    gr.Markdown("# Semantic Lifetime Width Lab\nInteractive companion for query-relative future quotients and certified state retirement.")
    with gr.Tab("Expiring-history DP"):
        with gr.Row():
            stages = gr.Slider(2, 40, value=16, step=1, label="Stages")
            block = gr.Slider(1, 12, value=4, step=1, label="Distinctions born per stage")
            life = gr.Slider(1, 10, value=2, step=1, label="Certified lifetime")
            core = gr.Slider(1, 32, value=1, step=1, label="Core states")
        btn = gr.Button("Run")
        metrics = gr.Dataframe(label="Metrics")
        profile = gr.Dataframe(label="Stage profile")
        btn.click(expiring, [stages, block, life, core], [metrics, profile])
    with gr.Tab("Structural separation"):
        n = gr.Slider(2, 100, value=20, step=1, label="n")
        b = gr.Button("Compare")
        out = gr.Dataframe(label="Pathwidth vs query-relative SLW")
        b.click(separation, n, out)
    with gr.Tab("Same structure, different query"):
        nq = gr.Slider(2, 200, value=32, step=1, label="Input bits")
        bq = gr.Button("Compare one-bit queries")
        oq = gr.Dataframe(label="Query-sensitive future quotient")
        bq.click(query_compare, nq, oq)
    with gr.Tab("Quotient explorer"):
        cc = gr.Slider(1, 1_000_000, value=2, step=1, label="Future-equivalence classes")
        bc = gr.Button("Compute SLW")
        oc = gr.Dataframe(label="Width")
        bc.click(quotient_explorer, cc, oc)

if __name__ == "__main__":
    demo.launch()
