# Phase 3: Streamlit UI & Visualizers

## 1. `ui/visualizers.py`
- `render_pyvis_graph(G: nx.Graph, node_to_comm: dict, path: list[int] = None, max_nodes: int = 200) -> str`:
  - Sample up to `max_nodes` around `path` (if provided) or highest-degree hub.
  - Color nodes by community (`node_to_comm`), size by degree, highlight `path` edges in red (`width=4`).
  - Use `pyvis.network.Network(height="550px", width="100%", bgcolor="#0e1117", font_color="white")`, `barnes_hut()`, return HTML string.
- `plot_rep_comparison(rep_list: list[dict]) -> plotly.graph_objects.Figure`:
  - Grouped bar chart comparing `memory_kb` and `build_time_ms` across Adjacency List, CSR, and Dense Matrix.
- `plot_scaling_benchmarks(df: pd.DataFrame) -> tuple`:
  - Return two Plotly line charts: `time_ms` vs `n_nodes` and `peak_kb` vs `n_nodes` grouped by `algorithm`.

## 2. `ui/tabs.py` & `app.py`
- `app.py`:
  - Set `st.set_page_config(page_title="SDS Social Network Analyzer", layout="wide")`.
  - Sidebar: Dataset source (`SNAP ego-Facebook` or file upload), subgraph slider (`500` to `4039`), Betweenness `k_pivots` slider (`25` to `200`).
  - Cache graph loading and centrality/community outputs using `@st.cache_data` / `@st.cache_resource`.
- `ui/tabs.py` (4 Tabs):
  1. **Overview & DS Design**: Summary metric cards + `compare_representations` table and bar chart.
  2. **Network Explorer**: Top-15 influencers DataFrame, Louvain modularity stats, BFS shortest-path finder (`source`/`target` selectors), and embedded PyVis HTML (`st.components.v1.html`).
  3. **Scalability Analysis**: Trigger/display `run_scaling_benchmark` charts + Big-O reference table.
  4. **Export Report**: Generate downloadable Markdown report and centrality `.csv` via `st.download_button`.