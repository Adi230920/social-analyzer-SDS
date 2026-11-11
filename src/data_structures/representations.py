"""Graph memory-layout representations and footprint comparison."""

import sys
import time

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix


def _deep_getsizeof(obj: object, seen: set[int] | None = None) -> int:
    """Recursively measure exact byte footprint of nested Python containers."""
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        for key, value in obj.items():
            size += _deep_getsizeof(key, seen)
            size += _deep_getsizeof(value, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            size += _deep_getsizeof(item, seen)
    return size


def compare_representations(G: nx.Graph) -> list[dict]:
    """Compare build time and memory footprint across Adjacency List, CSR, and Dense Matrix."""
    t0 = time.perf_counter()
    adj_list: dict[int, list[int]] = {
        int(u): [int(v) for v in G.neighbors(u)] for u in G.nodes()
    }
    adj_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    adj_bytes = _deep_getsizeof(adj_list)

    t0 = time.perf_counter()
    csr = csr_matrix(nx.to_scipy_sparse_array(G, dtype=np.uint8, format="csr"))
    csr_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    csr_bytes = int(csr.data.nbytes + csr.indices.nbytes + csr.indptr.nbytes)

    t0 = time.perf_counter()
    dense = nx.to_numpy_array(G, dtype=np.uint8)
    dense_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    dense_bytes = int(dense.nbytes)

    return [
        {
            "format": "Adjacency List",
            "memory_kb": round(adj_bytes / 1024.0, 2),
            "build_time_ms": adj_time_ms,
            "space_complexity": "O(V + E)",
            "edge_lookup_complexity": "O(deg(u))",
        },
        {
            "format": "Sparse CSR Matrix",
            "memory_kb": round(csr_bytes / 1024.0, 2),
            "build_time_ms": csr_time_ms,
            "space_complexity": "O(V + E)",
            "edge_lookup_complexity": "O(log(deg(u)))",
        },
        {
            "format": "Dense Adjacency Matrix",
            "memory_kb": round(dense_bytes / 1024.0, 2),
            "build_time_ms": dense_time_ms,
            "space_complexity": "O(V^2)",
            "edge_lookup_complexity": "O(1)",
        },
    ]

