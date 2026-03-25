"""CSC111 Winter 2026 - Project 2: Clustock

Plotly-based interactive visualization of the correlation graph.
"""

from __future__ import annotations
from correlation_graph import CorrelationGraph
import plotly.graph_objects as go
import networkx as nx


SECTOR_COLORS = {
    'Consumer Cyclical': '#FF7A45',
    'Utilities': '#FFC247',
    'Communication Services': '#FFF23A',
    'Consumer Defensive': '#B6FF2E',
    'Healthcare': '#43F06F',
    'Financial Services': '#4BE7D2',
    'Technology': '#52AEFF',
    'Real Estate': '#5A49F2',
    'Industrials': '#9A45F4',
    'Energy': '#F23CD7',
    'Basic Materials': '#FF4A4A'
}

SECTOR_ORDER = [
    'Consumer Cyclical',
    'Utilities',
    'Communication Services',
    'Consumer Defensive',
    'Healthcare',
    'Financial Services',
    'Technology',
    'Real Estate',
    'Industrials',
    'Energy',
    'Basic Materials'
]


def graph_to_networkx(cg: CorrelationGraph) -> nx.Graph:
    """Convert CorrelationGraph to NetworkX for layout algorithms."""
    # Our project graph stores the stock network in a custom structure.
    # We convert it to NetworkX here because spring_layout is already implemented there.
    G = nx.Graph()
    # First add every stock as a node. We keep the sector as node data so we can
    # color nodes by sector later without having to re-query the original graph.
    for ticker in cg.get_all_tickers():
        G.add_node(ticker, sector=cg.get_sector(ticker))
    # Then add undirected weighted edges. The custom graph stores each undirected
    # edge twice (A->B and B->A), so ticker < neighbour ensures we only add it once.
    for ticker in cg.get_all_tickers():
        for neighbour, weight in cg.get_neighbours(ticker).items():
            if ticker < neighbour:
                G.add_edge(ticker, neighbour, weight=weight)
    return G


def get_positions(cg: CorrelationGraph) -> dict[str, tuple[float, float]]:
    """Return node positions for a graph using the default spring layout."""
    graph = graph_to_networkx(cg)
    # The seed makes the layout deterministic: the same graph gets the same picture each run.
    # Spring layout treats edges like springs: connected nodes pull together and all
    # nodes push apart. That gives us a cluster-like network picture automatically.
    return nx.spring_layout(graph, seed=42)


def build_edge_traces(graph: nx.Graph,
                      positions: dict[str, tuple[float, float]]) -> list[go.Scatter]:
    """Return Plotly traces for all edges.

    We keep a fixed trace count across slider frames:
    - one trace for positive edges
    - one trace for negative edges
    This prevents old traces from lingering when switching thresholds.
    """
    positive_x = []
    positive_y = []
    negative_x = []
    negative_y = []
    positive_hover = []
    negative_hover = []

    # Plotly frames work best when each frame has the same trace structure.
    # So instead of creating one edge trace per edge, all positive edges are grouped
    # together and all negative edges are grouped together.
    for ticker_a, ticker_b, edge_data in graph.edges(data=True):
        # positions[ticker] gives the x,y location of this node in the layout.
        x0, y0 = positions[ticker_a]
        x1, y1 = positions[ticker_b]
        weight = edge_data['weight']
        # Hover text shows the exact pair and their correlation weight.
        hover_label = f'{ticker_a} - {ticker_b}<br>Correlation: {weight:.3f}'

        if weight >= 0:
            # Plotly draws one long line through every x,y pair in order.
            # Inserting None means stops the segment there, so many
            # separate edges can be packed into one trace.
            positive_x.extend([x0, x1, None])
            positive_y.extend([y0, y1, None])
            positive_hover.extend([hover_label, hover_label, None])
        else:
            negative_x.extend([x0, x1, None])
            negative_y.extend([y0, y1, None])
            negative_hover.extend([hover_label, hover_label, None])

    # One green trace for all positive-correlation edges.
    positive_trace = go.Scatter(
        x=positive_x,
        y=positive_y,
        line=dict(width=1.5, color='rgba(34, 139, 34, 0.45)'),
        hoverinfo='text',
        text=positive_hover,
        mode='lines',
        name='Positive Correlation',
        showlegend=True
    )
    # One red trace for all negative-correlation edges.
    negative_trace = go.Scatter(
        x=negative_x,
        y=negative_y,
        line=dict(width=1.5, color='rgba(220, 20, 60, 0.45)'),
        hoverinfo='text',
        text=negative_hover,
        mode='lines',
        name='Negative Correlation',
        showlegend=True
    )
    return [positive_trace, negative_trace]


