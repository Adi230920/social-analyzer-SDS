# SDS Project: Large-Scale Social Network Analyzer

A modular graph analytics, data-structure benchmarking, and interactive visualization platform built on the **SNAP ego-Facebook** dataset (`4,039` nodes, `88,234` undirected edges) and custom user-uploaded edgelists.

## Architecture

The codebase enforces strict separation of concerns:

- `src/` contains pure graph ingestion, memory-layout profiling, algorithms, and scalability benchmarking with **zero** `streamlit` imports.
- `ui/` and `app.py` handle Streamlit caching (`@st.cache_resource` / `@st.cache_data`), layout, Plotly charts, and PyVis visualization (capped at `200` nodes).

```text
social-network-analyzer/
├── data/raw/                   # Cached SNAP ego-Facebook edgelist (.txt.gz)
├── src/
│   ├── data_structures/
│   │   ├── graph_loader.py     # SNAP download/loader, custom CSV/TXT loader, BFS sampling, summary
│   │   └── representations.py  # Adjacency List vs. Sparse CSR vs. Dense uint8 Matrix profiler
│   ├── algorithms/
│   │   ├── traversal.py        # Manual deque BFS shortest path & component statistics
│   │   ├── centrality.py       # Degree, PageRank, and k-pivot Betweenness centralities
│   │   └── communities.py      # Louvain communities, modularity, clustering, triangle count
│   └── profiler/
│       └── benchmark.py        # Wall-clock (ms) & tracemalloc peak memory (KB) scaling profiler
├── ui/
│   ├── visualizers.py          # PyVis interactive network (<=200 nodes) & Plotly figures
│   └── tabs.py                 # 4-tab Streamlit layout & Markdown/CSV export builders
├── app.py                      # Streamlit entrypoint with sidebar controls & caching
├── verify_pipeline.py          # End-to-end CLI verification script
├── requirements.txt            # Python package dependencies
├── README.md
└── VIVA_NOTES.md
```

## Setup Instructions

1. Create and activate an isolated virtual environment (PowerShell on Windows):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## CLI Verification

Run the sequential verification script to validate dataset loading, representation memory footprints, BFS shortest paths, centralities, Louvain communities, and scaling benchmarks:

```powershell
.\.venv\Scripts\python.exe verify_pipeline.py
```

Expected output on success (exit code `0`):
```text
ALL SDS PIPELINE CHECKS PASSED
```

## Running the Streamlit Dashboard

Launch the interactive web application from the project root:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

## SDS Rubric Mapping

| Rubric Area | Implementation | Key Modules & Functions |
|---|---|---|
| **Data Structures & Space Trade-offs** | Compares Python `dict[int, list[int]]` Adjacency List (recursive `sys.getsizeof`), `scipy.sparse.csr_matrix` (`uint8`), and `numpy.ndarray` (`uint8`) Dense Matrix | `src/data_structures/representations.py` (`compare_representations`) |
| **Data Ingestion & Subgraph Sampling** | Automatic SNAP dataset fetch/gzip parse, custom `.txt`/`.csv` parsing (`nodetype=int`), and BFS connected subgraph sampling from the highest-degree hub | `src/data_structures/graph_loader.py` (`load_snap_facebook`, `load_custom_edgelist`, `sample_connected_subgraph`, `get_graph_summary`) |
| **Graph Traversal & Connectivity** | Manual `collections.deque` BFS tracking exact explored node count + connected components and 2-sweep approximate diameter | `src/algorithms/traversal.py` (`bfs_shortest_path`, `get_component_stats`) |
| **Centrality & Influence Ranking** | Degree centrality, power-iteration PageRank, and seeded $k$-pivot Brandes Betweenness centrality sorted descending by PageRank | `src/algorithms/centrality.py` (`compute_centralities`) |
| **Community Structure & Clustering** | Louvain modularity optimization, modularity $Q$, average clustering coefficient, and total triangle counts | `src/algorithms/communities.py` (`detect_communities`) |
| **Scalability & Memory Profiling** | Measures `time.perf_counter()` (ms) and `tracemalloc` peak memory (KB) across subgraph sizes `[250, 500, 1000, 2000, 4039]` | `src/profiler/benchmark.py` (`run_scaling_benchmark`) |
| **Interactive Visualization & Reporting** | 4-tab Streamlit UI, dual-axis Plotly bar chart, scaling line charts, 200-node capped PyVis network with red BFS path highlighting, and `.md`/`.csv` downloads | `ui/visualizers.py`, `ui/tabs.py`, `app.py` |

