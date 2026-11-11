"""Node centrality computation (Degree, PageRank, k-pivot Betweenness)."""

import time

import networkx as nx
import pandas as pd
import scipy.sparse  # Preload to prevent lazy-import latency in initial PageRank timing.


def compute_centralities(G: nx.Graph, k_pivots: int = 100) -> dict:
    """Compute degree, PageRank, and sampled betweenness centralities for all nodes."""
    columns = ["node", "degree", "pagerank", "betweenness"]
    if G.number_of_nodes() == 0:
        return {
            "df": pd.DataFrame(columns=columns),
            "timings_ms": {"degree": 0.0, "pagerank": 0.0, "betweenness": 0.0},
        }

    t0 = time.perf_counter()
    degree_scores = nx.degree_centrality(G)
    degree_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    t0 = time.perf_counter()
    pagerank_scores = nx.pagerank(G)
    pagerank_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    k = max(1, min(int(k_pivots), len(G)))
    t0 = time.perf_counter()
    betweenness_scores = nx.betweenness_centrality(G, k=k, seed=42)
    betweenness_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    rows = [
        {
            "node": int(node),
            "degree": float(degree_scores[node]),
            "pagerank": float(pagerank_scores[node]),
            "betweenness": float(betweenness_scores[node]),
        }
        for node in G.nodes()
    ]
    df = pd.DataFrame(rows, columns=columns)
    df = df.sort_values(by="pagerank", ascending=False).reset_index(drop=True)

    return {
        "df": df,
        "timings_ms": {
            "degree": degree_ms,
            "pagerank": pagerank_ms,
            "betweenness": betweenness_ms,
        },
    }
