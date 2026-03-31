"""CSC111 Winter 2026 - Project 2: Clustock

Entry point: download prices, build the correlation graph, open the interactive visualization.
"""

from __future__ import annotations

from compute import build_correlation_graphs_for_thresholds
from visualization import create_graph_figure, get_positions, top_neighbour_stocks, get_sector_oriented_positions, \
    get_community_positions
from constants import SP100_TICKERS
from config import CONFIG

from dash import Dash, html, dcc, callback, Output, Input, ALL, ctx, no_update


def edge_sign_counts(graph) -> tuple[int, int]:
    """return the number of positive and negative edges in the graph."""
    positive = 0
    negative = 0
    for ticker in graph.get_all_tickers():
        for neighbour, weight in graph.get_neighbours(ticker).items():
            if ticker < neighbour:
                if weight >= 0:
                    positive += 1
                else:
                    negative += 1
    return positive, negative


def most_connections_panel(graph) -> html.Div:
    """Return a Dash panel listing the most connected stocks in the current graph."""
    top_stocks = top_neighbour_stocks(graph)
    from visualization import sector_to_color_map
    sector_colors = sector_to_color_map([graph.get_sector(ticker) for ticker in graph.get_all_tickers()])
    if not top_stocks:
        return html.Div("No connected stocks")

    return html.Div([
        html.Div("Most connections:", style={'fontWeight': '600', 'marginBottom': '4px'}),
        html.Div([
            html.Div([
                html.Span(f'{index}. {ticker} ({count})'),
                html.Span(
                    ' ●',
                    style={'color': sector_colors.get(graph.get_sector(ticker), '#333333')}
                )
            ])
            for index, (ticker, count) in enumerate(top_stocks, start=1)
        ])
    ], style={
        'marginTop': '12px',
        'padding': '6px 8px',
        'border': '1px solid #C9D4E6',
        'backgroundColor': 'rgba(255, 255, 255, 0.88)'
    })


