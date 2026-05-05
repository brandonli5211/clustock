"""CSC111 Winter 2026 - Project 2: Clustock

Entry point: download prices, build the correlation graph, open the interactive visualization.
"""
from __future__ import annotations

from dash import Dash, html, dcc, Output, Input, ALL, ctx, no_update

from compute import build_correlation_graphs
from visualization import SECTOR_COLORS, create_graph_figure, get_positions, sector_to_color_map, \
    top_neighbour_stocks, get_sector_oriented_positions, \
    get_community_positions
from correlation_graph import CorrelationGraph
from constants import SP100_TICKERS
from config import CONFIG

def edge_sign_counts(graph: CorrelationGraph) -> tuple[int, int]:
    """return the number of positive and negative edges in the graph."""
    positive = 0
    negative = 0
    for ticker in graph.get_all_tickers():
        for neighbour, weight in graph.get_neighbours(ticker).items():
            if ticker < neighbour:
                positive += int(weight >= 0)
                negative += int(weight < 0)
    return positive, negative


def most_connections_panel(graph: CorrelationGraph) -> html.Div:
    """Return a Dash panel listing the most connected stocks in the current graph."""
    top_stocks = top_neighbour_stocks(graph)
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


def density_leaderboard_panel(graph: CorrelationGraph) -> html.Div:
    """Return panel containing the rankings for graph density between sectors"""
    densities = graph.get_ordered_sector_densities()
    return html.Div([
        html.Div("Densities:", style={'fontWeight': '600', 'marginBottom': '4px'}),
        html.Div([
            html.Div([
                html.Span(f'{index}. {sector} ({round(density, 5)})'),
                html.Span(
                    ' ●',
                    style={'color': SECTOR_COLORS[sector]}
                )
            ])
            for index, (sector, density) in enumerate(densities, start=1)
        ])
    ], style={
        'marginTop': '12px',
        'padding': '6px 8px',
        'border': '1px solid #C9D4E6',
        'backgroundColor': 'rgba(255, 255, 255, 0.88)'
    })


def avg_abs_pearson_panel(graph: CorrelationGraph) -> html.Div:
    """Return panel containing the rankings for average pearson corrleations between sectors

        Prerequisites:
            - graph is a complete graph
    """
    avg_abs_coeffs = graph.ordered_sector_abs_pearsons()
    return html.Div([
        html.Div("Average Absolute Value of Pearson Correlation Coefficients",
                 style={'fontWeight': '600', 'marginBottom': '4px'}),
        html.Div([
            html.Div([
                # https://stackoverflow.com/questions/394809/does-python-have-a-ternary-conditional-operator
                html.Span(
                    f'{index}. {sector} '
                    f'({round(avg_abs_coeff, 5) if avg_abs_coeff != -1 else "N/A <= 1 Stock in Sector"})'
                ),
                html.Span(
                    ' ●',
                    style={'color': SECTOR_COLORS[sector]}
                )
            ])
            for index, (sector, avg_abs_coeff) in enumerate(avg_abs_coeffs, start=1)
        ])
    ], style={
        'marginTop': '12px',
        'padding': '6px 8px',
        'border': '1px solid #C9D4E6',
        'backgroundColor': 'rgba(255, 255, 255, 0.88)'
    })


def build_figures_by_threshold(graphs_by_threshold: dict[float, CorrelationGraph],
                               position_views: dict[str, dict[str, tuple[float, float]]]
                               ) -> dict[str, dict[float, object]]:
    """Return precomputed figures grouped by threshold and view."""
    figures_by_threshold = {
        'Standard': {},
        'Sector': {},
        'Community': {}
    }

    for threshold, graph in graphs_by_threshold.items():
        figures_by_threshold['Standard'][threshold] = create_graph_figure(
            graph,
            position_views['Standard'],
            threshold,
            show_side_annotation=False
        )
        figures_by_threshold['Sector'][threshold] = create_graph_figure(
            graph,
            position_views['Sector'],
            threshold,
            show_side_annotation=False
        )
        figures_by_threshold['Community'][threshold] = create_graph_figure(
            graph,
            position_views['Community'],
            threshold,
            show_side_annotation=False
        )

    return figures_by_threshold


