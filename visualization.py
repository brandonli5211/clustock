"""CSC111 Winter 2026 - Project 2: Clustock

Plotly-based interactive visualization of the correlation graph.

WHAT THE GRAPH VISUALIZES
-------------------------
This graph is a stock correlation network. Each node is a stock (S&P 100 ticker).
An edge between two stocks means their log returns over the chosen period have a
Pearson correlation |r| > threshold (default 0.7).
  - Connected stocks tend to move together (r > 0) or oppositely (r < 0) in price.
  - Unconnected stocks have weaker or no significant price-movement relationship.
"""

from __future__ import annotations
from correlation_graph import CorrelationGraph
import plotly.graph_objects as go
import networkx as nx


def graph_to_networkx(cg: CorrelationGraph) -> nx.Graph:
    """Convert CorrelationGraph to NetworkX for layout algorithms."""
    G = nx.Graph()
    for ticker in cg.get_all_tickers():
        G.add_node(ticker, sector=cg.get_sector(ticker))
    for ticker in cg.get_all_tickers():
        for neighbour, weight in cg.get_neighbours(ticker).items():
            if ticker < neighbour:  # Add each edge once (undirected)
                G.add_edge(ticker, neighbour, weight=weight)
    return G


def create_interactive_graph(
    cg: CorrelationGraph,
    color_by_sector: bool = True,
    title: str = 'Stock Correlation Network'
) -> go.Figure:
    """Create interactive Plotly figure with hover info and color coding."""
    # Convert CorrelationGraph to NetworkX (needed for layout algorithms)
    G = graph_to_networkx(cg)
    # Spring layout: connected nodes pull together, all nodes push apart. Result:
    # correlated stocks (many edges) cluster in the center; isolated ones sit on the outside.
    # Deterministic = same input always gives same output. No randomness. The seed fixes
    # the algorithm's internal randomness so that for the same graph, we get the same layout.
    pos = nx.spring_layout(G, seed=42)

    # Build edge trace. Plotly draws one continuous line through all (x,y) points
    # in order. To draw *separate* lines (one per edge), we insert None between
    # segments: None means don't connect the previous point to
    # the next one (it's like we're drawing a continuous line, None means lift the pen).
    # So [Ax,Ay, Bx,By, None, Cx,Cy, Dx,Dy, None, ...] gives line
    # A->B, then line C->D, etc., with no line from B to C.
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for ticker_a, ticker_b in G.edges():
        x0, y0 = pos[ticker_a]
        x1, y1 = pos[ticker_b]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Build node trace. Plotly draws each node as a point at (x, y) with optional
    # label and hover text. We collect x and y from the layout for each ticker,
    # in the same order as get_all_tickers() so everything lines up.
    node_x = [pos[ticker][0] for ticker in cg.get_all_tickers()]
    node_y = [pos[ticker][1] for ticker in cg.get_all_tickers()]

    sectors = [cg.get_sector(ticker) for ticker in cg.get_all_tickers()]
    # zip(tickers, sectors) pairs them: (ticker_0, sector_0), (ticker_1, sector_1), ...
    # so we can build one hover string per node. Without zip we'd have two separate
    # lists and no clean way to say "this string goes with this node."
    hover_text = [
        f'{ticker}<br>Sector: {sector}<br>Neighbours: {len(cg.get_neighbours(ticker))}'
        for ticker, sector in zip(cg.get_all_tickers(), sectors)
    ]

    # color_by_sector: When True, nodes are colored by GICS sector so we can see if
    # correlated stocks cluster by industry. When False, all nodes use one colour;
    # useful for a simpler view or when we might color by something else
    # (e.g., degree, BFS depth from a crash node). For stock-sector analysis, use True.
    if color_by_sector:
        unique_sectors = list(dict.fromkeys(sectors))
        # enumerate gives (0, sector_0), (1, sector_1), ... so each sector gets a
        # unique number. Plotly needs numeric colour values; we map sector -> 0,1,2,...
        sector_to_idx = {sector: i for i, sector in enumerate(unique_sectors)}
        colors = [sector_to_idx[sector] for sector in sectors]
        # Viridis: a perceptually uniform colour scale (dark→light, purple→green→yellow).
        # Each sector gets a unique colour from the scale. Perceptually uniform means
        # equal numeric steps look like equal visual steps, which helps distinguish categories.
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[ticker for ticker in cg.get_all_tickers()],
            textposition='top center',
            hovertext=hover_text,
            hoverinfo='text',
            marker=dict(
                size=12,
                color=colors,
                colorscale='Viridis',
                line=dict(width=1, color='white')
            )
        )
    else:
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[ticker for ticker in cg.get_all_tickers()],
            textposition='top center',
            hovertext=hover_text,
            hoverinfo='text',
            marker=dict(
                size=12,
                color='#1f77b4',  # medium blue (when not coloring by sector)
                line=dict(width=1, color='white')
            )
        )

    # Combine the figure. Edges drawn first (underneath), then nodes on top.
    # Layout hides axes since we're drawing a graph and not a plot.
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title=title,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    ))
    return fig


def run_visualization(cg: CorrelationGraph) -> None:
    """Build the Plotly figure and open it in the default browser.
    Interactive: zoom, pan, and hover over nodes for ticker/sector info."""
    fig = create_interactive_graph(cg)
    fig.show()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['plotly', 'networkx', 'correlation_graph'],
    })