def run_full_pipeline(use_sample: bool = True) -> None:
    """Run the full pipeline: fetch data, build graph,launch Plotly visualization (with slider).

    If use_sample is True, only the first 15 S&P 100 tickers are used (faster). If False,
    all tickers in constants.SP100_TICKERS are used. Uses one month of daily bars by default.
    """
    tickers = set(SP100_TICKERS[:15]) if use_sample else set(SP100_TICKERS)
    print('Building correlation graph for', len(tickers), 'tickers...')
    thresholds = [x / 10 for x in range(1,11)]
    graphs_by_threshold = build_correlation_graphs_for_thresholds(tickers,thresholds, period='1mo', interval='1d')
    positions = get_positions(graphs_by_threshold[thresholds[0]])
    sector_oriented_positions = get_sector_oriented_positions(graphs_by_threshold[thresholds[0]])
    communinity_positions = get_community_positions(graphs_by_threshold[thresholds[0]])
    figures_by_threshold = {
        'Standard': {},
        'Sector': {},
        'Community': {}
    }

    for threshold in thresholds:
        graph = graphs_by_threshold[threshold]
        positive_edges, negative_edges = edge_sign_counts(graph)
        figures_by_threshold['Standard'][threshold] = create_graph_figure(
            graph,
            positions,
            threshold,
            show_side_annotation=False
        )
        figures_by_threshold['Sector'][threshold] = create_graph_figure(
            graph,
            sector_oriented_positions,
            threshold,
            show_side_annotation=False
        )
        figures_by_threshold['Community'][threshold] = create_graph_figure(
            graph,
            communinity_positions,
            threshold,
            show_side_annotation=False
        )
        print(
            f'Threshold {threshold} -> '
            f'density: {round(graph.density(), 3)}, '
            f'positive: {positive_edges}, '
            f'negative: {negative_edges}'
        )

    print('Opening interactive visualization...')

    # https://stackoverflow.com/questions/69570145/how-to-change-the-website-tab-name-in-dash-plotly-using-python
    app = Dash(__name__)
    app.title = "Clustock"

    default_threshold = 0.7
    visualization_figure = figures_by_threshold['Standard'][default_threshold]
    app.layout = html.Div([
        html.Div([
            dcc.Graph(
                id="graph",
                figure=visualization_figure,
                config=CONFIG,
                # https://community.plotly.com/t/dash-css-make-a-div-full-screen/50982/2
                style={
                    'width': '100%',
                    'height': '90vh'
                },
                # https://dash-resources.com/how-to-animate-dash-graphs/
                animation_options={
                    'frame': {
                        'redraw': True
                    },
                    'transition': {
                        'duration': 250,
                        'easing': 'cubic-in-out'
                    },
                    'mode': 'immediate'
                }
            ),
            html.Div([
                html.Div("View Options", style={'fontWeight': '600', 'marginBottom': '8px'}),
                dcc.RadioItems(
                    ['Standard', 'Sector', 'Community'],
                    'Standard',
                    id="view-menu"
                )
            ], style={
                'position': 'absolute',
                'top': '270px',
                'right': '30px',
                'width': '180px',
                'padding': '20px',
                'boxSizing': 'border-box',
                'backgroundColor': 'rgba(255, 255, 255, 0.88)',
                'border': '1px solid #C9D4E6',
                'fontFamily': '"Open Sans", verdana, arial, sans-serif',
                'fontSize': '12px',
                'color': '#2a3f5f'
            }),
            html.Div([
                html.Div("Pivot Candidates", style={'fontWeight': '600', 'marginBottom': '8px'}),
                dcc.Dropdown(
                    id="pivot_start_ticker",
                    options=[{'label': ticker, 'value': ticker} for ticker in sorted(SP100_TICKERS)],
                    placeholder="Search ticker...",
                    searchable=True,
                    clearable=True
                ),
                html.Div(
                    id="test-pivot-output",
                    style={
                        'marginTop': '8px',
                        'maxHeight': '220px',
                        'overflowY': 'auto'
                    }
                ),
                html.Div(
                    id="most-connections-output",
                    children=most_connections_panel(graphs_by_threshold[default_threshold])
                ),
            ], style={
                'position': 'absolute',
                'top': '400px',
                'right': '30px',
                'width': '180px',
                'padding': '20px',
                'boxSizing': 'border-box',
                'backgroundColor': 'rgba(255, 255, 255, 0.88)',
                'border': '1px solid #C9D4E6',
                'fontFamily': '"Open Sans", verdana, arial, sans-serif',
                'fontSize': '12px',
                'color': '#2a3f5f'
            })
        ], style={
            'position': 'relative',
            'width': '100%'
        }),
        dcc.Slider(
            min=0.1,
            max=1,
            step=0.1,
            value=0.7,
            id="threshold-slider",
            updatemode='drag',
            marks={
                x / 10: {
                    'label': f'{x / 10:.1f}',
                    'style': {
                        'fontFamily': '"Open Sans", verdana, arial, sans-serif',
                        'fontSize': '12px',
                        'color': '#2a3f5f'
                    }
                }
                for x in range(1, 11)
            }
        ),
    ])

    # Input Handling
    @callback(
        Output('graph', 'figure'),
        Output('most-connections-output', 'children'),
        Input('threshold-slider', 'value'),
        Input('pivot_start_ticker', 'value'),
        Input('view-menu', 'value'))
    def update_figure(selected_threshold, start_ticker, view_option):
        "Returns figure after handling the input"
        selected_threshold = round(selected_threshold, 1)
        graph = graphs_by_threshold[selected_threshold]

        if start_ticker in SP100_TICKERS:
            pivots = graph.get_pivot_candidates(start_ticker)
            pivot_tickers = {pivot[0] for pivot in pivots}

            if view_option == "Sector":
                fig = create_graph_figure(
                    graph,
                    sector_oriented_positions,
                    selected_threshold,
                    show_side_annotation=False,
                    start_ticker=start_ticker,
                    pivot_tickers=pivot_tickers
                )
            elif view_option == "Community":
                fig = create_graph_figure(
                    graph,
                    communinity_positions,
                    selected_threshold,
                    show_side_annotation=False,
                    start_ticker=start_ticker,
                    pivot_tickers=pivot_tickers
                )
            else:
                fig = create_graph_figure(
                    graph,
                    positions,
                    selected_threshold,
                    show_side_annotation=False,
                    start_ticker=start_ticker,
                    pivot_tickers=pivot_tickers
                )
        else:
            fig = figures_by_threshold[view_option][selected_threshold]

        return fig, most_connections_panel(graph)

    @callback(
        Output('test-pivot-output', 'children'),
        Input('threshold-slider', 'value'),
        Input("pivot_start_ticker", "value"))
    def update_pivots(selected_threshold, start_ticker):
        "Returns pivot candidates to current test div"
        selected_threshold = round(selected_threshold, 1)
        if start_ticker in SP100_TICKERS:
            pivots = graphs_by_threshold[selected_threshold].get_pivot_candidates(start_ticker)
            pivot_ticker_list = [pivot[0] for pivot in pivots]
            return html.Div([
                html.Button(
                    ticker,
                    id={'type': 'pivot-button', 'ticker': ticker},
                    n_clicks=0,
                    style={
                        'display': 'block',
                        'width': '100%',
                        'marginBottom': '6px',
                        'textAlign': 'left',
                        'cursor': 'pointer',
                        'fontFamily': 'inherit',
                        'fontSize': '12px',

                    }
                )
                for ticker in pivot_ticker_list
            ])
        else:
            return ""

    @callback(
        Output('pivot_start_ticker', 'value'),
        Input({'type': 'pivot-button', 'ticker': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def select_pivot_candidate(_clicks):
        "Sets the dropdown to the clicked pivot candidate ticker."
        triggered = ctx.triggered_id
        if triggered is None or not isinstance(triggered, dict):
            return no_update
        if not any(click_count for click_count in _clicks):
            return no_update
        return triggered['ticker']

    app.run(debug=True)

if __name__ == '__main__':
    # use_sample=False for full S&P 100 (~100 tickers); True for 15 tickers (faster).
    run_full_pipeline(use_sample=False)
