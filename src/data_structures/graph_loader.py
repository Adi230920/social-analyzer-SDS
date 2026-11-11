"""Graph loading, sampling, and summary utilities."""

from collections import deque
import csv
import gzip
import os
from pathlib import Path

import networkx as nx
import requests

SNAP_FACEBOOK_URL = "https://snap.stanford.edu/data/facebook_combined.txt.gz"
SNAP_FACEBOOK_FILENAME = "facebook_combined.txt.gz"


def load_snap_facebook(data_dir="data/raw") -> nx.Graph:
    """Load the SNAP ego-Facebook dataset as an undirected int-node graph.

    Downloads ``facebook_combined.txt.gz`` into ``data_dir`` if not present locally.
    """
    target_dir = Path(data_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / SNAP_FACEBOOK_FILENAME

    if not file_path.exists():
        temp_path = target_dir / f"{SNAP_FACEBOOK_FILENAME}.part"
        try:
            with requests.get(SNAP_FACEBOOK_URL, stream=True, timeout=60) as response:
                response.raise_for_status()
                with temp_path.open("wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            out_file.write(chunk)
            temp_path.replace(file_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    with gzip.open(file_path, "rb") as gz_file:
        return nx.read_edgelist(gz_file, create_using=nx.Graph, nodetype=int)


def _read_uploaded_text(uploaded_file) -> tuple[str, str]:
    """Read UTF-8 text and lowercase filename from a path or file-like object."""
    if isinstance(uploaded_file, (str, os.PathLike)):
        path = Path(uploaded_file)
        raw_bytes = path.read_bytes()
        if raw_bytes.startswith(b"\x1f\x8b"):
            raw_bytes = gzip.decompress(raw_bytes)
        return raw_bytes.decode("utf-8-sig"), path.name.lower()

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    raw = uploaded_file.read()
    name = str(getattr(uploaded_file, "name", "")).lower()

    if isinstance(raw, (bytes, bytearray)):
        raw_bytes = bytes(raw)
        if raw_bytes.startswith(b"\x1f\x8b"):
            raw_bytes = gzip.decompress(raw_bytes)
        return raw_bytes.decode("utf-8-sig"), name
    if isinstance(raw, str):
        return raw.lstrip("\ufeff"), name

    raise TypeError("uploaded_file must be a path or a file-like object returning str or bytes.")


def _parse_edge_tokens(line: str, is_csv: bool) -> list[str]:
    """Split a non-empty edgelist line into stripped field tokens."""
    if "," in line:
        return [tok.strip() for tok in next(csv.reader([line])) if tok.strip() != ""]
    if is_csv and ";" in line:
        return [tok.strip() for tok in next(csv.reader([line], delimiter=";")) if tok.strip() != ""]
    return line.split()


def load_custom_edgelist(uploaded_file) -> nx.Graph:
    """Parse an uploaded .txt or .csv edgelist into an undirected int-node nx.Graph."""
    text, filename = _read_uploaded_text(uploaded_file)
    is_csv = filename.endswith(".csv")

    G = nx.Graph()
    seen_first_row = False

    for line_num, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(("#", "%")):
            continue

        tokens = _parse_edge_tokens(stripped, is_csv=is_csv)
        if len(tokens) < 2:
            if not seen_first_row:
                seen_first_row = True
                continue
            raise ValueError(f"Line {line_num} does not contain at least two node IDs: {raw_line!r}")

        try:
            u = int(tokens[0])
            v = int(tokens[1])
        except ValueError as exc:
            if not seen_first_row:
                # Skip a single non-numeric header row (e.g., "source,target").
                seen_first_row = True
                continue
            raise ValueError(f"Line {line_num} contains non-integer node IDs: {raw_line!r}") from exc

        seen_first_row = True
        G.add_edge(u, v)

    return G


def sample_connected_subgraph(G: nx.Graph, n_nodes: int) -> nx.Graph:
    """Sample a connected subgraph of up to n_nodes via BFS from the highest-degree node."""
    if n_nodes <= 0 or G.number_of_nodes() == 0:
        return nx.Graph()

    start_node = max(G.nodes, key=lambda node: G.degree(node))
    visited = [start_node]
    seen = {start_node}
    queue = deque([start_node])

    while queue and len(visited) < n_nodes:
        current = queue.popleft()
        for neighbor in G.neighbors(current):
            if neighbor not in seen:
                seen.add(neighbor)
                visited.append(neighbor)
                if len(visited) >= n_nodes:
                    break
                queue.append(neighbor)

    return G.subgraph(visited).copy()


def get_graph_summary(G: nx.Graph) -> dict:
    """Return structural summary metrics for an undirected graph."""
    num_nodes = int(G.number_of_nodes())
    num_edges = int(G.number_of_edges())
    density = float(nx.density(G))
    avg_degree = float((2 * num_edges) / num_nodes) if num_nodes > 0 else 0.0
    is_connected = bool(nx.is_connected(G)) if num_nodes > 0 else False

    return {
        "nodes": num_nodes,
        "edges": num_edges,
        "density": density,
        "avg_degree": avg_degree,
        "is_connected": is_connected,
    }

