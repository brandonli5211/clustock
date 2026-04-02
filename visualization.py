"""CSC111 Winter 2026 - Project 2: Clustock

Plotly-based interactive visualization of the correlation graph.
"""

from __future__ import annotations
import plotly.graph_objects as go
import networkx as nx
from correlation_graph import CorrelationGraph
from constants import NODE_SIZE_MODE, SECTORS
from config import CONFIG

SECTOR_PALETTE = [
    '#FF7A45',
    '#FFC247',
    '#FFF23A',
    '#B6FF2E',
    '#43F06F',
    '#4BE7D2',
    '#52AEFF',
    '#5A49F2',
    '#9A45F4',
    '#F23CD7',
    '#FF4A4A'
]

SECTOR_COLORS = {
    sector: SECTOR_PALETTE[index % len(SECTOR_PALETTE)]
    for index, sector in enumerate(SECTORS)
}


def graph_to_networkx(cg: CorrelationGraph) -> nx.Graph:
    """Convert CorrelationGraph to NetworkX for layout algorithms."""
    # Our project graph stores the stock network in a custom structure.
    # We convert it to NetworkX here because spring_layout is already implemented there.
    g = nx.Graph()
    # First add every stock as a node. We keep the sector as node data so we can
    # color nodes by sector later without having to re-query the original graph.
    for ticker in cg.get_all_tickers():
        g.add_node(ticker, sector=cg.get_sector(ticker))
    # Then add undirected weighted edges. The custom graph stores each undirected
    # edge twice (A->B and B->A), so ticker < neighbour ensures we only add it once.
    for ticker in cg.get_all_tickers():
        for neighbour, weight in cg.get_neighbours(ticker).items():
            if ticker < neighbour:
                g.add_edge(ticker, neighbour, weight=weight)
    return g


def get_positions(cg: CorrelationGraph) -> dict[str, tuple[float, float]]:
    """Return node positions for a graph using the default spring layout."""
    graph = graph_to_networkx(cg)
    # The seed makes the layout deterministic: the same graph gets the same picture each run.
    # Spring layout treats edges like springs: connected nodes pull together and all
    # nodes push apart. That gives us a cluster-like network picture automatically.
    return nx.spring_layout(graph, seed=42)


def graph_sectors(cg: CorrelationGraph) -> list[str]:
    """Return the sectors that actually appear in this graph in display order."""
    return ordered_sectors([cg.get_sector(stock) for stock in cg.get_all_tickers()])


def get_sector_oriented_positions(cg: CorrelationGraph) -> dict[str, tuple[float, float]]:
    """Return node positions for a graph with nodes of the same sector clustered together
    Taken from https://networkx.org/documentation/stable/auto_examples/drawing/plot_clusters.html
    """
    graph = graph_to_networkx(cg)
    sector_order = graph_sectors(cg)

    supergraph = nx.cycle_graph(len(sector_order))
    superpos = nx.spring_layout(supergraph, scale=2, seed=429)

    # Supernodes are used as centers for the new node clusters
    centers = list(superpos.values())
    pos = {}

    nodes_by_sector = {}
    for ticker in cg.get_all_tickers():
        sector = cg.get_sector(ticker)
        if sector not in nodes_by_sector:
            nodes_by_sector[sector] = []
        nodes_by_sector[sector].append(ticker)

    for center, sector in zip(centers, sector_order):
        pos.update(nx.spring_layout(nx.subgraph(graph, frozenset(nodes_by_sector[sector])), center=center, seed=1430))

    return pos


def get_community_positions(cg: CorrelationGraph) -> dict[str, tuple[float, float]]:
    """Return node positions for a graph with nodes of the same communities as calculated by greedy modularity
    Taken from https://networkx.org/documentation/stable/auto_examples/drawing/plot_clusters.html
    """
    graph = graph_to_networkx(cg)
    sector_count = max(1, len(graph_sectors(cg)))
    communities = nx.community.greedy_modularity_communities(graph, cutoff=sector_count, best_n=sector_count)

    # Compute positions for the node clusters as if they were themselves nodes in a
    # supergraph using a larger scale factor
    supergraph = nx.cycle_graph(len(communities))
    superpos = nx.spring_layout(supergraph, scale=2, seed=429)

    # Use the "supernode" positions as the center of each node cluster
    centers = list(superpos.values())
    pos = {}
    for center, comm in zip(centers, communities):
        pos.update(nx.spring_layout(nx.subgraph(graph, comm), center=center, seed=1430))

    # Nodes colored by cluster
    # for nodes, clr in zip(communities, ("tab:blue", "tab:orange", "tab:green")):
    #     nx.draw_networkx_nodes(G, pos=pos, nodelist=nodes, node_color=clr, node_size=100)
    # nx.draw_networkx_edges(G, pos=pos)

    return pos


