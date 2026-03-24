"""CSC111 Winter 2026 - Project 2: Clustock

Entry point: download prices, build the correlation graph, open the interactive visualization.
"""

from __future__ import annotations

from compute import build_correlation_graph
from visualization import run_visualization
from constants import SP100_TICKERS


def run_full_pipeline(use_sample: bool = True) -> None:
    """Run the full pipeline: fetch data, build graph, launch Plotly visualization.

    If use_sample is True, only the first 15 S&P 100 tickers are used (faster). If False,
    all tickers in constants.SP100_TICKERS are used. Uses one month of daily bars by default.
    """
    tickers = set(SP100_TICKERS[:15]) if use_sample else set(SP100_TICKERS)
    print('Building correlation graph for', len(tickers), 'tickers...')
    graph = build_correlation_graph(tickers, period='1mo', interval='1d')
    print('Graph density:', graph.density())
    print('Nodes:', len(graph.get_all_tickers()))

    print('Opening interactive visualization...')
    run_visualization(graph)


if __name__ == '__main__':
    # use_sample=False for full S&P 100 (~100 tickers); True for 15 tickers (faster).
    run_full_pipeline(use_sample=False)
