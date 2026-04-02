"""CSC111 Winter 2026 - Project 2: Clustock

Entry point: download prices, build the correlation graph, open the interactive visualization.
"""

from __future__ import annotations

from compute import build_correlation_graphs
from visualization import run_visualization
from constants import SP100_TICKERS


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
    graphs_by_threshold = build_correlation_graphs(tickers, thresholds, period='1mo', interval='1d')

    for threshold in thresholds:
        graph = graphs_by_threshold[threshold]
        positive_edges, negative_edges = edge_sign_counts(graph)
        print(
            f'Threshold {threshold} -> '
            f'density: {round(graph.density(),3)}, '
            f'positive: {positive_edges}, '
            f'negative: {negative_edges}'
        )

    print('Opening interactive visualization...')
    run_visualization(graphs_by_threshold)


if __name__ == '__main__':
    # use_sample=False for full S&P 100 (~100 tickers); True for 15 tickers (faster).
    run_full_pipeline(use_sample=True)
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['compute', 'visualization', 'constants'],
        'allowed-io': ['run_full_pipeline'],
        'max-line-length': 120
    })
