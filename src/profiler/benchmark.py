"""Scalability benchmarking across subgraph sizes for core graph algorithms."""

from collections import deque
import time
import tracemalloc

import networkx as nx
import pandas as pd
import scipy.sparse  # Preload to prevent lazy-import latency in initial PageRank timing.

from src.algorithms.traversal import bfs_shortest_path
from src.data_structures.graph_loader import sample_connected_subgraph


def _find_bfs_endpoints(G: nx.Graph) -> tuple[int, int]:
    """Pick the highest-degree node and the last node reached by BFS from it."""
    source = max(G.nodes, key=lambda node: G.degree(node))
    visited = {source}
    queue = deque([source])
    last_node = source

    while queue:
        current = queue.popleft()
        last_node = current
        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return int(source), int(last_node)


def _profile_callable(fn) -> tuple[float, float]:
    """Measure uninstrumented wall-clock time (ms) and tracemalloc peak memory (KB)."""
    t0 = time.perf_counter()
    fn()
    time_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    was_tracing = tracemalloc.is_tracing()
    if was_tracing:
        tracemalloc.reset_peak()
    else:
        tracemalloc.start()

    try:
        fn()
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        if not was_tracing:
            tracemalloc.stop()

    peak_kb = round(peak_bytes / 1024.0, 2)
    return time_ms, peak_kb


def run_scaling_benchmark(
    G: nx.Graph,
    sizes=[250, 500, 1000, 2000, 4039],
) -> pd.DataFrame:
    """Benchmark runtime and peak memory across subgraph sizes for 4 core algorithms."""
    columns = ["n_nodes", "n_edges", "algorithm", "time_ms", "peak_kb"]
    if G.number_of_nodes() == 0 or not sizes:
        return pd.DataFrame(columns=columns)

    rows: list[dict] = []
    for target_size in sizes:
        sub = sample_connected_subgraph(G, int(target_size))
        n_nodes = int(sub.number_of_nodes())
        n_edges = int(sub.number_of_edges())
        if n_nodes == 0:
            continue

        source, target = _find_bfs_endpoints(sub)
        k_betweenness = max(1, min(50, n_nodes))

        workloads = [
            ("BFS", lambda s=sub, src=source, dst=target: bfs_shortest_path(s, src, dst)),
            ("PageRank", lambda s=sub: nx.pagerank(s)),
            (
                "Betweenness (k=50)",
                lambda s=sub, k=k_betweenness: nx.betweenness_centrality(s, k=k, seed=42),
            ),
            ("Louvain", lambda s=sub: nx.community.louvain_communities(s, seed=42)),
        ]

        for algo_name, fn in workloads:
            time_ms, peak_kb = _profile_callable(fn)
            rows.append(
                {
                    "n_nodes": n_nodes,
                    "n_edges": n_edges,
                    "algorithm": algo_name,
                    "time_ms": time_ms,
                    "peak_kb": peak_kb,
                }
            )

    return pd.DataFrame(rows, columns=columns)