def append_edge_data(bucket: dict[str, list], edge_points: tuple[float, float, float, float], hover_label: str) -> None:
    """Append one edge segment and its hover text to a trace bucket."""
    x0, y0, x1, y1 = edge_points
    bucket['x'].extend([x0, x1, None])
    bucket['y'].extend([y0, y1, None])
    bucket['hover'].extend([hover_label, hover_label, None])


def edge_trace(x_values: list, y_values: list, hover_text: list, color: str, name: str) -> go.Scatter:
    """Return a single Plotly edge trace."""
    return go.Scatter(
        x=x_values,
        y=y_values,
        line={'width': 1.5, 'color': color},
        hoverinfo='text',
        text=hover_text,
        mode='lines',
        name=name,
        showlegend=True
    )


def build_edge_traces(graph: nx.Graph,
                      positions: dict[str, tuple[float, float]]) -> list[go.Scatter]:
    """Return Plotly traces for all edges."""
    edge_buckets = {
        'positive': {'x': [], 'y': [], 'hover': []},
        'negative': {'x': [], 'y': [], 'hover': []}
    }

    for ticker_a, ticker_b, edge_data in graph.edges(data=True):
        x0, y0 = positions[ticker_a]
        x1, y1 = positions[ticker_b]
        hover_label = f'{ticker_a} - {ticker_b}<br>Correlation: {edge_data["weight"]:.3f}'
        key = 'positive' if edge_data['weight'] >= 0 else 'negative'
        append_edge_data(edge_buckets[key], (x0, y0, x1, y1), hover_label)

    return [
        edge_trace(
            edge_buckets['positive']['x'],
            edge_buckets['positive']['y'],
            edge_buckets['positive']['hover'],
            'rgba(34, 139, 34, 0.45)',
            'Positive Correlation'
        ),
        edge_trace(
            edge_buckets['negative']['x'],
            edge_buckets['negative']['y'],
            edge_buckets['negative']['hover'],
            'rgba(220, 20, 60, 0.45)',
            'Negative Correlation'
        )
    ]


def node_size_function(degrees: list[int], threshold: float | None) -> callable:
    """Return the node-size function for the current graph."""
    max_degree = max(degrees) if degrees else 1

    def _node_size(degree: int) -> float:
        if NODE_SIZE_MODE == 'linear':
            return 12 + (min(degree, 100) ** 1.3) / 6
        normalized = degree / max_degree if max_degree > 0 else 0
        threshold_scale = 36 if threshold is None else (38 - 18 * threshold)
        return 12 + threshold_scale * (normalized ** 2)

    return _node_size


def highlight_node_traces(cg: CorrelationGraph,
                          positions: dict[str, tuple[float, float]],
                          tickers: list[str],
                          node_size: callable,
                          highlight: tuple[str, set[str]]) -> list[go.Scatter]:
    """Return traces for highlight mode."""
    start_ticker, pivot_tickers = highlight
    other_tickers = [stock for stock in tickers if stock != start_ticker and stock not in pivot_tickers]
    pivot_list = [stock for stock in tickers if stock in pivot_tickers and stock != start_ticker]
    traces = [go.Scatter(
        x=[positions[stock][0] for stock in other_tickers],
        y=[positions[stock][1] for stock in other_tickers],
        mode='markers+text',
        text=other_tickers,
        textposition='top center',
        hovertext=[
            f'{stock}<br>Sector: {cg.get_sector(stock)}<br>Neighbours: {len(cg.get_neighbours(stock))}'
            for stock in other_tickers
        ],
        hoverinfo='text',
        marker={
            'size': [node_size(len(cg.get_neighbours(stock))) for stock in other_tickers],
            'color': 'rgba(140, 140, 140, 0.75)',
            'line': {'width': 1, 'color': 'white'}
        },
        name='Other Stocks' + '                 ',
        showlegend=True
    )]

    if pivot_list:
        traces.append(go.Scatter(
            x=[positions[stock][0] for stock in pivot_list],
            y=[positions[stock][1] for stock in pivot_list],
            mode='markers+text',
            text=pivot_list,
            textposition='top center',
            hovertext=[
                f'{stock}<br>Sector: {cg.get_sector(stock)}<br>Neighbours: {len(cg.get_neighbours(stock))}'
                for stock in pivot_list
            ],
            hoverinfo='text',
            marker={
                'size': [node_size(len(cg.get_neighbours(stock))) for stock in pivot_list],
                'color': '#AE67FF',
                'line': {'width': 1, 'color': 'white'}
            },
            name='Pivot Candidates',
            showlegend=True
        ))

    if start_ticker in positions:
        start_degree = len(cg.get_neighbours(start_ticker))
        traces.append(go.Scatter(
            x=[positions[start_ticker][0]],
            y=[positions[start_ticker][1]],
            mode='markers+text',
            text=[start_ticker],
            textposition='top center',
            hovertext=[
                f'{start_ticker}<br>Sector: {cg.get_sector(start_ticker)}<br>Neighbours: {start_degree}'
            ],
            hoverinfo='text',
            marker={
                'size': [node_size(start_degree)],
                'color': '#FFD95C',
                'line': {'width': 2, 'color': 'white'}
            },
            name='Start Ticker',
            showlegend=True
        ))

    return traces


