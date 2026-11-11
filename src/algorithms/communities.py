"""Community detection and clustering metrics via Louvain modularity optimization."""

import time

import networkx as nx


def detect_communities(G: nx.Graph) -> dict:
    """Detect communities with Louvain and compute modularity, clustering, and triangles."""
    if G.number_of_nodes() == 0:
        return {
            "node_to_comm": {},
            "modularity": 0.0,
            "num_communities": 0,
            "comm_sizes": [],
            "avg_clustering": 0.0,
            "triangles": 0,
            "time_ms": 0.0,
        }

    t0 = time.perf_counter()
    communities = sorted(
        nx.community.louvain_communities(G, seed=42),
        key=len,
        reverse=True,
    )

    node_to_comm: dict[int, int] = {}
    comm_sizes: list[int] = []
    for comm_id, members in enumerate(communities):
        comm_sizes.append(len(members))
        for node in members:
            node_to_comm[int(node)] = comm_id

    modularity = (
        float(nx.community.modularity(G, communities))
        if G.number_of_edges() > 0
        else 0.0
    )
    avg_clustering = float(nx.average_clustering(G))
    triangles = int(sum(nx.triangles(G).values()) // 3)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    return {
        "node_to_comm": node_to_comm,
        "modularity": modularity,
        "num_communities": len(communities),
        "comm_sizes": comm_sizes,
        "avg_clustering": avg_clustering,
        "triangles": triangles,
        "time_ms": elapsed_ms,
    }

