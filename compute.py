"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Computation module: log returns, Pearson correlation, graph building.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
from correlation_graph import CorrelationGraph
from data_reader import download_tickers, get_sectors_for_tickers
from constants import CORRELATION_THRESHOLD

# tyler's code from before: 
#  def add_node(self, ticker_set: set[str] | str,
#                  period: Optional[str] = None,
#                  start: Optional[str] = None,
#                  end: Optional[str] = None,
#                  interval: Optional[str] = None) -> None:
#         """Add a stock node if not already present.
#             Preconditions:
#             - ticker_set contains valid yfinance tickers.
#             - (period in {'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'})  \
#             or (start and end are valid dates)
#             - interval in {1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo}
#         """
#         if isinstance(ticker_set, str):  # MUST be a set in order for the download function to work
#             ticker_set = {ticker_set}
#         graph_tickers = download_tickers(ticker_set, period=period, start=start, end=end, interval=interval)
#         for ticker in ticker_set:
#             stock_data = access_one_stock(ticker, graph_tickers)
#             sector = yf.Ticker(ticker).info.get('sector', 'Unknown')
#             for time in stock_data:
#                 stock_data_name = f"{ticker} {time}"
#                 if stock_data_name not in self._vertices:
#                     self._vertices[stock_data_name] = _Vertex(ticker=ticker,
#                                                               date=time,
#                                                               sector=sector,
#                                                               data=(stock_data[time][0],
#                                                                     stock_data[time][1])
#                                                               )

def add_nodes_from_tickers(
    graph: CorrelationGraph,
    tickers: set[str],
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch price data and sector info, then add one node per ticker to the graph.

    This is the logic that used to be in CorrelationGraph.add_node.
    Returns the downloaded DataFrame (for use by build_correlation_graph).

    Preconditions:
        - period is not None, or (start and end are provided)
    """
    df = download_tickers(tickers, period=period, start=start, end=end, interval=interval)
    sectors = get_sectors_for_tickers(tickers)
    for ticker in tickers:
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
