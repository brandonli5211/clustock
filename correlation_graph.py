"""CSC111 Winter 2026 - Project 2: Stock Market Correlation Network (Clustock)

Weighted undirected graph for stock correlations.
One node per ticker. Populated by compute.build_correlation_graph().
"""

from __future__ import annotations

from operator import add

from constants import BFS_DEPTH
from collections import deque


class _Vertex:
    """A vertex in the correlation graph (represents a stock)."""
    ticker: str
    sector: str
    neighbours: dict[str, float]  # ticker -> correlation weight

    def __init__(self, ticker: str, sector: str = 'Unknown') -> None:
        self.ticker = ticker
        self.sector = sector
        self.neighbours = {}


class CorrelationGraph:
    """Weighted undirected graph of stock correlations.
    One node per ticker. Edges represent strong correlation (|r| > threshold).
    """

    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._vertices = {}

    def add_node(self, ticker: str, sector: str = 'Unknown') -> None:
        """Add a stock node if not already present."""
        if ticker not in self._vertices:
            self._vertices[ticker] = _Vertex(ticker, sector)

    def add_edge(self, ticker1: str, ticker2: str, weight: float) -> None:
        """Add undirected edge between two stocks with given correlation weight."""
        if ticker1 not in self._vertices or ticker2 not in self._vertices:
            return
        self._vertices[ticker1].neighbours[ticker2] = weight
        self._vertices[ticker2].neighbours[ticker1] = weight

    def get_all_tickers(self) -> list[str]:
        """Return list of all ticker symbols."""
        return list(self._vertices.keys())

    def get_sector(self, ticker: str) -> str:
        """Return GICS sector for a ticker. Returns 'Unknown' if ticker not in graph."""
        if ticker not in self._vertices:
            return 'Unknown'
        return self._vertices[ticker].sector

    def get_neighbours(self, ticker: str) -> dict[str, float]:
        """Return dict of neighbour ticker -> correlation weight."""
        if ticker not in self._vertices:
            return {}
        return dict(self._vertices[ticker].neighbours)

    def density(self) -> float:
        """Compute graph density D = 2|E| / (|V|(|V|-1))."""
        n = len(self._vertices)
        if n <= 1:
            return 0.0
        edge_count = sum(len(v.neighbours) for v in self._vertices.values()) // 2
        return 2 * edge_count / (n * (n - 1))

    def bfs_crash_simulation(self, start_ticker: str, max_depth: int = BFS_DEPTH) -> dict[int, set[str]]:
        """BFS from a 'crashing' stock. Returns {depth: set of tickers at that depth}."""
        # Todo: Test through this code to make sure it works

        queue = deque()
        visited = {}
        nodes_at_depths = {} # Output set
        depth = 0

        #BFS
        queue.append(start_ticker)
        visited[start_ticker] = 0

        # https://www.geeksforgeeks.org/python/how-to-check-if-a-deque-is-empty-in-python/
        while len(queue) != 0:
            curr = queue.popleft()
            if visited[curr] > max_depth: # if we reach a node greater than max, we're past the last layer
                return nodes_at_depths

            if visited[curr] not in nodes_at_depths.keys():
                nodes_at_depths[visited[curr]] = set()

            nodes_at_depths[visited[curr]].add(curr)

            # Adding neighbours to the queue
            for next in self.get_neighbours(curr):
                if next not in visited.keys():
                    queue.append(next)
                    visited[next] = depth + 1

            depth += 1

        return nodes_at_depths

    def get_pivot_candidates(self, start_ticker: str) -> list[tuple[str, int]]:
        """Stocks that connect multiple sectors within BFS reach.
        Returns list of (ticker, sector_count) sorted by sector_count desc.
        """
        bfs_result = self.bfs_crash_simulation(start_ticker)
        # Collect all tickers reachable from start (union of all depths).
        # Same as: reached = reached | tickers_at_depth. We loop instead.
        reached: set[str] = set()
        for tickers_at_depth in bfs_result.values():
            for ticker in tickers_at_depth:
                reached.add(ticker)
        # For each reached ticker, count how many sectors it touches
        # (its own sector + sectors of neighbours that are also in reached).
        pivots: list[tuple[str, int]] = []
        for ticker in reached:
            sectors_touched = {self._vertices[ticker].sector}
            for neighbour in self._vertices[ticker].neighbours:
                if neighbour in reached:
                    sectors_touched.add(self._vertices[neighbour].sector)
            if len(sectors_touched) > 1:
                pivots.append((ticker, len(sectors_touched)))
        # Step 3: Sort by sector_count descending. The key=lambda gives the
        # sort value: -p[1] means "use negative of sector count" so higher
        # counts appear first (e.g. -3 < -2, so 3 sorts before 2).
        def _sector_count_desc(pair: tuple[str, int]) -> int:
            return -pair[1]
        return sorted(pivots, key=_sector_count_desc)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['constants'],
    # })
