# SDS Project: Large-Scale Social Network Analyzer

## Architecture Rules
- Strict Separation of Concerns: `src/` MUST NOT import `streamlit`.
- All node IDs MUST be parsed as `int`.
- Add `__init__.py` to all package folders.

## Directory Tree
social-network-analyzer/
├── data/raw/
├── src/
│   ├── data_structures/ (graph_loader.py, representations.py)
│   ├── algorithms/ (traversal.py, centrality.py, communities.py)
│   └── profiler/ (benchmark.py)
├── ui/ (tabs.py, visualizers.py)
├── app.py
├── verify_pipeline.py
└── requirements.txt


## requirements.txt
networkx>=3.2
streamlit>=1.32
scipy>=1.12
numpy>=1.26
pandas>=2.2
plotly>=5.19
pyvis>=0.3.2
psutil>=5.9
requests>=2.31


## Shared Contracts
- Graph object: Undirected `nx.Graph` with `int` nodes.
- Timing metric: `time.perf_counter()` in milliseconds (`float`, rounded to 2 decimals).
- Memory metric: `tracemalloc` or `sys.getsizeof` in KB (`float`, rounded to 2 decimals).