# Phase 2: Algorithms & Scalability Profiler

## 1. `src/algorithms/traversal.py`
- `bfs_shortest_path(G: nx.Graph, source: int, target: int) -> dict`:
  - Implement manual queue-based BFS (`collections.deque`) to track exact nodes explored.
  - Return `{"path": list[int], "hops": int, "visited_count": int, "time_ms": float}`.
- `get_component_stats(G: nx.Graph) -> dict`:
  - Return `{"num_components": int, "largest_cc_size": int, "diameter_approx": int}`.

## 2. `src/algorithms/centrality.py`
- `compute_centralities(G: nx.Graph, k_pivots: int = 100) -> dict`:
  - Compute `nx.degree_centrality(G)`, `nx.pagerank(G)`, and `nx.betweenness_centrality(G, k=min(k_pivots, len(G)), seed=42)`.
  - Return `{"df": pd.DataFrame(columns=["node", "degree", "pagerank", "betweenness"]), "timings_ms": dict}`. Sort `df` by `pagerank` descending.

## 3. `src/algorithms/communities.py`
- `detect_communities(G: nx.Graph) -> dict`:
  - Run `nx.community.louvain_communities(G, seed=42)`.
  - Compute modularity (`nx.community.modularity`), `nx.average_clustering(G)`, and total triangles (`sum(nx.triangles(G).values()) // 3`).
  - Return `{"node_to_comm": dict[int, int], "modularity": float, "num_communities": int, "comm_sizes": list[int], "avg_clustering": float, "triangles": int, "time_ms": float}`.

## 4. `src/profiler/benchmark.py`
- `run_scaling_benchmark(G: nx.Graph, sizes=[250, 500, 1000, 2000, 4039]) -> pd.DataFrame`:
  - For each `n` in `sizes`, extract `sample_connected_subgraph(G, n)`.
  - Measure `time_ms` and peak `tracemalloc` (`peak_kb`) for: (1) BFS traversal, (2) PageRank, (3) Betweenness (`k=50`), (4) Louvain.
  - Return DataFrame with columns: `n_nodes, n_edges, algorithm, time_ms, peak_kb`.