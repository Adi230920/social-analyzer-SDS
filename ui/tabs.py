"""Streamlit multi-tab UI views wired to backend analytics and visualizers."""

from typing import Callable

import networkx as nx
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.algorithms.traversal import bfs_shortest_path
from ui.visualizers import plot_rep_comparison, plot_scaling_benchmarks, render_pyvis_graph

BIG_O_REFERENCE = [
    {
        "Component": "Adjacency List (dict[int, list[int]])",
        "Category": "Data Structure",
        "Time / Lookup": "O(deg(u)) edge check",
        "Space Complexity": "O(V + E)",
    },
    {
        "Component": "Sparse CSR Matrix (scipy.sparse)",
        "Category": "Data Structure",
        "Time / Lookup": "O(log(deg(u))) edge check",
        "Space Complexity": "O(V + E)",
    },
    {
        "Component": "Dense Adjacency Matrix (uint8 ndarray)",
        "Category": "Data Structure",
        "Time / Lookup": "O(1) edge check",
        "Space Complexity": "O(V²)",
    },
    {
        "Component": "BFS Shortest Path",
        "Category": "Traversal",
        "Time / Lookup": "O(V + E)",
        "Space Complexity": "O(V)",
    },
    {
        "Component": "Degree Centrality",
        "Category": "Centrality",
        "Time / Lookup": "O(V)",
        "Space Complexity": "O(V)",
    },
    {
        "Component": "PageRank (Power Iteration)",
        "Category": "Centrality",
        "Time / Lookup": "O(I × (V + E))",
        "Space Complexity": "O(V + E)",
    },
    {
        "Component": "Brandes Betweenness (k-pivot)",
        "Category": "Centrality",
        "Time / Lookup": "O(k × (V + E)) vs O(V × E) exact",
        "Space Complexity": "O(V + E)",
    },
    {
        "Component": "Louvain Modularity Optimization",
        "Category": "Community Detection",
        "Time / Lookup": "O(E) per pass (heuristic)",
        "Space Complexity": "O(V + E)",
    },
]


# ── Reusable UI components ─────────────────────────────────────────────────────

def _kpi_card(label: str, value: str, icon: str = "📊") -> str:
    """Return an HTML KPI card with icon, value, and label."""
    return f'''
    <div style="
        background: #131825;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        text-align: center;
        transition: border-color 0.2s ease;
    ">
        <div style="font-size:1.25rem; margin-bottom:0.2rem;">{icon}</div>
        <div style="font-size:1.45rem; font-weight:700; color:#E2E8F0;
                    letter-spacing:-0.02em; line-height:1.2;">{value}</div>
        <div style="font-size:0.72rem; color:#94A3B8;
                    margin-top:0.35rem; text-transform:uppercase;
                    letter-spacing:0.06em; font-weight:500;">{label}</div>
    </div>'''


def _render_kpi_row(cards: list[tuple[str, str, str]]) -> None:
    """Render a row of KPI cards. Each tuple is (label, value, icon)."""
    cols = st.columns(len(cards))
    for col, (label, value, icon) in zip(cols, cards):
        col.markdown(_kpi_card(label, value, icon), unsafe_allow_html=True)


def _section_heading(title: str, subtitle: str = "") -> None:
    """Render a styled section heading with optional subtitle."""
    sub_html = (
        f'<p style="color:#94A3B8;font-size:0.84rem;margin-top:0.1rem;margin-bottom:0;">'
        f'{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f'<h3 style="color:#E2E8F0;font-weight:600;font-size:1.15rem;'
        f'margin-bottom:0.15rem;margin-top:0.5rem;">{title}</h3>{sub_html}',
        unsafe_allow_html=True,
    )


def _styled_divider() -> None:
    """Render a subtle themed horizontal rule."""
    st.markdown(
        '<hr style="border:none;border-top:1px solid #1E293B;margin:1.5rem 0;">',
        unsafe_allow_html=True,
    )


# ── Tab renderers ──────────────────────────────────────────────────────────────

