# Phase 1: Data Ingestion & Representations

## 1. `src/data_structures/graph_loader.py`
- `load_snap_facebook(data_dir="data/raw") -> nx.Graph`:
  - If `data/raw/facebook_combined.txt.gz` is missing, download from `https://snap.stanford.edu/data/facebook_combined.txt.gz`.
  - Parse gzipped space-separated edgelist (`nodetype=int`) into an undirected `nx.Graph`.
- `load_custom_edgelist(uploaded_file) -> nx.Graph`:
  - Parse uploaded `.txt` or `.csv` edgelist into `nx.Graph` (`nodetype=int`).
- `sample_connected_subgraph(G: nx.Graph, n_nodes: int) -> nx.Graph`:
  - Start BFS from the highest-degree node in `G`, collect first `n_nodes` visited, return `G.subgraph(nodes).copy()`.
- `get_graph_summary(G: nx.Graph) -> dict`:
  - Return `{"nodes": int, "edges": int, "density": float, "avg_degree": float, "is_connected": bool}`.

## 2. `src/data_structures/representations.py`
- `compare_representations(G: nx.Graph) -> list[dict]`:
  - Convert `G` into 3 structures and measure construction time (`time_ms`) and exact byte footprint (`memory_kb`):
    1. **Adjacency List**: Python `dict[int, list[int]]` (recursive size calculation).
    2. **Sparse CSR Matrix**: `scipy.sparse.csr_matrix` (`data.nbytes + indices.nbytes + indptr.nbytes`).
    3. **Dense Adjacency Matrix**: `numpy.ndarray` (`dtype=np.uint8`, `nbytes`).
  - Return list of dicts with keys: `format, memory_kb, build_time_ms, space_complexity, edge_lookup_complexity`.