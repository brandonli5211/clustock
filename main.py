"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Main File
"""

from __future__ import annotations

from data_reader import download_tickers, get_sectors_for_tickers
from compute import build_correlation_graph
from visualization import run_visualization
from constants import SP100_TICKERS


def run_full_pipeline(use_sample: bool = True) -> None:
    """Run data download -> graph build -> visualization.

    If use_sample=True, uses only first 15 tickers for faster testing.
    """
    tickers = SP100_TICKERS[:15] if use_sample else SP100_TICKERS
    print('Downloading data for', len(tickers), 'tickers...')
    df = download_tickers(tickers, period='1mo', interval='1d')
    print('Data shape:', df.shape)

    print('Fetching sector info...')
    sectors = get_sectors_for_tickers(tickers)

    print('Building correlation graph...')
    graph = build_correlation_graph(df, sectors)
    print('Graph density:', graph.density())
    print('Nodes:', len(graph.get_all_tickers()))

    print('Opening interactive visualization...')
    run_visualization(graph)


if __name__ == '__main__':
    # Use sample (15 tickers) for quick demo. Set use_sample=False for full S&P 100.
    run_full_pipeline(use_sample=True)
