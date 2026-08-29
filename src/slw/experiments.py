from __future__ import annotations
import json, time
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from .core import (
    expiring_block_schedule, live_counts, semantic_lifetime_width,
    linear_preservation_volume, lifetime_sum, semantic_state_volume,
    fixed_state_volume, clique_parity_metrics, path_index_metrics,
    same_structure_query_metrics, log2_ratio, quotient_class_counts,
)


def run_experiments(outdir: str | Path, max_n: int = 24) -> dict:
    outdir = Path(outdir)
    tdir = outdir / "tables"
    fdir = outdir / "figures"
    tdir.mkdir(parents=True, exist_ok=True)
    fdir.mkdir(parents=True, exist_ok=True)

    rows = []
    for n in [4, 8, 12, 16, 20, 24]:
        rows.append({"family": "clique-parity", **clique_parity_metrics(n)})
        rows.append({"family": "path-index", **path_index_metrics(n)})
    sep = pd.DataFrame(rows)
    sep.to_csv(tdir / "separation.csv", index=False)

    rows = []
    for n in range(4, max_n + 1, 4):
        block = max(1, n // 4)
        sch = expiring_block_schedule(stages=n, block_size=block, lifetime=1)
        sv = semantic_state_volume(sch)
        fv = fixed_state_volume(sch)
        rows.append({
            "n": n,
            "block_size": block,
            "distinctions": sch.n_distinctions,
            "slw": semantic_lifetime_width(sch),
            "linear_volume": linear_preservation_volume(sch),
            "lifetime_sum": lifetime_sum(sch),
            "semantic_state_volume": sv,
            "fixed_state_volume": fv,
            "log2_fixed_over_retired": log2_ratio(fv, sv),
        })
    exp = pd.DataFrame(rows)
    exp.to_csv(tdir / "expiring_history.csv", index=False)

    qrows = []
    for n in [4, 8, 16, 32, 64]:
        qrows.extend(same_structure_query_metrics(n))
    qdf = pd.DataFrame(qrows)
    qdf.to_csv(tdir / "query_sensitivity.csv", index=False)

    bench = []
    for live in range(4, 19, 2):
        t0 = time.perf_counter()
        checksum = 0
        for x in range(2**live):
            checksum ^= x & 1
        dt = time.perf_counter() - t0
        bench.append({"live_bits": live, "states": 2**live, "seconds": dt, "checksum": checksum})
    bdf = pd.DataFrame(bench)
    bdf.to_csv(tdir / "enumeration_benchmark.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ns = [4, 8, 12, 16, 20, 24]
    ax.plot(ns, [n - 1 for n in ns], marker="o", label="pathwidth(K_n)")
    ax.plot(ns, [1] * len(ns), marker="s", label="SLW: clique-parity")
    ax.plot(ns, [1] * len(ns), marker="^", label="pathwidth(P_n)")
    ax.plot(ns, ns, marker="d", label="SLW: path-index")
    ax.set_xlabel("n")
    ax.set_ylabel("width (bits for SLW)")
    ax.set_title("Structural width and query-relative SLW separate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fdir / "separation.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(exp["n"], exp["log2_fixed_over_retired"], marker="o")
    ax.set_xlabel("stages n")
    ax.set_ylabel("log2(fixed volume / retired volume)")
    ax.set_title("Certified retirement reduces represented state volume")
    fig.tight_layout()
    fig.savefig(fdir / "volume_gap.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    p = qdf[qdf["query"] == "parity"]
    i = qdf[qdf["query"] == "indexed-bit"]
    ax.plot(p["n"], p["slw"], marker="o", label="parity query")
    ax.plot(i["n"], i["slw"], marker="s", label="indexed-bit query")
    ax.set_xlabel("input bits n")
    ax.set_ylabel("SLW (bits)")
    ax.set_title("Same structure, different one-bit queries")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fdir / "query_sensitivity.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(bdf["states"], bdf["seconds"], marker="o")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("explicit represented states")
    ax.set_ylabel("seconds")
    ax.set_title("Measured cost of explicit state enumeration")
    fig.tight_layout()
    fig.savefig(fdir / "enumeration_runtime.png", dpi=220)
    plt.close(fig)

    sch = expiring_block_schedule(stages=20, block_size=4, lifetime=3)
    lc = live_counts(sch)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.step(range(len(lc)), lc, where="post")
    ax.set_xlabel("stage")
    ax.set_ylabel("unexpired factorized distinctions")
    ax.set_title("Certified lifetime profile (20 stages, block=4, lifetime=3)")
    fig.tight_layout()
    fig.savefig(fdir / "lifetime_profile.png", dpi=220)
    plt.close(fig)

    summary = {
        "separation_rows": len(sep),
        "expiring_rows": len(exp),
        "query_rows": len(qdf),
        "benchmark_rows": len(bdf),
        "max_n": max_n,
        "checks": {
            "lifetime_accounting_all": bool((exp["linear_volume"] == exp["lifetime_sum"]).all()),
            "clique_two_future_classes": bool((sep[sep.family == "clique-parity"]["future_classes"] == 2).all()),
            "clique_constant_slw": bool((sep[sep.family == "clique-parity"]["slw"] == 1).all()),
            "path_linear_slw": bool((sep[sep.family == "path-index"]["slw"] == sep[sep.family == "path-index"]["n"]).all()),
            "state_volume_class_sum": all(
                semantic_state_volume(expiring_block_schedule(n, max(1, n // 4), 1))
                == sum(quotient_class_counts(expiring_block_schedule(n, max(1, n // 4), 1)))
                for n in range(4, max_n + 1, 4)
            ),
        },
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary
