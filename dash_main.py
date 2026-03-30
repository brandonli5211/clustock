"""CSC111 Winter 2026 - Project 2: Clustock

Entry point: download prices, build the correlation graph, open the interactive visualization.
"""

from __future__ import annotations

from compute import build_correlation_graphs_for_thresholds
from visualization import run_visualization, create_interactive_graph
from constants import SP100_TICKERS
from config import CONFIG

from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px


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


def run_full_pipeline(use_sample: bool = True) -> None:
    """Run the full pipeline: fetch data, build graph,launch Plotly visualization (with slider).

    If use_sample is True, only the first 15 S&P 100 tickers are used (faster). If False,
    all tickers in constants.SP100_TICKERS are used. Uses one month of daily bars by default.
    """
    tickers = set(SP100_TICKERS[:15]) if use_sample else set(SP100_TICKERS)
    print('Building correlation graph for', len(tickers), 'tickers...')
    thresholds = [x / 10 for x in range(1,11)]
    graphs_by_threshold = build_correlation_graphs_for_thresholds(tickers,thresholds, period='1mo', interval='1d')

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
    app = Dash(__name__)
    app.title = "Clustock"

    visualization_figure = create_interactive_graph(graphs_by_threshold)
    app.layout = [
        dcc.Graph(
            id="graph",
            figure=visualization_figure,
            config=CONFIG,
            # https://community.plotly.com/t/dash-css-make-a-div-full-screen/50982/2
            style={
                'width': '95vw',
                'height': '90vh'
            },
            # https://dash-resources.com/how-to-animate-dash-graphs/
            animation_options={
                'frame': {
                    'redraw': True
                },
                'transition': {
                    'duration': 500,
                    'easing': 'cubic-in-out'
                },
                'mode': 'immediate|'
            }
        ),
        dcc.Slider(
            min=0,
            max=1,
            step=0.1,
            value=0.7,
            id="threshold-slider"
        ),
        html.H2("Pivot Candidates"),
        dcc.Input(
            id="pivot_start_ticker",
            type="text",
            placeholder="Input Start Ticker"
        ),
        html.Div(
            id="test-pivot-output"
        )
    ]

    # Input Handling
    @callback(
        Output('graph', 'figure'),
        Input('threshold-slider', 'value'))
    def update_figure(selected_threshold):
        "Returns figure after handling the input"

        # Todo: Figure how to properly change this instead of having to remake the figure
        fig = create_interactive_graph(graphs_by_threshold, start_threshold=int(selected_threshold*10))
        fig.update_layout()

        return fig

    @callback(
        Output('test-pivot-output', 'children'),
        Input('threshold-slider', 'value'),
        Input("pivot_start_ticker", "value"))
    def update_pivots(selected_threshold, start_ticker):
        "Returns pivot candidates to current test div"
        if start_ticker in SP100_TICKERS:
            pivots = graphs_by_threshold[selected_threshold].get_pivot_candidates(start_ticker)
            pivot_ticker_list = [pivot[0] for pivot in pivots]
            return f"{pivot_ticker_list}"
        else:
            return "No starter ticker selected"

    app.run(debug=True)

if __name__ == '__main__':
    # use_sample=False for full S&P 100 (~100 tickers); True for 15 tickers (faster).
    run_full_pipeline(use_sample=True)