def _render_overview_tab(summary: dict, comp_stats: dict, rep_list: list[dict]) -> None:
    """Render Tab 1: Graph summary metrics and representation comparison."""
    _section_heading("Graph Structural Summary", "Key topological metrics for the active graph")

    _render_kpi_row([
        ("Nodes", f"{summary['nodes']:,}", "🔵"),
        ("Edges", f"{summary['edges']:,}", "🔗"),
        ("Density", f"{summary['density']:.5f}", "📐"),
        ("Avg Degree", f"{summary['avg_degree']:.2f}", "📊"),
        ("Connected",
         "Yes" if summary["is_connected"]
         else f"No ({comp_stats['num_components']} CCs)", "🌐"),
    ])

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    _render_kpi_row([
        ("Connected Components", f"{comp_stats['num_components']:,}", "🧩"),
        ("Largest Component", f"{comp_stats['largest_cc_size']:,}", "🏔️"),
        ("Approx. Diameter", f"{comp_stats['diameter_approx']}", "📏"),
    ])

    _styled_divider()
    _section_heading("Data Structure Memory & Construction Trade-offs",
                     "Comparing adjacency list, sparse CSR, and dense matrix representations")
    rep_df = pd.DataFrame(rep_list)
    st.dataframe(rep_df, use_container_width=True, hide_index=True)
    st.plotly_chart(plot_rep_comparison(rep_list), use_container_width=True)