def build_graph_sets(tickers: set[str], thresholds: list[float]
                     ) -> tuple[dict[float, CorrelationGraph], CorrelationGraph]:
    """Build all threshold graphs once, plus the complete graph used by the summary panels."""
    all_thresholds = [0.0] + thresholds
    all_graphs = build_correlation_graphs(tickers, all_thresholds, period='1mo', interval='1d')
    graphs_by_threshold = {threshold: all_graphs[threshold] for threshold in thresholds}
    return graphs_by_threshold, all_graphs[0.0]


def register_callbacks(app: Dash,
                       graphs_by_threshold: dict[float, CorrelationGraph],
                       figures_by_threshold: dict[str, dict[float, object]],
                       position_views: dict[str, dict[str, tuple[float, float]]]) -> None:
    """Register all Dash callbacks for the app."""

    @app.callback(
        Output('graph', 'figure'),
        Output('most-connections-output', 'children'),
        Input('threshold-slider', 'value'),
        Input('pivot_start_ticker', 'value'),
        Input('view-menu', 'value'))
    def update_figure(selected_threshold: float, start_ticker: str | None, view_option: str) -> tuple[object, html.Div]:
        """Return the figure and most-connections panel after input changes."""
        selected_threshold = round(selected_threshold, 1)
        graph = graphs_by_threshold[selected_threshold]

        if start_ticker in SP100_TICKERS:
            pivots = graph.get_pivot_candidates(start_ticker)
            pivot_tickers = {pivot[0] for pivot in pivots}
            fig = create_graph_figure(
                graph,
                position_views[view_option],
                selected_threshold,
                highlight=(start_ticker, pivot_tickers),
                show_side_annotation=False
            )
        else:
            fig = figures_by_threshold[view_option][selected_threshold]

        # https://community.plotly.com/t/set-intial-mode-to-box-select/22073
        fig.update_layout(dragmode='pan')
        return fig, most_connections_panel(graph)

    @app.callback(
        Output('test-pivot-output', 'children'),
        Input('threshold-slider', 'value'),
        Input("pivot_start_ticker", "value"))
    def update_pivots(selected_threshold: float, start_ticker: str | None) -> html.Div | str:
        """Return pivot candidates for the selected start ticker."""
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
        return ""

    @app.callback(
        Output('density-leaderboard', 'children'),
        Input('threshold-slider', 'value'),
    )
    def update_density_leaderboard(selected_threshold: float) -> list[str | html.Div]:
        """Return the full-graph density and sector density leaderboard."""
        selected_threshold = round(selected_threshold, 1)
        return [
            f"Density of Full Graph: {round(graphs_by_threshold[selected_threshold].density(), 5)}",
            density_leaderboard_panel(graphs_by_threshold[selected_threshold])
        ]

    @app.callback(
        Output('pivot_start_ticker', 'value'),
        Input({'type': 'pivot-button', 'ticker': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def select_pivot_candidate(_clicks: list[int]) -> str | object:
        """Set the dropdown to the clicked pivot candidate ticker."""
        triggered = ctx.triggered_id
        if triggered is None or not isinstance(triggered, dict):
            return no_update
        if not any(click_count for click_count in _clicks):
            return no_update
        return triggered['ticker']


def run_full_pipeline(use_sample: bool = True) -> None:
    """Run the full pipeline: fetch data, build graph,launch Plotly visualization (with slider).

    If use_sample is True, only the first 15 S&P 100 tickers are used (faster). If False,
    all tickers in constants.SP100_TICKERS are used. Uses one month of daily bars by default.
    """
    tickers = set(SP100_TICKERS[:15]) if use_sample else set(SP100_TICKERS)
    print('Building correlation graph for', len(tickers), 'tickers...')
    thresholds = [x / 10 for x in range(1, 11)]
    graphs_by_threshold, complete_graph = build_graph_sets(tickers, thresholds)
    position_views = {
        'Standard': get_positions(graphs_by_threshold[thresholds[0]]),
        'Sector': get_sector_oriented_positions(graphs_by_threshold[thresholds[0]]),
        'Community': get_community_positions(graphs_by_threshold[thresholds[0]])
    }
    figures_by_threshold = build_figures_by_threshold(graphs_by_threshold, position_views)
    for threshold in thresholds:
        graph = graphs_by_threshold[threshold]
        positive_edges, negative_edges = edge_sign_counts(graph)
        print(
            f'Threshold {threshold} -> '
            f'density: {round(graph.density(), 3)}, '
            f'positive: {positive_edges}, '
            f'negative: {negative_edges}'
        )

    print('Opening interactive visualization...')

    # https://stackoverflow.com/questions/69570145/how-to-change-the-website-tab-name-in-dash-plotly-using-python

    default_threshold = 0.7
    visualization_figure = figures_by_threshold['Standard'][default_threshold]
    # https://community.plotly.com/t/set-intial-mode-to-box-select/22073
    visualization_figure.update_layout(dragmode='pan')
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
                    id="view-menu",
                    style={'marginBottom': '12px'}
                ),
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
                'bottom': '100px',
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
        html.Div([
            html.Div([
                html.Div("Densities of Sector Subgraphs", style={'fontWeight': '600', 'marginBottom': '4px'}),
                html.Div(
                    children=[
                        f"Density of Full Graph: {round(graphs_by_threshold[default_threshold].density(), 5)}",
                        density_leaderboard_panel(graphs_by_threshold[default_threshold])
                    ],
                    id='density-leaderboard'
                ),
            ], style={
                'marginTop': '20px',
                'padding': '20px',
                'boxSizing': 'border-box',
                'backgroundColor': 'rgba(255, 255, 255, 0.88)',
                'border': '1px solid #C9D4E6',
                'fontFamily': '"Open Sans", verdana, arial, sans-serif',
                'fontSize': '12px',
                'color': '#2a3f5f'
            }
            ),
            html.Div([
                html.Div("Average Absolute Value of Pearson Coefficients in Sector Subgraph",
                         style={'fontWeight': '600', 'marginBottom': '4px'}),
                html.Div(
                    children=[
                        f"Average Absolute Value of Pearson Coefficients in Full Graph: \
                        {round(complete_graph.get_average_abs_weight(), 5)}",
                        avg_abs_pearson_panel(complete_graph)
                    ],
                    id='avg-abs-pearson-coefficient-leaderboard'
                ),
            ], style={
                'marginTop': '20px',
                'padding': '20px',
                'boxSizing': 'border-box',
                'backgroundColor': 'rgba(255, 255, 255, 0.88)',
                'border': '1px solid #C9D4E6',
                'fontFamily': '"Open Sans", verdana, arial, sans-serif',
                'fontSize': '12px',
                'color': '#2a3f5f'
            }
            )
        ], style={
            'width': '100vw',
            'display': 'flex',
            'justify-content': 'space-evenly'
        })
    ])
    register_callbacks(app, graphs_by_threshold, figures_by_threshold, position_views)


# Initialization
app = Dash(__name__)
app.title = "Clustock"
run_full_pipeline(use_sample=False)


if __name__ == '__main__':
    # use_sample=False for full S&P 100 (~100 tickers); True for 15 tickers (faster).
    app.run(debug=False)
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': ['compute', 'visualization', 'correlation_graph', 'constants', 'config', 'dash'],
    #     'allowed-io': ['run_full_pipeline'],
    #     'max-line-length': 120
    # })
