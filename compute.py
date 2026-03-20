"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Computation module: log returns, Pearson correlation, graph building.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
from correlation_graph import CorrelationGraph
from data_reader import download_tickers, get_sectors_for_tickers
from constants import CORRELATION_THRESHOLD


def add_nodes_from_tickers(
    graph: CorrelationGraph,
    tickers: list[str] | set[str],
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch price data and sector info, then add one node per ticker to the graph.

    This is the logic that used to live in CorrelationGraph.add_node.
    Returns the downloaded DataFrame (for use by build_correlation_graph).

    Preconditions:
        - period is not None, or (start and end are provided)
    """
    ticker_list = list(tickers) if isinstance(tickers, set) else tickers
    df = download_tickers(
        set(ticker_list), period=period, start=start, end=end, interval=interval
    )
    sectors = get_sectors_for_tickers(ticker_list)
    for ticker in ticker_list:
        graph.add_node(ticker, sectors.get(ticker, 'Unknown'))
    return df


def compute_log_returns(prices: list[float]) -> list[float]:
    """Compute log returns R_t = ln(P_t / P_{t-1}) for a price series.

    Returns list of length len(prices)-1.
    """
    raise NotImplementedError("TODO: implement")


def pearson_correlation(a: list[float], b: list[float]) -> float:
    """Compute Pearson correlation coefficient between two equal-length series.

    Returns r in [-1, 1]. r=1: perfect positive, r=-1: perfect negative, r=0: no correlation.
    Formula: r = sum[(a_i - a_avg)(b_i - b_avg)] / (sqrt(sum[(a_i - a_avg)^2]) * sqrt(sum[(b_i - b_avg)^2]))
    """
    raise NotImplementedError("TODO: implement")


def build_correlation_graph(
    df: pd.DataFrame,
    sectors: dict[str, str],
    threshold: float = CORRELATION_THRESHOLD
) -> CorrelationGraph:
    """Build weighted undirected graph from price data.

    Nodes = stocks (ticker, sector). Edges = pairs with |correlation| > threshold.
    Use Adj Close (or Close) for log returns, then Pearson correlation between pairs.
    """
    raise NotImplementedError("TODO: implement")


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['pandas', 'correlation_graph', 'data_reader', 'constants'],
    })
