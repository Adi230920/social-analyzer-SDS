# Technical Viva Notes: Large-Scale Social Network Analyzer

Quick technical reference covering the data structure trade-offs, algorithmic complexity, and social network properties demonstrated by this codebase.

---

## 1. Graph Representations & Space Complexity

Let $V = |V|$ be the number of nodes and $E = |E|$ be the number of undirected edges (requiring $2E$ directed adjacency entries in symmetric matrix/list layouts).

| Representation | Storage Layout | Space Complexity | Edge Lookup `(u, v)` | Trade-offs |
|---|---|---|---|---|
| **Adjacency List** | `dict[int, list[int]]` | $O(V + E)$ | $O(\deg(u))$ | Fast dynamic updates and neighbor iteration, but high per-object memory overhead in Python (`dict` hash table + `V` separate `list` headers/pointer arrays + `int` objects). |
| **Sparse CSR Matrix** | `scipy.sparse.csr_matrix` (`data`, `indices`, `indptr`) | $O(V + E)$ | $O(\log(\deg(u)))$ (binary search on sorted row) | Stores nonzeros in 3 contiguous typed NumPy arrays (`uint8` `data` + `int32` `indices`/`indptr`). Minimal memory footprint and cache-friendly SpMV for algorithms like PageRank. |
| **Dense Adjacency Matrix** | `numpy.ndarray` (`dtype=np.uint8`, shape $V \times V$) | $O(V^2)$ | $O(1)$ | Constant-time edge existence check via `A[u, v]`, but quadratic space regardless of edge sparsity. |

### Why CSR Beats Both Adjacency List and Dense Matrix on Sparse Social Graphs
- Social graphs are **sparse**: SNAP ego-Facebook has $V = 4{,}039$, $E = 88{,}234$, giving edge density $\frac{2E}{V(V-1)} \approx 0.0108$ (~98.9% zeros).
- On a 500-node sampled hub subgraph ($E = 5{,}782$), observed memory footprints are:
  - **Sparse CSR Matrix (`uint8`)**: `105.55 KB`
  - **Dense Adjacency Matrix (`uint8`)**: `244.14 KB`
  - **Python Adjacency List (`dict[int, list[int]]`)**: `307.34 KB`
- At full scale ($V = 4{,}039$), a `uint8` Dense Matrix allocates $4039^2 \approx 16.3\text{ MB}$ (`15,931 KB`), whereas CSR stores only the $2E = 176{,}468$ nonzeros plus `indptr` in under `1 MB`.

---

## 2. Brandes' Betweenness Centrality: Exact $O(VE)$ vs. $k$-Pivot $O(kE)$

Betweenness centrality measures how often node $v$ lies on shortest paths between all node pairs $(s, t)$:

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

- **Exact Brandes' Algorithm — $O(VE)$ unweighted / $O(VE + V^2 \log V)$ weighted**:
  - Instead of storing all-pairs paths ($O(V^3)$ naive or $O(V^2)$ memory), Brandes executes a BFS (unweighted) from every source $s \in V$, counting shortest paths $\sigma_{sv}$, and accumulates pairwise dependencies in a reverse-distance stack sweep using $O(V + E)$ auxiliary space.
  - Still expensive on large graphs because it performs $V$ full graph traversals.
- **$k$-Pivot Approximation — $O(k(V + E))$ (written $O(kE)$ for connected graphs)**:
  - Implemented via `nx.betweenness_centrality(G, k=min(k_pivots, len(G)), seed=42)`.
  - Samples $k \ll V$ pivot source vertices instead of all $V$ sources and rescales estimates, cutting runtime by a factor of $\approx V / k$ while preserving high-betweenness structural bridges.
  - On 4,039 nodes with $k=50$, Brandes runs in `~1.57 s` vs. ~80× longer for exact $k=4039$.

---

## 3. Social Graph Properties & Algorithms

### Heavy-Tailed / Power-Law Degree Distribution
- Real social networks exhibit strongly right-skewed degree distributions: most users have modest neighborhoods while a small set of hubs (celebrities/connectors) accumulate disproportionately high degree.
- In SNAP ego-Facebook ($V=4{,}039, E=88{,}234$), average degree is `43.69`, yet hubs reach over `1,000` connections while peripheral nodes have degree `1`–`5`.
- Because `sample_connected_subgraph` starts BFS from the highest-degree hub, small subgraphs retain dense hub-centric ego structure, whereas shortest paths across the graph traverse hubs in very few hops (approximate diameter `8` across 4,039 nodes — the small-world property).

### Clustering Coefficient & Triadic Closure
- **Triadic closure**: Friends of a common user are highly likely to connect directly, forming triangles.
- **Local clustering coefficient** of node $u$: $C(u) = \frac{2 T(u)}{\deg(u)(\deg(u) - 1)}$, where $T(u)$ is the number of triangles containing $u$.
- SNAP ego-Facebook exhibits strong clustering (`avg_clustering ≈ 0.6055`, `1,612,010` total triangles across the full graph) — orders of magnitude higher than an Erdős–Rényi random graph of matching density ($\approx 0.0108$).

### Louvain Modularity Optimization
- **Modularity ($Q$)** quantifies how densely connected nodes are within communities relative to a degree-preserving random null model:

$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

  where $m = |E|$, $k_i = \deg(i)$, and $\delta(c_i, c_j) = 1$ iff nodes $i, j$ share a community.
- **Louvain Algorithm** (`nx.community.louvain_communities(G, seed=42)`) runs two alternating phases per hierarchy pass:
  1. **Local moving**: Greedily reassign each node to the neighbor community maximizing $\Delta Q$.
  2. **Aggregation**: Collapse each community into a super-node with weighted self/inter-community edges and repeat until $Q$ converges.
- Runs near-linearly ($O(E)$ empirically per pass) and achieves `Q ≈ 0.8349` across `16` communities on full ego-Facebook.

---

## 4. Profiling Notes (`time.perf_counter()` & `tracemalloc`)
- **Latency (`time_ms`)**: Measured via monotonic high-resolution `time.perf_counter()` in milliseconds (`round(..., 2)`), with `scipy.sparse` preloaded to avoid one-time lazy-import spikes skewing the first PageRank benchmark point.
- **Memory (`peak_kb`)**: Measured via Python's `tracemalloc.get_traced_memory()` peak allocation in KB (`round(peak_bytes / 1024.0, 2)`) in a dedicated trace pass so tracing hooks do not distort wall-clock `time_ms`.

