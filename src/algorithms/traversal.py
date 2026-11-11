"""Graph traversal and connected-component statistics."""

from collections import deque
import time

import networkx as nx


def _reconstruct_path(parent: dict[int, int | None], target: int) -> list[int]:
    """Reconstruct shortest path from BFS parent pointers."""
    path: list[int] = []
    curr: int | None = target
    while curr is not None:
        path.append(int(curr))
        curr = parent[curr]
    path.reverse()
    return path


def bfs_shortest_path(G: nx.Graph, source: int, target: int) -> dict:
    """Find shortest path via manual deque BFS while tracking explored node count."""
    source = int(source)
    target = int(target)

    if source not in G or target not in G:
        raise ValueError(f"Source ({source}) or target ({target}) node not found in graph.")

    t0 = time.perf_counter()
    if source == target:
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return {
            "path": [source],
            "hops": 0,
            "visited_count": 1,
            "time_ms": elapsed_ms,
        }

    visited: set[int] = {source}
    parent: dict[int, int | None] = {source: None}
    queue: deque[int] = deque([source])
    found = False

    while queue and not found:
        current = queue.popleft()
        for neighbor in G.neighbors(current):
            neighbor = int(neighbor)
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            if neighbor == target:
                found = True
                break
            queue.append(neighbor)

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    if not found:
        return {
            "path": [],
            "hops": -1,
            "visited_count": len(visited),
            "time_ms": elapsed_ms,
        }

    path = _reconstruct_path(parent, target)
    return {
        "path": path,
        "hops": len(path) - 1,
        "visited_count": len(visited),
        "time_ms": elapsed_ms,
    }


def get_component_stats(G: nx.Graph) -> dict:
    """Compute connected-component summary statistics and approximate diameter."""
    if G.number_of_nodes() == 0:
        return {
            "num_components": 0,
            "largest_cc_size": 0,
            "diameter_approx": 0,
        }

    components = list(nx.connected_components(G))
    largest_cc = max(components, key=len)
    largest_subgraph = G.subgraph(largest_cc)
    diameter_approx = (
        int(nx.approximation.diameter(largest_subgraph, seed=42))
        if len(largest_cc) > 1
        else 0
    )

    return {
        "num_components": len(components),
        "largest_cc_size": len(largest_cc),
        "diameter_approx": diameter_approx,
    }

