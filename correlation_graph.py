"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Weighted undirected graph for stock correlations.
"""

from __future__ import annotations
import yfinance_cache as yf
from constants import BFS_DEPTH
from typing import Optional, Any
from data_reader import download_tickers, access_one_stock
import pprint  # For testing (for now)


class _Vertex:
    """A vertex in the correlation graph (represents a stock)."""
    ticker: str
    date: str
    sector: str
    neighbours: dict[str, float]  # ticker -> correlation weight
    data: tuple[str, str]  # (open, close)

    def __init__(self, ticker: str, date: str, sector: str, data: tuple[str, str]) -> None:
        self.ticker = ticker
        self.date = date
        self.sector = sector
        self.neighbours = {}
        self.open_price = data[0]
        self.close_price = data[1]


class CorrelationGraph:
    """Weighted undirected graph of stock correlations."""

    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._vertices = {}

    def add_node(self, ticker_set: set[str] | str,
                 period: Optional[str] = None,
                 start: Optional[str] = None,
                 end: Optional[str] = None,
                 interval: Optional[str] = None) -> None:
        """Add a stock node if not already present.
            Preconditions:
            - ticker_set contains valid yfinance tickers.
            - (period in {'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'})  \
            or (start and end are valid dates)
            - interval in {1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo}
        """
        if isinstance(ticker_set, str):  # MUST be a set in order for the download function to work
            ticker_set = {ticker_set}
        graph_tickers = download_tickers(ticker_set, period=period, start=start, end=end, interval=interval)
        for ticker in ticker_set:
            stock_data = access_one_stock(ticker, graph_tickers)
            sector = yf.Ticker(ticker).info.get('sector', 'Unknown')
            for time in stock_data:
                stock_data_name = f"{ticker} {time}"
                if stock_data_name not in self._vertices:
                    self._vertices[stock_data_name] = _Vertex(ticker=ticker,
                                                              date=time,
                                                              sector=sector,
                                                              data=(stock_data[time][0],
                                                                    stock_data[time][1])
                                                              )

    def add_edge(self, ticker1: str, ticker2: str, weight: float) -> None:
        """Add undirected edge between two stocks with given correlation weight."""
        raise NotImplementedError("TODO: implement")

    def get_vertices(self) -> dict[str, _Vertex]:
        """Return list of all ticker symbols."""
        return self._vertices

    def get_vertices_date(self, dates: set[str] | str) -> dict[str, _Vertex]:
        """Return a dictionary of ticker names as the key and TickerVertexes and the value
        with the given date.
            Preconditions:
                - date must be a valid date from within the time period and interval downloaded
        """
        if isinstance(dates, str):
            dates = {dates}
        output = {f"{self._vertices[vertice].ticker} {self._vertices[vertice].date}": self._vertices[vertice]
                  for vertice in self._vertices if self._vertices[vertice].date in dates}
        return output

    def get_vertices_ticker(self, ticker_names: set[str] | str) -> dict[str, _Vertex]:
        """Return a dictionary of ticker names as the key and TickerVertexes and the value
        with the given ticker_name.
            Preconditions:
                - ticker_name in {self._vertices[vertice].ticker for vertice in self._vertices}
        """
        if isinstance(ticker_names, str):
            ticker_names = {ticker_names}
        output = {f"{self._vertices[vertice].ticker} {self._vertices[vertice].date}": self._vertices[vertice]
                  for vertice in self._vertices if self._vertices[vertice].ticker in ticker_names}
        return output

    def get_neighbours(self, ticker: str) -> dict[str, float]:
        """Return dict of neighbour ticker -> correlation weight."""
        return self._vertices[ticker].neighbours

    def density(self) -> float:
        """Compute graph density D = 2|E| / (|V|(|V|-1))."""
        raise NotImplementedError("TODO: implement")

    def bfs_crash_simulation(self, start_ticker: str, max_depth: int = BFS_DEPTH) -> dict[int, set[str]]:
        """BFS from a 'crashing' stock. Returns {depth: set of tickers at that depth}."""
        raise NotImplementedError("TODO: implement")

    def get_pivot_candidates(self, start_ticker: str) -> list[tuple[str, int]]:
        """Stocks that connect multiple sectors within BFS reach. Returns list of (ticker, sector_count)."""
        raise NotImplementedError("TODO: implement")


if __name__ == '__main__':
    g = CorrelationGraph()
    g.add_node({'AAPL', 'GOOGL'}, period='5d', interval='1d')
    g.add_node('JPM', period='1mo', interval='1wk')
    g_vertices = g.get_vertices()
    example = {g_vertices[ticker].open_price: g_vertices[ticker].close_price for ticker in g_vertices
               if g_vertices[ticker].ticker == "AAPL"}
    pprint.pprint(example)

    g2 = CorrelationGraph()
    g2.add_node({'F', 'V', 'JPM'}, period='1mo', interval='1wk')
    g2.add_node('AAPL', period='5d', interval='1d')  # Period and interval can be different
    # for start and end dates, it goes from dates start to end exclusive [start, end)
    g2.add_node({'GOOGL'}, start='2026-03-01', end='2026-03-06', interval='1d')  # Can do start, end times
    g2.add_node({'META', 'NVDA'}, start='2026-03-02', end='2026-03-06', interval='1d')
    pprint.pprint(g2.get_vertices())
    pprint.pprint(g2.get_vertices_ticker('META'))
    # import doctest
    # doctest.testmod()
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['constants'],
    # })
