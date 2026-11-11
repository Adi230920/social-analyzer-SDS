"""Streamlit application entrypoint for the SDS Social Network Analyzer."""

import hashlib
import io

import networkx as nx
import pandas as pd
import streamlit as st

from src.algorithms.centrality import compute_centralities
from src.algorithms.communities import detect_communities
from src.algorithms.traversal import get_component_stats
from src.data_structures.graph_loader import (
    get_graph_summary,
    load_custom_edgelist,
    load_snap_facebook,
    sample_connected_subgraph,
)
from src.data_structures.representations import compare_representations
from src.profiler.benchmark import run_scaling_benchmark
from ui.tabs import render_tabs

st.set_page_config(page_title="SDS Social Network Analyzer", layout="wide")


def _inject_custom_css() -> None:
    """Inject global custom CSS for the SaaS-style dark theme."""
    st.markdown(
        """
        <style>
        /* ── Typography ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }
        code, pre, .stCode {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Hide default chrome ── */
        #MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }
        div.block-container { padding-top: 1.5rem; }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #131825 !important;
            border-right: 1px solid #1E293B !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 0.5rem;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.9rem;
        }

        /* ── Pill-style Tabs ── */
        button[data-baseweb="tab"] {
            background: #131825 !important;
            border: 1px solid #1E293B !important;
            border-radius: 8px !important;
            color: #94A3B8 !important;
            padding: 0.5rem 1.25rem !important;
            margin-right: 0.5rem !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            transition: all 0.2s ease !important;
        }
        button[data-baseweb="tab"]:hover {
            background: #1A2035 !important;
            color: #E2E8F0 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0,212,255,0.12), rgba(167,139,250,0.12)) !important;
            border-color: #00D4FF !important;
            color: #E2E8F0 !important;
            font-weight: 600 !important;
        }
        div[data-baseweb="tab-highlight"] { display: none !important; }
        div[data-baseweb="tab-border"] { display: none !important; }

        /* ── DataFrames ── */
        .stDataFrame, [data-testid="stDataFrame"] {
            border: 1px solid #1E293B;
            border-radius: 10px;
            overflow: hidden;
        }

        /* ── Buttons ── */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #00D4FF, #A78BFA) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            color: #0B0F19 !important;
            transition: opacity 0.2s ease !important;
        }
        .stButton > button[kind="primary"]:hover,
        .stButton > button[data-testid="baseButton-primary"]:hover {
            opacity: 0.88 !important;
        }
        .stDownloadButton > button {
            border: 1px solid #1E293B !important;
            border-radius: 8px !important;
            background: #131825 !important;
            color: #E2E8F0 !important;
            transition: all 0.2s ease !important;
        }
        .stDownloadButton > button:hover {
            background: #1A2035 !important;
            border-color: #00D4FF !important;
        }

        /* ── Selectbox / Slider / Radio ── */
        .stSelectbox, .stSlider, .stRadio {
            margin-bottom: 0.5rem;
        }

        /* ── Expander ── */
        details[data-testid="stExpander"] {
            border: 1px solid #1E293B !important;
            border-radius: 10px !important;
            background: #131825 !important;
        }

        /* ── Success / Warning / Info alerts ── */
        .stAlert { border-radius: 8px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


_inject_custom_css()


@st.cache_resource(show_spinner="Loading SNAP ego-Facebook dataset...")
def get_snap_graph() -> nx.Graph:
    """Load and cache the full SNAP ego-Facebook graph."""
    return load_snap_facebook()


@st.cache_resource(show_spinner="Parsing uploaded edgelist...")
def get_custom_graph(file_name: str, file_bytes: bytes) -> nx.Graph:
    """Parse and cache an uploaded custom edgelist graph."""
    buffer = io.BytesIO(file_bytes)
    buffer.name = file_name
    return load_custom_edgelist(buffer)


@st.cache_resource(show_spinner="Sampling connected subgraph...")
def get_working_graph(source_key: str, n_nodes: int, _base_graph: nx.Graph) -> nx.Graph:
    """Return a cached connected subgraph (or full graph when n_nodes >= total)."""
    if n_nodes >= _base_graph.number_of_nodes():
        return _base_graph
    return sample_connected_subgraph(_base_graph, n_nodes)


@st.cache_data(show_spinner=False)
def cached_graph_summary(graph_key: str, _G: nx.Graph) -> dict:
    """Compute and cache structural graph summary metrics."""
    return get_graph_summary(_G)


@st.cache_data(show_spinner=False)
def cached_representations(graph_key: str, _G: nx.Graph) -> list[dict]:
    """Compute and cache data structure footprint comparisons."""
    return compare_representations(_G)


@st.cache_data(show_spinner=False)
def cached_component_stats(graph_key: str, _G: nx.Graph) -> dict:
    """Compute and cache connected-component statistics."""
    return get_component_stats(_G)


@st.cache_data(show_spinner="Computing node centralities...")
def cached_centralities(graph_key: str, k_pivots: int, _G: nx.Graph) -> dict:
    """Compute and cache degree, PageRank, and k-pivot betweenness centralities."""
    return compute_centralities(_G, k_pivots=k_pivots)


@st.cache_data(show_spinner="Detecting Louvain communities...")
def cached_communities(graph_key: str, _G: nx.Graph) -> dict:
    """Compute and cache Louvain community partition and clustering metrics."""
    return detect_communities(_G)


@st.cache_data(show_spinner=False)
def cached_scaling_benchmark(
    source_key: str,
    sizes: tuple[int, ...],
    _base_graph: nx.Graph,
) -> pd.DataFrame:
    """Run and cache the empirical scaling benchmark for a dataset."""
    return run_scaling_benchmark(_base_graph, sizes=list(sizes))


def _resolve_benchmark_sizes(total_nodes: int) -> tuple[int, ...]:
    """Build valid ascending benchmark subgraph sizes up to total_nodes."""
    if total_nodes >= 4039:
        return (250, 500, 1000, 2000, 4039)
    if total_nodes <= 0:
        return ()
    candidates = [size for size in (250, 500, 1000, 2000) if size < total_nodes]
    if not candidates and total_nodes > 4:
        half = max(2, total_nodes // 2)
        if half < total_nodes:
            candidates.append(half)
    candidates.append(total_nodes)
    return tuple(candidates)


def main() -> None:
    """Render sidebar configuration and main analysis tabs."""
    st.markdown(
        '<h1 style="font-size:2rem;font-weight:700;letter-spacing:-0.03em;margin-bottom:0;">'
        '<span style="color:#00D4FF;">⬡</span> Social Network Analyzer</h1>'
        '<p style="color:#94A3B8;font-size:0.92rem;margin-top:0.15rem;margin-bottom:1.5rem;">'
        'Large-Scale Graph Analytics &amp; Profiling Platform</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:0.5rem;'
            'padding:0.5rem 0 1rem 0;border-bottom:1px solid #1E293B;margin-bottom:1rem;">'
            '<span style="font-size:1.3rem;">⚙️</span>'
            '<span style="font-weight:600;font-size:1.05rem;color:#E2E8F0;">Configuration</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        dataset_choice = st.radio(
            "Dataset Source",
            options=["SNAP ego-Facebook", "Upload Custom Edgelist"],
            key="dataset_source",
        )

        if dataset_choice == "SNAP ego-Facebook":
            base_graph = get_snap_graph()
            source_key = "snap_facebook"
            dataset_label = "SNAP ego-Facebook"
        else:
            uploaded = st.file_uploader(
                "Upload Edgelist (.txt or .csv)",
                type=["txt", "csv"],
                key="custom_edgelist_uploader",
            )
            if uploaded is None:
                st.info("Upload a `.txt` or `.csv` integer edgelist to begin analysis.")
                st.stop()
            file_bytes = uploaded.getvalue()
            digest = hashlib.sha256(file_bytes).hexdigest()[:12]
            try:
                base_graph = get_custom_graph(uploaded.name, file_bytes)
            except Exception as exc:
                st.error(f"Failed to parse uploaded edgelist: {exc}")
                st.stop()
            source_key = f"custom:{uploaded.name}:{digest}"
            dataset_label = f"Custom ({uploaded.name})"

        total_nodes = int(base_graph.number_of_nodes())
        if total_nodes > 500:
            default_nodes = min(1000, total_nodes)
            n_nodes = st.slider(
                "Subgraph Sample Size (Nodes)",
                min_value=500,
                max_value=total_nodes,
                value=default_nodes,
                step=100 if total_nodes - 500 >= 100 else 1,
                key="subgraph_size_slider",
            )
        else:
            n_nodes = total_nodes
            st.caption(f"Analyzing full uploaded graph ({total_nodes} nodes).")

        k_pivots = st.slider(
            "Betweenness k-Pivots",
            min_value=25,
            max_value=200,
            value=100,
            step=25,
            key="k_pivots_slider",
        )

    working_graph = get_working_graph(source_key, n_nodes, base_graph)
    graph_key = (
        f"{source_key}|n={working_graph.number_of_nodes()}"
        f"|e={working_graph.number_of_edges()}"
    )

    summary = cached_graph_summary(graph_key, working_graph)
    rep_list = cached_representations(graph_key, working_graph)
    comp_stats = cached_component_stats(graph_key, working_graph)
    centralities = cached_centralities(graph_key, k_pivots, working_graph)
    communities = cached_communities(graph_key, working_graph)

    bench_sizes = _resolve_benchmark_sizes(total_nodes)

    def _run_benchmark() -> pd.DataFrame:
        return cached_scaling_benchmark(source_key, bench_sizes, base_graph)

    render_tabs(
        G=working_graph,
        dataset_label=f"{dataset_label} ({summary['nodes']:,} nodes)",
        source_key=source_key,
        summary=summary,
        rep_list=rep_list,
        comp_stats=comp_stats,
        centralities=centralities,
        communities=communities,
        run_benchmark_fn=_run_benchmark,
        k_pivots=k_pivots,
    )


if __name__ == "__main__":
    main()

