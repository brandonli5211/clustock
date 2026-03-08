"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Weighted undirected graph for stock correlations.
"""

from __future__ import annotations
from constants import BFS_DEPTH


class _Vertex:
    """A vertex in the correlation graph (represents a stock)."""
    ticker: str
    sector: str
    neighbours: dict[str, float]  # ticker -> correlation weight

    def __init__(self, ticker: str, sector: str) -> None:
        self.ticker = ticker
        self.sector = sector
        self.neighbours = {}


class CorrelationGraph:
    """Weighted undirected graph of stock correlations."""

    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._vertices = {}

    def add_node(self, ticker: str, sector: str = 'Unknown') -> None:
        """Add a stock node if not already present."""
        raise NotImplementedError("TODO: implement")

    def add_edge(self, ticker1: str, ticker2: str, weight: float) -> None:
        """Add undirected edge between two stocks with given correlation weight."""
        raise NotImplementedError("TODO: implement")

    def get_all_tickers(self) -> list[str]:
        """Return list of all ticker symbols."""
        raise NotImplementedError("TODO: implement")

    def get_sector(self, ticker: str) -> str:
        """Return GICS sector for a ticker."""
        raise NotImplementedError("TODO: implement")

    def get_neighbours(self, ticker: str) -> dict[str, float]:
        """Return dict of neighbour ticker -> correlation weight."""
        raise NotImplementedError("TODO: implement")

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
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['constants'],
    })
