"""CSC111 Winter 2026 - Project 2: Clustock

Weighted undirected graph for stock correlations: nodes are tickers with GICS sectors;
edges store Pearson correlation weights above a threshold.
"""

from __future__ import annotations

from networkx.classes import number_of_edges

from constants import BFS_DEPTH, SECTORS
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

    def get_weight(self, ticker1: str, ticker2: str) -> float:
        """Get the correlation weight between two nodes"""
        return self.get_neighbours(ticker1)[ticker2]

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

    def subgraph(self, tickers: list[str]) -> CorrelationGraph:
        """Return a correlation subgraph of the original graph consisting of only nodes and edges included in
        the given tickers list. Edges between nodes contained in the subgraph and outside nodes are not preserved"""

        subgraph = CorrelationGraph()
        for ticker in tickers:
            subgraph.add_node(ticker, self.get_sector(ticker))
            for neighbour in self.get_neighbours(ticker):
                subgraph.add_edge(ticker, neighbour, self.get_neighbours(ticker)[neighbour])

        return subgraph

    def bfs_crash_simulation(self, start_ticker: str, max_depth: int = BFS_DEPTH) -> dict[int, set[str]]:
        """Breadth-first search from start_ticker along correlation edges.

        Depth 0 is the start ticker; depth k is tickers k edges away (not yet visited).
        Used to model how far a price shock could propagate through the network.

        Returns:
            Mapping from depth (int) to the set of tickers first reached at that depth.

        Preconditions:
            - start_ticker is in the graph.
        """
        queue = deque()
        visited = {}
        nodes_at_depths = {} # Output set

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
                    visited[next] = visited[curr] + 1

        return nodes_at_depths

    def _reachable_from_crash(self, start_ticker: str) -> set[str]:
        """All tickers within BFS_DEPTH hops of start_ticker along correlation edges.

        Union of every BFS layer returned by bfs_crash_simulation(start_ticker).
        """
        layers = self.bfs_crash_simulation(start_ticker)
        return {ticker for stocks in layers.values() for ticker in stocks}

    def get_pivot_candidates(self, start_ticker: str) -> list[tuple[str, int]]:
        """ Returns:
            List of ``(ticker, sector_diversity)`` where ``sector_diversity`` is
            the number of distinct sectors among {this stock} ∪ {reached neighbours},
            only including stocks with diversity ≥ 2. Sorted with highest diversity first.
        """
        reachable = self._reachable_from_crash(start_ticker)

        candidates: list[tuple[str, int]] = []
        for ticker in reachable:
            sectors_here = {self._vertices[ticker].sector}
            for neighbour in self._vertices[ticker].neighbours:
                if neighbour in reachable:
                    sectors_here.add(self._vertices[neighbour].sector)
            if len(sectors_here) > 1:
                candidates.append((ticker, len(sectors_here)))

        # Highest sector_diversity first (sort by the integer, largest first).
        return sorted(candidates, key=lambda pair: pair[1], reverse=True)

    def sector_density(self, sector: str) -> float:
        """Return the density of the isolated subgraph of the given sector"""

        tickers_in_sector = []

        for ticker in self.get_all_tickers():
            if self.get_sector(ticker) == sector:
                tickers_in_sector.append(ticker)

        sector_subgraph = self.subgraph(tickers_in_sector)
        return sector_subgraph.density()

    def get_ordered_sector_densities(self, limit: int = 11) -> list[tuple[str, int]]:
        """Return list or ordered tuples mapping (sector, density) sorted from highest to least density"""
        densities = []
        for sector in SECTORS:
            density = self.sector_density(sector)
            densities.append((sector, density))
        densities.sort(key=lambda pair: (-pair[1], pair[0]))
        return densities[:limit]

    def get_average_abs_weight(self) -> float:
        """Return the average absolute weight between two nodes in the graph"""
        # This graph has unweighted edges, so I will doublecount the total edge weights and doublecount the total
        # number of edges because this is easier than storing each edge that has been used so far
        edge_total = 0
        correlation_total = 0
        for u in self.get_all_tickers():
            for v in self.get_all_tickers():
                if u != v:
                    correlation_total += abs(self.get_weight(u, v))
                    edge_total += 1

        return correlation_total / edge_total

    def sector_average_abs_pearson_coefficients(self, sector: str) -> float:
        """Return the average absolute value of the pearson correlation coefficient between two tickers
        in a sector; if a sector contains only 1, return -1 as the output"""
        tickers_in_sector = []

        for ticker in self.get_all_tickers():
            if self.get_sector(ticker) == sector:
                tickers_in_sector.append(ticker)

        sector_subgraph = self.subgraph(tickers_in_sector)

        if len(tickers_in_sector) <= 1:
            return -1
        else:
            return sector_subgraph.get_average_abs_weight()

    def get_ordered_sector_abs_pearson_coefficients(self, limit: int = 11) -> list[tuple[str, int]]:
        """Return list or ordered tuples mapping (sector, density) sorted from highest to least density"""
        abs_pearson_coefficients = []
        for sector in SECTORS:
            abs_pearson_coefficient = self.sector_average_abs_pearson_coefficients(sector)
            abs_pearson_coefficients.append((sector, abs_pearson_coefficient))
        abs_pearson_coefficients.sort(key=lambda pair: (-pair[1], pair[0]))
        return abs_pearson_coefficients[:limit]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['constants'],
    # })
