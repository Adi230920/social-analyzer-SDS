"""Standalone CLI verification pipeline for the SDS Social Network Analyzer."""

import ast
import pathlib
import sys

from src.algorithms.centrality import compute_centralities
from src.algorithms.communities import detect_communities
from src.algorithms.traversal import bfs_shortest_path, get_component_stats
from src.data_structures.graph_loader import (
    get_graph_summary,
    load_snap_facebook,
    sample_connected_subgraph,
)
from src.data_structures.representations import compare_representations
from src.profiler.benchmark import run_scaling_benchmark


def _check_no_streamlit_in_src() -> None:
    """Verify strict separation of concerns: src/ must not import streamlit."""
    for py_file in pathlib.Path("src").rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("streamlit"), (
                        f"Forbidden streamlit import in {py_file}"
                    )
            elif isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("streamlit"), (
                    f"Forbidden streamlit import in {py_file}"
                )


def main() -> int:
    """Run sequential end-to-end assertions and return 0 only on full pass."""
    _check_no_streamlit_in_src()

    # 1. Load SNAP ego-Facebook and assert full graph counts.
    G = load_snap_facebook()
    summary = get_graph_summary(G)
    assert summary["nodes"] == 4039, f"Expected 4039 nodes, got {summary['nodes']}"
    assert summary["edges"] == 88234, f"Expected 88234 edges, got {summary['edges']}"

    # 2. Sample 500-node connected subgraph.
    sub = sample_connected_subgraph(G, 500)
    assert sub.number_of_nodes() == 500, f"Expected 500 sampled nodes, got {sub.number_of_nodes()}"
    comp_stats = get_component_stats(sub)
    assert comp_stats["num_components"] == 1, "Sampled subgraph must be connected"
    assert comp_stats["largest_cc_size"] == 500

    # 3. Compare representations and verify CSR footprint < Dense Matrix footprint.
    reps = compare_representations(sub)
    rep_by_format = {item["format"]: item for item in reps}
    assert "Sparse CSR Matrix" in rep_by_format
    assert "Dense Adjacency Matrix" in rep_by_format
    csr_kb = rep_by_format["Sparse CSR Matrix"]["memory_kb"]
    dense_kb = rep_by_format["Dense Adjacency Matrix"]["memory_kb"]
    assert csr_kb < dense_kb, f"Expected CSR ({csr_kb} KB) < Dense ({dense_kb} KB)"

    # 4. Run BFS shortest path between two distinct valid nodes.
    sub_nodes = list(sub.nodes())
    source = int(sub_nodes[0])
    target = int(next(n for n in reversed(sub_nodes) if int(n) != source))
    bfs_res = bfs_shortest_path(sub, source, target)
    assert bfs_res["hops"] >= 1, f"Expected hops >= 1, got {bfs_res['hops']}"
    assert bfs_res["path"][0] == source and bfs_res["path"][-1] == target
    assert len(bfs_res["path"]) == bfs_res["hops"] + 1

    # 5. Compute centralities (k_pivots=30) and detect communities.
    cent_res = compute_centralities(sub, k_pivots=30)
    cent_df = cent_res["df"]
    assert not cent_df.empty and len(cent_df) == 500
    assert list(cent_df.columns) == ["node", "degree", "pagerank", "betweenness"]
    assert cent_df["pagerank"].is_monotonic_decreasing
    assert set(cent_res["timings_ms"].keys()) == {"degree", "pagerank", "betweenness"}

    comm_res = detect_communities(sub)
    assert len(comm_res["node_to_comm"]) == 500
    assert comm_res["num_communities"] >= 1
    assert sum(comm_res["comm_sizes"]) == 500
    assert comm_res["modularity"] > 0

    # 6. Run scaling benchmark on sizes=[200, 500] and assert 8 rows returned.
    bench_df = run_scaling_benchmark(G, sizes=[200, 500])
    assert list(bench_df.columns) == ["n_nodes", "n_edges", "algorithm", "time_ms", "peak_kb"]
    assert len(bench_df) == 8, f"Expected 8 benchmark rows, got {len(bench_df)}"

    # 7. Print completion banner.
    print("ALL SDS PIPELINE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"PIPELINE CHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