def sector_node_traces(tickers: list[str],
                       node_info: list[tuple[str, int]],
                       positions: dict[str, tuple[float, float]],
                       node_size: callable,
                       sector_to_color: dict[str, str]) -> list[go.Scatter]:
    """Return one node trace per sector."""
    sector_to_points: dict[str, list[tuple[str, int]]] = {}
    sectors = [stock_sector for stock_sector, _ in node_info]
    for ticker, (sector, degree) in zip(tickers, node_info):
        if sector not in sector_to_points:
            sector_to_points[sector] = []
        sector_to_points[sector].append((ticker, degree))

    node_traces = []
    for sector in ordered_sectors(sectors):
        points = sector_to_points[sector]
        sector_tickers = [stock for stock, _ in points]
        node_traces.append(go.Scatter(
            x=[positions[stock][0] for stock in sector_tickers],
            y=[positions[stock][1] for stock in sector_tickers],
            mode='markers+text',
            text=sector_tickers,
            textposition='top center',
            hovertext=[
                f'{stock}<br>Sector: {sector}<br>Neighbours: {stock_degree}'
                for stock, stock_degree in points
            ],
            hoverinfo='text',
            marker={
                'size': [node_size(stock_degree) for _, stock_degree in points],
                'color': sector_to_color[sector],
                'line': {'width': 1, 'color': 'white'}
            },
            name=sector,
            showlegend=True
        ))
    return node_traces


def build_node_traces(cg: CorrelationGraph,
                      positions: dict[str, tuple[float, float]],
                      threshold: float | None = None,
                      highlight: tuple[str, set[str]] | None = None) -> list[go.Scatter]:
    """Return the Plotly node traces."""
    tickers = cg.get_all_tickers()
    sectors = [cg.get_sector(stock) for stock in tickers]
    degrees = [len(cg.get_neighbours(stock)) for stock in tickers]
    node_size = node_size_function(degrees, threshold)
    if highlight is not None:
        return highlight_node_traces(cg, positions, tickers, node_size, highlight)
    node_info = list(zip(sectors, degrees))
    return sector_node_traces(tickers, node_info, positions, node_size, sector_to_color_map(sectors))


def traces_for_graph(cg: CorrelationGraph,
                     positions: dict[str, tuple[float, float]],
                     threshold: float | None = None,
                     highlight: tuple[str, set[str]] | None = None) -> list[go.Scatter]:
    """Return all traces needed to draw one graph."""
    graph = graph_to_networkx(cg)
    return build_edge_traces(graph, positions) + build_node_traces(cg, positions, threshold, highlight)


def sector_to_color_map(sectors: list[str]) -> dict[str, str]:
    """Return a stable mapping from sector name to display color."""
    # dict.fromkeys preserves first appearance order while removing duplicates.
    # We use that so the mapping stays stable for a given sector list.
    unique_sectors = ordered_sectors(sectors)
    if not unique_sectors:
        return {}
    color_map = {}
    for index, sector in enumerate(unique_sectors):
        if sector in SECTOR_COLORS:
            color_map[sector] = SECTOR_COLORS[sector]
        else:
            color_map[sector] = SECTOR_PALETTE[index % len(SECTOR_PALETTE)]
    return color_map


def ordered_sectors(sectors: list[str]) -> list[str]:
    """Return sectors in the preferred display order."""
    present = set(sectors)
    # Keep the sectors that appear in our shared constants order first.
    ordered = [sector for sector in SECTORS if sector in present]
    # Any extra sector names not in constants are appended alphabetically.
    remaining = sorted(sector for sector in present if sector not in SECTORS)
    return ordered + remaining


def top_neighbour_stocks(cg: CorrelationGraph, limit: int = 5) -> list[tuple[str, int]]:
    """Return the top stocks by neighbour count, excluding zero-neighbour stocks."""
    counts = []
    for ticker in cg.get_all_tickers():
        neighbour_count = len(cg.get_neighbours(ticker))
        if neighbour_count > 0:
            counts.append((ticker, neighbour_count))
    counts.sort(key=lambda pair: (-pair[1], pair[0]))
    return counts[:limit]


