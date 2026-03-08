"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Plotly-based interactive visualization of the correlation graph.
"""

from __future__ import annotations
from correlation_graph import CorrelationGraph
import plotly.graph_objects as go
import networkx as nx


def graph_to_networkx(cg: CorrelationGraph) -> nx.Graph:
    """Convert CorrelationGraph to NetworkX for layout algorithms."""
    raise NotImplementedError("TODO: implement")


def create_interactive_graph(
    cg: CorrelationGraph,
    color_by_sector: bool = True,
    title: str = 'Stock Correlation Network'
) -> go.Figure:
    """Create interactive Plotly figure with hover info and color coding."""
    raise NotImplementedError("TODO: implement")


def run_visualization(cg: CorrelationGraph) -> None:
    """Display the graph in browser."""
    raise NotImplementedError("TODO: implement")


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['plotly', 'networkx', 'correlation_graph'],
    })
