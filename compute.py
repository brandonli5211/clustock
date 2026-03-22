"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Computation module: log returns, Pearson correlation, graph building.
"""

from __future__ import annotations
from typing import Optional
from math import log
import pandas as pd
from correlation_graph import CorrelationGraph
from data_reader import download_tickers, get_sectors_for_tickers
from constants import CORRELATION_THRESHOLD


def compute_log_returns(prices: list[float]) -> list[float]:
    """Compute log returns R_t = ln(P_t / P_{t-1}) for a price series.

    Returns list of length len(prices)-1.
    Preconditions:
    - len(prices) >= 2
    """
    return [log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]


def log_return_list(df: pd.DataFrame) -> dict[str, list[float]]:
    """Return a dictionary of ticker keys to a list of log returns value for the corresponding ticker."""
    log_returns = {}
    for ticker, group in df.groupby('Ticker'):
        group_sorted = group.sort_values('Date')
        # .dropna() remove NaN rows if a stock doesn't have a close price, and p > 0 removes zero/negative prices
        close_prices = [p for p in list(group_sorted['Close'].dropna()) if p > 0]
        if len(close_prices) < 2:  # need at least two close prices to calculate a log return
            continue
        log_returns[ticker] = compute_log_returns(close_prices)
    return log_returns


def pearson_correlation(a: list[float], b: list[float]) -> float:
    """Compute Pearson correlation coefficient between two equal-length series.

    Returns r in [-1, 1]. r=1: perfect positive, r=-1: perfect negative, r=0: no correlation.
    Formula: r = sum[(a_i - a_avg)(b_i - b_avg)] / (sqrt(sum[(a_i - a_avg)^2]) * sqrt(sum[(b_i - b_avg)^2]))

    Preconditions:
    -  len(a) == len(b)
    """
    n = len(a)
    a_avg = sum(a) / n
    b_avg = sum(b) / n
    numerator = sum((a[i] - a_avg) * (b[i] - b_avg) for i in range(n))
    # calculate standard deviations
    a_std = sum((a[i] - a_avg) ** 2 for i in range(n)) ** 0.5
    b_std = sum((b[i] - b_avg) ** 2 for i in range(n)) ** 0.5
    if a_std == 0.0 or b_std == 0.0:
        return 0.0
    else:
        return numerator / (a_std * b_std)


def create_edges_in_graph(graph: CorrelationGraph,
                          log_returns: dict[str, list[float]],
                          tickers: list[str],
                          threshold: float = CORRELATION_THRESHOLD) -> None:
    """
    Create edges in graph, using the log_returns of the tickers in graph.
    Designed as a helper function to build_correlation_graph().
    Preconditions:
    - 0 <= threshold <= 1
    """
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            # tickers[i] and tickers [j] are the log return lists of two tickers
            if (tickers[i] not in log_returns or tickers[j] not in log_returns) or \
                    (len(log_returns[tickers[i]]) != len(log_returns[tickers[j]])):
                continue  # skip if a ticker failed to download, or the there aren't the same number of log returns
            # calculate Pearson correlation coefficient
            r = pearson_correlation(log_returns[tickers[i]], log_returns[tickers[j]])
            if abs(r) > threshold:  # r is above the threshold. Edge will be added
                graph.add_edge(tickers[i], tickers[j], r)


def build_correlation_graph(
    tickers: set[str],
    period: Optional[str] = None,
    date_range: Optional[tuple[str, str]] = None,
    interval: Optional[str] = None,
    threshold: float = CORRELATION_THRESHOLD
) -> CorrelationGraph:
    """Build weighted undirected graph from price data.

    Nodes = stocks (ticker, sector). Edges = pairs with |correlation| > threshold.
    Use Adj Close (or Close) for log returns, then Pearson correlation between pairs.

    Preconditions:
    - All tickers in tickers are valid yfinance ticker symbols.
    - (period is None) != (date_range is None)
    - if date_range is not None, len(date_range) == 2, date_range[0] is the start date, date_range[1] is the end date
    - 0 <= threshold <= 1
    """
    g = CorrelationGraph()
    start, end = date_range if date_range else (None, None)
    df = download_tickers(tickers, period=period, start=start, end=end, interval=interval)

    # -------------------- Add tickers as nodes in the graph
    for ticker, sector in get_sectors_for_tickers(tickers).items():  # Key-value pair is ticker: sector
        g.add_node(ticker, sector)

    # -------------------- Add edges to graph if necessary
    # Calculating log returns for each ticker. This becomes a dictionary of {ticker: [log returns]}
    log_returns = log_return_list(df)
    # Calculate Pearson correlation coefficient between each vertex in the graph.
    # Then, add edges when the coefficient is above threshold.
    create_edges_in_graph(g, log_returns, g.get_all_tickers(), threshold)

    return g


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['pandas', 'correlation_graph', 'data_reader', 'constants', 'math'],
    # })