def side_panel_annotation(cg: CorrelationGraph) -> dict:
    """Return a Plotly annotation listing the top neighbour stocks for this graph."""
    top_stocks = top_neighbour_stocks(cg)
    sector_colors = sector_to_color_map([cg.get_sector(stock) for stock in cg.get_all_tickers()])
    if top_stocks:
        lines = ['Most connections:']
        for index, (ticker, count) in enumerate(top_stocks, start=1):
            sector = cg.get_sector(ticker)
            color = sector_colors.get(sector, '#333333')
            lines.append(f'{index}. {ticker} ({count}) <span style="color:{color}">&#9679;</span>')
    else:
        lines = ['Most connections:', 'No connected stocks']

    return {
        'x': 0,
        'y': 0.1,
        'xref': 'paper',
        'yref': 'paper',
        'xanchor': 'left',
        'yanchor': 'top',
        'align': 'left',
        'showarrow': False,
        'bordercolor': '#C9D4E6',
        'borderwidth': 1,
        'borderpad': 8,
        'bgcolor': 'rgba(255, 255, 255, 0.78)',
        'text': '<br>'.join(lines)
    }


def create_interactive_graph(
        graphs_by_threshold: dict[float, CorrelationGraph],
        title: str = 'Stock Correlation Network by Threshold',
        start_threshold: int = 0,
        show_side_annotation: bool = True,
        group_by_sector: bool = False
) -> go.Figure:
    """Create interactive Plotly figure with hover info, color coding, a threshold slider, and a color key."""

    # Sort thresholds so the slider always runs from smallest to biggest
    thresholds = sorted(graphs_by_threshold)
    reference_graph = graphs_by_threshold[thresholds[0]]
    # Keep one shared layout between thresholds so this is comparing
    # same stocks, and different edge cutoffs to keep node in same position

    if group_by_sector:
        positions = get_sector_oriented_positions(reference_graph)
    else:
        positions = get_positions(reference_graph)

    frames = []
    for threshold in thresholds:
        graph = graphs_by_threshold[threshold]
        # Each frame reuses the same positions but swaps in a different edge set
        # and different node sizes for that threshold.
        frames.append(go.Frame(
            name=f'{threshold:.1f}',
            data=traces_for_graph(graph, positions, threshold),
            layout=go.Layout(
                title=f'{title} (threshold = {threshold:.1f})',
                annotations=[side_panel_annotation(graph)] if show_side_annotation else []
            )
        ))

    # Initial figure is the first threshold frame. The slider then switches between
    # the other precomputed frames with zero-duration transitions.
    fig = go.Figure(
        data=frames[start_threshold].data,
        layout=go.Layout(
            title=f'{title} (threshold = {thresholds[0]:.1f})',
            showlegend=True,
            hovermode='closest',
            margin={'b': 80, 'l': 20, 'r': 180, 't': 40},
            # Move the legend to the right so it behaves like a colour key.
            legend={'x': 1.02, 'y': 1, 'xanchor': 'left', 'yanchor': 'top'},
            annotations=[side_panel_annotation(reference_graph)] if show_side_annotation else [],
            # Hide axis lines/ticks because this is a network diagram, not an x-y chart.
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
        ),
        frames=frames
    )
    return fig


def get_figure_layout(title: str, annotation: dict | None) -> go.Layout:
    """Return the shared Plotly layout for a graph figure."""
    return go.Layout(
        title=title,
        autosize=True,
        showlegend=True,
        hovermode='closest',
        margin={'b': 80, 'l': 20, 'r': 180, 't': 40},
        legend={'x': 1.02, 'y': 1, 'xanchor': 'left', 'yanchor': 'top'},
        annotations=[annotation] if annotation is not None else [],
        xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
        yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}
    )


def create_graph_figure(
        graph: CorrelationGraph,
        positions: dict[str, tuple[float, float]],
        threshold: float,
        highlight: tuple[str, set[str]] | None = None,
        show_side_annotation: bool = True
) -> go.Figure:
    """Create a single-threshold figure.

    This is useful for Dash callbacks where we want one threshold at a time,
    instead of rebuilding the whole slider figure on every update.
    """
    annotation = side_panel_annotation(graph) if show_side_annotation else None
    fig = go.Figure(
        data=traces_for_graph(graph, positions, threshold, highlight),
        layout=get_figure_layout(f'Stock Correlation Network by Threshold (threshold = {threshold:.1f})', annotation)
    )
    return fig


def run_visualization(graphs_by_threshold: dict[float, CorrelationGraph]) -> None:
    """Open a threshold-slider visualization."""
    fig = create_interactive_graph(graphs_by_threshold)
    fig.show(config=CONFIG)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['correlation_graph', 'constants', 'plotly.graph_objects', 'networkx', 'config'],
        'allowed-io': [],
        'max-line-length': 120
    })