def _render_explorer_tab(
    G: nx.Graph,
    centralities: dict,
    communities: dict,
    k_pivots: int,
) -> None:
    """Render Tab 2: Influencers, Louvain communities, BFS path finder, and PyVis graph."""
    _section_heading("Louvain Community Detection & Clustering",
                     "Modularity-based partitioning and local clustering coefficients")

    _render_kpi_row([
        ("Communities", f"{communities['num_communities']}", "🏘️"),
        ("Modularity (Q)", f"{communities['modularity']:.4f}", "📈"),
        ("Avg Clustering", f"{communities['avg_clustering']:.4f}", "🔄"),
        ("Triangles", f"{communities['triangles']:,}", "🔺"),
        ("Detection Time", f"{communities['time_ms']:.2f} ms", "⏱️"),
    ])

    if communities["comm_sizes"]:
        top_sizes = ", ".join(str(sz) for sz in communities["comm_sizes"][:8])
        st.markdown(
            f'<p style="color:#94A3B8;font-size:0.82rem;margin-top:0.5rem;">'
            f'Largest community sizes (nodes): {top_sizes}</p>',
            unsafe_allow_html=True,
        )

    _styled_divider()
    left_col, right_col = st.columns([1.15, 1.0])

    with left_col:
        _section_heading("Top-15 Influencers", "Sorted by PageRank centrality score")
        top15_df = centralities["df"].head(15)
        st.dataframe(top15_df, use_container_width=True, hide_index=True)
        timings = centralities["timings_ms"]
        st.markdown(
            f'<p style="color:#94A3B8;font-size:0.8rem;margin-top:0.25rem;">'
            f'⏱ Degree: {timings["degree"]:.2f} ms &nbsp;|&nbsp; '
            f'PageRank: {timings["pagerank"]:.2f} ms &nbsp;|&nbsp; '
            f'Betweenness (k={k_pivots}): {timings["betweenness"]:.2f} ms</p>',
            unsafe_allow_html=True,
        )

    with right_col:
        _section_heading("BFS Shortest-Path Finder", "Select source and target nodes")
        if G.number_of_nodes() == 0:
            st.warning("Graph is empty; no nodes available for BFS traversal.")
            bfs_path: list[int] | None = None
        else:
            sorted_nodes = sorted(int(n) for n in G.nodes())
            ranked_nodes = [int(n) for n in centralities["df"]["node"].tolist()]
            default_src = ranked_nodes[0] if ranked_nodes else sorted_nodes[0]
            default_dst = (
                ranked_nodes[min(14, len(ranked_nodes) - 1)]
                if len(ranked_nodes) > 1
                else sorted_nodes[-1]
            )
            if default_dst == default_src and len(sorted_nodes) > 1:
                default_dst = sorted_nodes[-1] if sorted_nodes[0] == default_src else sorted_nodes[0]

            src_idx = sorted_nodes.index(default_src)
            dst_idx = sorted_nodes.index(default_dst)

            s_col, t_col = st.columns(2)
            source = s_col.selectbox("Source Node", sorted_nodes, index=src_idx, key="bfs_source")
            target = t_col.selectbox("Target Node", sorted_nodes, index=dst_idx, key="bfs_target")

            bfs_result = bfs_shortest_path(G, source, target)

            _render_kpi_row([
                ("Hops",
                 "Unreachable" if bfs_result["hops"] < 0 else str(bfs_result["hops"]),
                 "🚶"),
                ("Nodes Explored", f"{bfs_result['visited_count']:,}", "🔍"),
                ("BFS Time", f"{bfs_result['time_ms']:.2f} ms", "⚡"),
            ])

            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

            if bfs_result["path"]:
                st.success("Shortest Path: " + " → ".join(str(n) for n in bfs_result["path"]))
                bfs_path = bfs_result["path"]
            else:
                st.warning(f"No path connects node {source} and node {target}.")
                bfs_path = None

    _styled_divider()
    _section_heading("Interactive Network Graph",
                     "PyVis visualization · Nodes colored by community, sized by degree · BFS path in red")
    # Framed PyVis canvas
    html_str = render_pyvis_graph(G, communities["node_to_comm"], path=bfs_path, max_nodes=200)
    st.markdown(
        '<div style="border:1px solid #1E293B;border-radius:12px;'
        'overflow:hidden;background:#0B0F19;">',
        unsafe_allow_html=True,
    )
    components.html(html_str, height=580, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_scalability_tab(
    source_key: str,
    run_benchmark_fn: Callable[[], pd.DataFrame],
) -> None:
    """Render Tab 3: On-demand scalability profiler charts and Big-O complexity table."""
    _section_heading("Empirical Scaling Profiler",
                     "Wall-clock latency and peak memory across connected subgraphs")
    st.markdown(
        '<p style="color:#94A3B8;font-size:0.85rem;">'
        'Profile <code style="color:#00D4FF;">time_ms</code> and '
        '<code style="color:#00D4FF;">peak_kb</code> (tracemalloc) '
        'for BFS, PageRank, Betweenness (k=50), and Louvain.</p>',
        unsafe_allow_html=True,
    )

    if "scaling_results" not in st.session_state:
        st.session_state["scaling_results"] = {}

    if st.button("🚀  Run Scaling Benchmark", type="primary", key="run_scaling_btn"):
        with st.spinner("Profiling BFS, PageRank, Betweenness (k=50), and Louvain across subgraph sizes..."):
            st.session_state["scaling_results"][source_key] = run_benchmark_fn()

    bench_df = st.session_state["scaling_results"].get(source_key)
    if bench_df is not None and not bench_df.empty:
        c1, c2 = st.columns(2)
        fig_time, fig_memory = plot_scaling_benchmarks(bench_df)
        c1.plotly_chart(fig_time, use_container_width=True)
        c2.plotly_chart(fig_memory, use_container_width=True)
        st.dataframe(bench_df, use_container_width=True, hide_index=True)
    else:
        st.info("Click **Run Scaling Benchmark** to profile runtime and memory scaling for the active dataset.")

    _styled_divider()
    _section_heading("Asymptotic Complexity Reference", "Big-O bounds for every algorithm and data structure")
    st.dataframe(pd.DataFrame(BIG_O_REFERENCE), use_container_width=True, hide_index=True)


def _df_to_markdown(df: pd.DataFrame) -> str:
    """Convert a small DataFrame to a GitHub-flavored Markdown table without extra deps."""
    if df.empty:
        return "_No rows._"
    headers = [str(col) for col in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in df.itertuples(index=False, name=None):
        formatted = []
        for val in row:
            if isinstance(val, float):
                formatted.append(f"{val:.6g}")
            else:
                formatted.append(str(val))
        lines.append("| " + " | ".join(formatted) + " |")
    return "\n".join(lines)


def _build_markdown_report(
    dataset_label: str,
    summary: dict,
    comp_stats: dict,
    rep_list: list[dict],
    centralities: dict,
    communities: dict,
    k_pivots: int,
    bench_df: pd.DataFrame | None,
) -> str:
    """Assemble a concise Markdown summary report for download."""
    sections = [
        "# SDS Social Network Analysis Report",
        f"- **Dataset**: {dataset_label}",
        f"- **Betweenness Pivots (k)**: {k_pivots}",
        "",
        "## 1. Structural Summary",
        f"- **Nodes**: {summary['nodes']:,}",
        f"- **Edges**: {summary['edges']:,}",
        f"- **Density**: {summary['density']:.6f}",
        f"- **Average Degree**: {summary['avg_degree']:.2f}",
        f"- **Connected**: {summary['is_connected']}",
        f"- **Connected Components**: {comp_stats['num_components']}",
        f"- **Largest Component Size**: {comp_stats['largest_cc_size']:,}",
        f"- **Approx. Diameter**: {comp_stats['diameter_approx']}",
        "",
        "## 2. Data Structure Comparison",
        _df_to_markdown(pd.DataFrame(rep_list)),
        "",
        "## 3. Community Detection (Louvain)",
        f"- **Communities**: {communities['num_communities']}",
        f"- **Modularity (Q)**: {communities['modularity']:.4f}",
        f"- **Average Clustering**: {communities['avg_clustering']:.4f}",
        f"- **Total Triangles**: {communities['triangles']:,}",
        f"- **Runtime (ms)**: {communities['time_ms']:.2f}",
        "",
        "## 4. Top-15 Influencers (by PageRank)",
        _df_to_markdown(centralities["df"].head(15)),
    ]

    if bench_df is not None and not bench_df.empty:
        sections.extend(["", "## 5. Scalability Benchmark", _df_to_markdown(bench_df)])

    return "\n".join(sections) + "\n"


def _render_export_tab(
    dataset_label: str,
    source_key: str,
    summary: dict,
    comp_stats: dict,
    rep_list: list[dict],
    centralities: dict,
    communities: dict,
    k_pivots: int,
) -> None:
    """Render Tab 4: Markdown summary report and CSV export downloads."""
    _section_heading("Export Analysis Report & Centrality Data",
                     "Download a full Markdown report or raw centrality CSV")
    bench_df = st.session_state.get("scaling_results", {}).get(source_key)

    report_md = _build_markdown_report(
        dataset_label=dataset_label,
        summary=summary,
        comp_stats=comp_stats,
        rep_list=rep_list,
        centralities=centralities,
        communities=communities,
        k_pivots=k_pivots,
        bench_df=bench_df,
    )
    centrality_csv = centralities["df"].to_csv(index=False)

    c1, c2 = st.columns(2)
    c1.download_button(
        label="📄  Download Report (.md)",
        data=report_md,
        file_name="social_network_report.md",
        mime="text/markdown",
    )
    c2.download_button(
        label="📊  Download Centrality (.csv)",
        data=centrality_csv,
        file_name="centralities.csv",
        mime="text/csv",
    )

    with st.expander("Preview Markdown Report", expanded=True):
        st.markdown(report_md)


def render_tabs(
    G: nx.Graph,
    dataset_label: str,
    source_key: str,
    summary: dict,
    rep_list: list[dict],
    comp_stats: dict,
    centralities: dict,
    communities: dict,
    run_benchmark_fn: Callable[[], pd.DataFrame],
    k_pivots: int,
) -> None:
    """Render the four main application tabs."""
    tab_overview, tab_explorer, tab_scalability, tab_export = st.tabs(
        [
            "📊  Overview & DS Design",
            "🌐  Network Explorer",
            "⚡  Scalability Analysis",
            "📥  Export Report",
        ]
    )

    with tab_overview:
        _render_overview_tab(summary=summary, comp_stats=comp_stats, rep_list=rep_list)

    with tab_explorer:
        _render_explorer_tab(
            G=G,
            centralities=centralities,
            communities=communities,
            k_pivots=k_pivots,
        )

    with tab_scalability:
        _render_scalability_tab(source_key=source_key, run_benchmark_fn=run_benchmark_fn)

    with tab_export:
        _render_export_tab(
            dataset_label=dataset_label,
            source_key=source_key,
            summary=summary,
            comp_stats=comp_stats,
            rep_list=rep_list,
            centralities=centralities,
            communities=communities,
            k_pivots=k_pivots,
        )