def build_node_traces(cg: CorrelationGraph,
                      positions: dict[str, tuple[float, float]],
                      color_by_sector: bool) -> list[go.Scatter]:
    """Return the Plotly node traces.

    When coloring by sector, each sector gets its own trace so legend toggles
    actually hide/show the corresponding nodes.
    """
    tickers = cg.get_all_tickers()
    # Build one list of sectors and one of node degrees so each ticker
    # has matching data at the same index.
    sectors = [cg.get_sector(ticker) for ticker in tickers]
    degrees = [len(cg.get_neighbours(ticker)) for ticker in tickers]
    sector_to_color = sector_to_color_map(sectors)

    if not color_by_sector:
        # Simpler fallback mode: all stocks in one trace, all the same color.
        return [go.Scatter(
            # x and y positions must be in the same ticker order as text/hover data
            # so each label and hover card matches the right plotted point.
            x=[positions[ticker][0] for ticker in tickers],
            y=[positions[ticker][1] for ticker in tickers],
            mode='markers+text',
            text=tickers,
            textposition='top center',
            hovertext=[
                f'{ticker}<br>Sector: {sector}<br>Neighbours: {degree}'
                for ticker, sector, degree in zip(tickers, sectors, degrees)
            ],
            hoverinfo='text',
            marker=dict(
                # Higher-degree stocks get larger nodes so hubs stand out visually.
                size=[10 + min(degree * 1.2, 18) for degree in degrees],
                color='#1f77b4',
                line=dict(width=1, color='white')
            ),
            name='Stocks',
            showlegend=True
        )]

    sector_to_points: dict[str, list[tuple[str, int]]] = {}
    # Group stocks by sector so we can create one trace per sector.
    for ticker, sector, degree in zip(tickers, sectors, degrees):
        if sector not in sector_to_points:
            sector_to_points[sector] = []
        sector_to_points[sector].append((ticker, degree))

    node_traces = []
    # One node trace per sector means the Plotly legend can toggle sectors on and off.
    for sector in ordered_sectors(sectors):
        points = sector_to_points[sector]
        sector_tickers = [ticker for ticker, _ in points]
        sector_degrees = [degree for _, degree in points]
        # Each trace contains only the stocks from one sector, but they still use
        # the shared network layout so the overall structure stays consistent.
        node_traces.append(go.Scatter(
            x=[positions[ticker][0] for ticker in sector_tickers],
            y=[positions[ticker][1] for ticker in sector_tickers],
            mode='markers+text',
            text=sector_tickers,
            textposition='top center',
            hovertext=[
                f'{ticker}<br>Sector: {sector}<br>Neighbours: {degree}'
                for ticker, degree in points
            ],
            hoverinfo='text',
            marker=dict(
                size=[10 + min(degree * 1.2, 18) for degree in sector_degrees],
                color=sector_to_color[sector],
                line=dict(width=1, color='white')
            ),
            name=sector,
            showlegend=True
        ))
    return node_traces


def traces_for_graph(cg: CorrelationGraph,
                     positions: dict[str, tuple[float, float]],
                     color_by_sector: bool) -> list[go.Scatter]:
    """Return all traces needed to draw one graph."""
    # The figure is built from:
    # 1. edge traces (positive and negative)
    # 2. node traces (one per sector, or one total trace in fallback mode)
    graph = graph_to_networkx(cg)
    return [*build_edge_traces(graph, positions), *build_node_traces(cg, positions, color_by_sector)]


