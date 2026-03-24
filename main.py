"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Main File
"""

from __future__ import annotations

from compute import build_correlation_graph
from visualization import run_visualization
from constants import SP100_TICKERS


def run_full_pipeline(use_sample: bool = True) -> None:
    """Run data download -> graph build -> visualization.

    If use_sample=True, uses only first 15 tickers for faster testing.
    """
    tickers = set(SP100_TICKERS[:15]) if use_sample else set(SP100_TICKERS)
    print('Building correlation graph for', len(tickers), 'tickers...')
    graph = build_correlation_graph(tickers, period='1mo', interval='1d')
    print('Graph density:', graph.density())
    print('Nodes:', len(graph.get_all_tickers()))

    print('Opening interactive visualization...')
    print("Pivot candidates", graph.get_pivot_candidates('AAPL'))
    run_visualization(graph)


if __name__ == '__main__':
    # use_sample=False for full S&P 100 (~100 tickers); True for 15 tickers (faster).
    run_full_pipeline(use_sample=False)
