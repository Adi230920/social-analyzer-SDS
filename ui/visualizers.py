"""Interactive PyVis network and Plotly analytical visualizations."""

from collections import deque
import math

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pyvis.network import Network

MAX_PYVIS_NODES = 200

# ── Design-token aligned palettes ──────────────────────────────────────────────

COMMUNITY_PALETTE = [
    "#00D4FF", "#A78BFA", "#10B981", "#F59E0B", "#EF4444",
    "#EC4899", "#06B6D4", "#84CC16", "#38BDF8", "#FB7185",
    "#FACC15", "#2DD4BF", "#C084FC", "#FB923C", "#8B5CF6",
    "#14B8A6", "#6366F1", "#EAB308", "#A855F7", "#22C55E",
]

CHART_COLORS = ["#00D4FF", "#A78BFA", "#10B981", "#F59E0B", "#EF4444", "#EC4899"]

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    title_font=dict(size=15, color="#E2E8F0"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#94A3B8"),
    ),
    margin=dict(t=60, b=40, l=50, r=20),
    hovermode="x unified",
)

_AXIS_STYLE = dict(gridcolor="#1E293B", zerolinecolor="#1E293B", linecolor="#1E293B")


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the unified dark transparent theme to any Plotly figure."""
    fig.update_layout(**_CHART_LAYOUT)
    fig.update_xaxes(**_AXIS_STYLE)
    fig.update_yaxes(**_AXIS_STYLE)
    return fig


# ── PyVis network rendering ───────────────────────────────────────────────────

def _bfs_collect(G: nx.Graph, seeds: list[int], seen: set[int], selected: list[int], cap: int) -> None:
    """Expand BFS from seed nodes in G until cap nodes are collected."""
    queue: deque[int] = deque()
    for seed in seeds:
        if len(selected) >= cap:
            return
        if seed not in seen:
            seen.add(seed)
            selected.append(seed)
            queue.append(seed)

    while queue and len(selected) < cap:
        current = queue.popleft()
        for neighbor in G.neighbors(current):
            neighbor = int(neighbor)
            if neighbor not in seen:
                seen.add(neighbor)
                selected.append(neighbor)
                if len(selected) >= cap:
                    return
                queue.append(neighbor)


def _sample_visual_nodes(G: nx.Graph, path: list[int] | None, cap: int) -> list[int]:
    """Select up to cap nodes centered on path (if valid) or highest-degree hub."""
    if G.number_of_nodes() == 0 or cap <= 0:
        return []

    seen: set[int] = set()
    selected: list[int] = []

    valid_path = [int(n) for n in (path or []) if int(n) in G]
    if valid_path:
        _bfs_collect(G, valid_path, seen, selected, cap)
    else:
        hub = int(max(G.nodes, key=lambda node: G.degree(node)))
        _bfs_collect(G, [hub], seen, selected, cap)

    if len(selected) < cap and len(selected) < G.number_of_nodes():
        remaining = sorted(
            (int(n) for n in G.nodes if int(n) not in seen),
            key=lambda node: G.degree(node),
            reverse=True,
        )
        for node in remaining:
            if len(selected) >= cap:
                break
            if node not in seen:
                _bfs_collect(G, [node], seen, selected, cap)

    return selected


def render_pyvis_graph(
    G: nx.Graph,
    node_to_comm: dict,
    path: list[int] = None,
    max_nodes: int = 200,
) -> str:
    """Render up to 200 nodes as an interactive dark-themed PyVis HTML network."""
    cap = min(max(1, int(max_nodes)), MAX_PYVIS_NODES)
    net = Network(
        height="550px",
        width="100%",
        bgcolor="#0B0F19",
        font_color="white",
        cdn_resources="in_line",
    )
    net.barnes_hut()

    selected_nodes = _sample_visual_nodes(G, path=path, cap=cap)
    if not selected_nodes:
        return net.generate_html()

    sub = G.subgraph(selected_nodes)
    path_nodes = {int(n) for n in (path or [])}
    path_edges = (
        {
            (min(int(path[i]), int(path[i + 1])), max(int(path[i]), int(path[i + 1])))
            for i in range(len(path) - 1)
        }
        if path and len(path) >= 2
        else set()
    )

    for node in sub.nodes():
        node_id = int(node)
        comm_id = int(node_to_comm.get(node_id, 0))
        fill_color = COMMUNITY_PALETTE[comm_id % len(COMMUNITY_PALETTE)]
        degree = int(G.degree(node))
        size = round(10.0 + min(30.0, 2.5 * math.sqrt(degree)), 1)
        tooltip = f"Node {node_id} | Community {comm_id} | Degree {degree}"

        if node_id in path_nodes:
            node_color = {
                "background": fill_color,
                "border": "#EF4444",
                "highlight": {"background": fill_color, "border": "#EF4444"},
            }
            border_width = 3
        else:
            node_color = fill_color
            border_width = 1

        net.add_node(
            node_id,
            label=str(node_id),
            title=tooltip,
            color=node_color,
            size=size,
            borderWidth=border_width,
        )

    for u, v in sub.edges():
        u_id, v_id = int(u), int(v)
        edge_key = (min(u_id, v_id), max(u_id, v_id))
        if edge_key in path_edges:
            net.add_edge(u_id, v_id, color="#EF4444", width=4)
        else:
            net.add_edge(u_id, v_id, color="rgba(160, 174, 192, 0.25)", width=1)

    return net.generate_html()


# ── Plotly chart builders ──────────────────────────────────────────────────────

def plot_rep_comparison(rep_list: list[dict]) -> go.Figure:
    """Create a grouped dual-axis bar chart of memory_kb and build_time_ms across formats."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if not rep_list:
        fig.update_layout(
            title="Graph Representation Memory & Build Time Comparison",
        )
        return _apply_theme(fig)

    formats = [item["format"] for item in rep_list]
    memory_vals = [item["memory_kb"] for item in rep_list]
    timing_vals = [item["build_time_ms"] for item in rep_list]

    fig.add_trace(
        go.Bar(
            name="Memory (KB)",
            x=formats,
            y=memory_vals,
            offsetgroup=0,
            marker_color="#00D4FF",
            marker_line=dict(width=0),
            text=memory_vals,
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(color="#94A3B8", size=11),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name="Build Time (ms)",
            x=formats,
            y=timing_vals,
            offsetgroup=1,
            marker_color="#A78BFA",
            marker_line=dict(width=0),
            text=timing_vals,
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(color="#94A3B8", size=11),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Graph Representation Memory & Build Time Comparison",
        barmode="group",
    )
    fig.update_yaxes(title_text="Memory Footprint (KB)", secondary_y=False)
    fig.update_yaxes(title_text="Build Time (ms)", secondary_y=True)
    return _apply_theme(fig)


def _build_scaling_line_chart(
    df: pd.DataFrame,
    y_col: str,
    y_title: str,
    title: str,
) -> go.Figure:
    """Build a dark-themed Plotly line chart grouped by algorithm."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title=title)
        return _apply_theme(fig)

    fig = px.line(
        df,
        x="n_nodes",
        y=y_col,
        color="algorithm",
        markers=True,
        title=title,
        labels={
            "n_nodes": "Subgraph Size (Nodes)",
            y_col: y_title,
            "algorithm": "Algorithm",
        },
        color_discrete_sequence=CHART_COLORS,
    )
    return _apply_theme(fig)


def plot_scaling_benchmarks(df: pd.DataFrame) -> tuple:
    """Return Plotly line charts for execution time and peak memory vs subgraph size."""
    fig_time = _build_scaling_line_chart(
        df,
        y_col="time_ms",
        y_title="Execution Time (ms)",
        title="Algorithm Runtime Scaling (time_ms vs n_nodes)",
    )
    fig_memory = _build_scaling_line_chart(
        df,
        y_col="peak_kb",
        y_title="Peak Traced Memory (KB)",
        title="Algorithm Memory Scaling (peak_kb vs n_nodes)",
    )
    return fig_time, fig_memory