def sector_to_color_map(sectors: list[str]) -> dict[str, str]:
    """Return a stable mapping from sector name to display color."""
    # dict.fromkeys preserves first appearance order while removing duplicates.
    # We use that so the mapping stays stable for a given sector list.
    unique_sectors = list(dict.fromkeys(sectors))
    if not unique_sectors:
        return {}
    fallback_colors = [
        '#FF7A45', '#FFC247', '#FFF23A', '#B6FF2E', '#43F06F',
        '#4BE7D2', '#52AEFF', '#5A49F2', '#9A45F4', '#F23CD7', '#FF4A4A'
    ]
    color_map = {}
    fallback_index = 0
    for sector in unique_sectors:
        # If the sector is one of the known categories, use the exact chosen colour.
        if sector in SECTOR_COLORS:
            color_map[sector] = SECTOR_COLORS[sector]
        else:
            # Fallback only matters if Yahoo returns an unexpected sector label.
            color_map[sector] = fallback_colors[fallback_index % len(fallback_colors)]
            fallback_index += 1
    return color_map


def ordered_sectors(sectors: list[str]) -> list[str]:
    """Return sectors in the preferred display order."""
    present = set(sectors)
    # Keep the sectors that appear in our preferred legend order first.
    ordered = [sector for sector in SECTOR_ORDER if sector in present]
    # Any extra sector names not in SECTOR_ORDER are appended alphabetically.
    remaining = sorted(sector for sector in present if sector not in SECTOR_ORDER)
    return [*ordered, *remaining]


def create_interactive_graph(
    graphs_by_threshold: dict[float, CorrelationGraph],
    color_by_sector: bool = True,
    title: str = 'Stock Correlation Network by Threshold'
) -> go.Figure:
    """Create interactive Plotly figure with hover info, color coding, a threshold slider, and a color key."""

    # Sort thresholds so the slider always runs from smallest to biggest
    thresholds = sorted(graphs_by_threshold)
    reference_graph = graphs_by_threshold[thresholds[0]]
    # Keep one shared layout between thresholds so this is comparing
    # same stocks, and different edge cutoffs to keep node in same position
    positions = get_positions(reference_graph)

    frames = []
    for threshold in thresholds:
        graph = graphs_by_threshold[threshold]
        # Each frame reuses the same positions but swaps in a different edge set
        # and different node sizes for that threshold.
        frames.append(go.Frame(
            name=f'{threshold:.1f}',
            data=traces_for_graph(graph, positions, color_by_sector),
            layout=go.Layout(title=f'{title} (threshold = {threshold:.1f})')
        ))

    # Initial figure is the first threshold frame. The slider then switches between
    # the other precomputed frames with zero-duration transitions.
    fig = go.Figure(
        data=frames[0].data,
        layout=go.Layout(
            title=f'{title} (threshold = {thresholds[0]:.1f})',
            showlegend=True,
            hovermode='closest',
            # Extra bottom margin leaves room for the slider.
            margin=dict(b=80, l=20, r=20, t=40),
            # Move the legend to the right so it behaves like a colour key.
            legend=dict(x=1.02, y=1, xanchor='left', yanchor='top'),
            # Hide axis lines/ticks because this is a network diagram, not an x-y chart.
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            # The slider swaps between precomputed frames 0.1 ... 0.9.
            sliders=[{
                'active': 0,
                'currentvalue': {'prefix': 'Threshold: '},
                'pad': {'t': 20},
                'steps': [{
                    'label': f'{threshold:.1f}',
                    'method': 'animate',
                    'args': [[f'{threshold:.1f}'],
                             {'frame': {'duration': 0, 'redraw': True},
                              'mode': 'immediate',
                              'transition': {'duration': 0}}]
                } for threshold in thresholds]
            }]
        ),
        frames=frames
    )
    return fig


def run_visualization(graphs_by_threshold: dict[float, CorrelationGraph]) -> None:
    """Open a threshold-slider visualization."""
    fig = create_interactive_graph(graphs_by_threshold)
    fig.show()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
