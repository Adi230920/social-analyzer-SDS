# Phase 4: Verification, Docs & Viva Readiness

## 1. `verify_pipeline.py`
Create a standalone CLI test script that executes sequentially and exits `0` only if all assertions pass:
1. Call `load_snap_facebook()` and assert `nodes == 4039` and `edges == 88234`.
2. Sample 500-node subgraph via `sample_connected_subgraph(G, 500)`.
3. Run `compare_representations` and assert `CSR memory_kb < Dense Matrix memory_kb`.
4. Run `bfs_shortest_path` between two valid nodes and assert `hops >= 1`.
5. Run `compute_centralities(k_pivots=30)` and `detect_communities()`, asserting valid non-empty returns.
6. Run `run_scaling_benchmark(G, sizes=[200, 500])` and assert 8 rows returned.
7. Print `"ALL SDS PIPELINE CHECKS PASSED"`.

## 2. `VIVA_NOTES.md` & `README.md`
- `README.md`: Setup instructions, CLI verification command, `streamlit run app.py` command, and SDS rubric mapping.
- `VIVA_NOTES.md`: Concise technical reference explaining:
  - Space complexity: Adjacency List $O(V+E)$, CSR $O(V+E)$ contiguous arrays, Dense Matrix $O(V^2)$.
  - Brandes' Betweenness exact $O(VE)$ vs $k$-pivot approximation $O(kE)$.
  - Power-law degree distributions, clustering coefficient, and Louvain modularity optimization.