"""CSC111 Winter 2026 - Project 2: Stock Price Data Reader
NOTE: DOWNLOAD THE yfinance-cache MODULE
(Pandas imported by yfinance-cache when calling yf.download())

yfinance-cache:
Below are some important functions (maybe)(idk yet i need to see how ts works)
- yfinance.Ticker(str) - Initializes Ticker. str must be a valid ticker of a stock.
- Ticker.history(period=str) - Historical market data
of the stock.
    - Default is 1mo
- Ticker.info - Gets company info (sector, market cap, etc.)
- yfinance.download(tickers, period=str,interval=str) - Downloads period of data over interval time for multiple stocks.
the first parameter will be a string of one ticker/ list with all the tickers you want to download
with a space in between each one.
    - Download has the following data for each stock:
        - Open: price at first trade
        - High: highest price reached
        - Low: lowest price reached
        - Close: price at last trade
        - Adj Close: close price, but adjusts for dividends and stock splits
        - Volume: number of shares/contracts traded
Note:
    - interval in {1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo}
    - period in {1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max}
"""

from __future__ import annotations
from typing import Optional, Any
import pprint  # For testing (for now)
import pandas as pd
import yfinance_cache as yf
from pandas import DataFrame


def access_one_stock(ticker: str, ticker_dataframe: DataFrame) -> dict[str, list[Any]]:
    """Access the info for one stock.
        Preconditions:
            - ticker must be a valid ticker
    """
    # Use double brackets [[ticker]] to always return a DataFrame, then reset_index()
    # so 'Ticker' becomes a regular column again (not the index).

    ticker_index = ticker_dataframe.set_index('Ticker').sort_index()
    ticker_data = ticker_index.loc[[ticker]].reset_index()
    final = {str(row.Date.date()): [row.Open, row.Close]
             for row in ticker_data.itertuples(index=False)}  # Because of yfinance_cache, close gives adj close
    return final
    # for row in ticker_data.itertuples(index=False):
    #     print(f"{row.Ticker}    {row.Date}    {row.Open}   {row.Close}  {row.Volume}")


def access_all_stocks(tickers: DataFrame) -> Any:
    """Test to access ALL info from every stock.
        Preconditions:
            - every ticker in tickers must be valid
    """
    all_info = {}
    for ticker, group in tickers.groupby('Ticker'):
        ticker_info = {}
        group = group.reset_index(drop=True)
        for row in group.itertuples(index=False):
            # Two ways to write:
            #             print(f"{getattr(row, 'Ticker')}    {getattr(row, 'Date')}    \
            # {getattr(row, 'Open')}   {getattr(row, 'Close')}  {getattr(row, 'Volume')}")
            # print(f"{row.Ticker}    {row.Date}    {row.Open}    {row.Close}    {row.Volume}")
            date = str(row.Date.date())
            ticker_info[date] = [row.Open, row.Close]
        all_info[ticker] = ticker_info
    return all_info


def get_sectors_for_tickers(tickers: set[str]) -> dict[str, str]:
    """Return sector for each ticker from GICS via yfinance.

    Returns {ticker: sector} for all tickers. Uses 'Unknown' if sector missing.
    Preconditions:
        - tickers contains valid yfinance ticker symbols
    """
    result: dict[str, str] = {}
    for t in tickers:
        sector = yf.Ticker(t).info.get('sector', 'Unknown')
        result[t] = sector
    return result


def download_tickers(tickers: set[str],
                     period: Optional[str] = None,
                     start: Optional[str] = None, end: Optional[str] = None,
                     interval: Optional[str] = None) -> pd.DataFrame:
    """Download the tickers.
    This will also give us many pieces of data needed, such as Open, Close, High, Low, etc.
    Order of attributes:
        - Date
        - Ticker
        - Adj Close
        - Close
        - High
        - Low
        - Open
        - Volume
    Preconditions:
        - every ticker in tickers must be a valid ticker in yfinance
        - period is not None or (start is None or end is None)
    """
    params = {'period': period, 'interval': interval, 'start': start, 'end': end}
    params = {k: s for k, s in params.items() if s}
    data = yf.download(tickers, threads=False, progress=True, **params)
    # auto_adjust is default True, so Close becomes Adj Close.

    if isinstance(data.columns, pd.MultiIndex):  # Adding more than one ticker
        # .stack() turns level 1 columns (which are the ticker names) into rows of Date (level 0 cols were Date)
        # .reset_index() removes Ticker out of index, so the column name becomes Date and Ticker,
        # like an Excel spreadsheet.
        # This way, we can access each row and the data points like Date, Ticker, etc. will be our attributes
        data_flattened = data.stack(level=1, future_stack=True).reset_index()
        # Renaming columns to match data.
        data_flattened.rename(columns={'level_0': 'Date', 'level_1': 'Ticker'}, inplace=True)
    else:  # Only want to add one ticker
        data_flattened = data.reset_index()
        data_flattened['Ticker'] = next(iter(tickers))
    return data_flattened


class TickerGraph:
    """A graph containing TickerVertexes."""
    _vertices: dict[str, TickerVertex]

    def __init__(self) -> None:
        self._vertices = {}

    # def add_vertices_period(self, ticker_set: set[str] | str,
    #                         period: Optional[str] = None, interval: Optional[str] = None) -> None:
    #     """Create all vertices of TickerGraph given ticker_set of tickers."""
    #     if isinstance(ticker_set, str):  # MUST be a set in order for the download function to work
    #         ticker_set = {ticker_set}
    #     graph_tickers = download_tickers(ticker_set, period=period, interval=interval)
    #     for ticker in ticker_set:
    #         stock_data = access_one_stock(ticker, graph_tickers)
    #         for time in stock_data:
    #             stock_data_name = f"{ticker}    {time}"
    #             if stock_data_name not in self._vertices:
    #                 self._vertices[stock_data_name] = TickerVertex(name=ticker,
    #                                                                date=time,
    #                                                                data=(stock_data[time][0],
    #                                                                      stock_data[time][1],
    #                                                                      stock_data[time][2]))
    #
    # def add_vertices_start_end(self, ticker_set: set[str],
    #                            start: Optional[str] = None, end: Optional[str] = None,
    #                            interval: Optional[str] = None) -> None:
    #     """Create all vertices of TickerGraph given ticker_set of tickers given a start and end time.
    #     start and end must be in YYYY-MM-DD format.
    #     Below are the valid intervals for start and end times (credit to Google Gemini):
    #                        Interval | Max Historical Look-back
    #                              1m | Last 7 days
    #           2m, 5m, 15m, 30m, 90m | Last 60 days
    #                              1h | Last 730 days (2 years)
    #                    1d, 1wk, 1mo | Entire history (Max)
    #     Preconditions:
    #         - all tickers in ticker_set are valid yfinance tickers and must not be an existing ticker in the graph.
    #     """
    #     if isinstance(ticker_set, str):  # MUST be a set in order for the download function to work
    #         ticker_set = {ticker_set}
    #     graph_tickers = download_tickers(ticker_set, start=start, end=end, interval=interval)
    #     for ticker in ticker_set:
    #         stock_data = access_one_stock(ticker, graph_tickers)
    #         for time in stock_data:
    #             stock_data_name = f"{ticker}    {time}"
    #             if stock_data_name not in self._vertices:
    #                 self._vertices[stock_data_name] = TickerVertex(name=ticker,
    #                                                                date=time,
    #                                                                data=(stock_data[time][0],
    #                                                                      stock_data[time][1],
    #                                                                      stock_data[time][2]))

    # def get_vertices(self) -> dict[str, TickerVertex]:
    #     """Return the data of the given stocks on the given dates.
    #         Preconditions:
    #             - Must be a valid ticker from the downloaded tickers
    #             - Must be a valid date within the downloaded time period
    #     """
    #     return self._vertices
    #
    # def get_vertices_date(self, dates: set[str] | str) -> dict[str, TickerVertex]:
    #     """Return a dictionary of ticker names as the key and TickerVertexes and the value
    #     with the given date.
    #         Preconditions:
    #             - date must be a valid date from within the time period and interval downloaded
    #     """
    #     if isinstance(dates, str):
    #         dates = {dates}
    #     output = {f"{self._vertices[vertice].name} {self._vertices[vertice].date}": self._vertices[vertice]
    #               for vertice in self._vertices if self._vertices[vertice].date in dates}
    #     return output
    #
    # def get_vertices_ticker(self, ticker_names: set[str] | str) -> dict[str, TickerVertex]:
    #     """Return a dictionary of ticker names as the key and TickerVertexes and the value
    #     with the given ticker_name.
    #         Preconditions:
    #             - ticker_name in {self._vertices[vertice].name for vertice in self._vertices}
    #     """
    #     if isinstance(ticker_names, str):
    #         ticker_names = {ticker_names}
    #     output = {f"{self._vertices[vertice].name} {self._vertices[vertice].date}": self._vertices[vertice]
    #               for vertice in self._vertices if self._vertices[vertice].name in ticker_names}
    #     return output


class TickerVertex:
    """A ticker from yfinance."""
    name: str
    date: str
    open_price: str
    close_price: str
    volume: str
    neighbours: dict[str, TickerVertex]

    def __init__(self, name: str, date: str, data: tuple[str, str, str]) -> None:
        self.name = name
        self.date = date
        self.open_price = data[0]
        self.close_price = data[1]
        self.volume = data[2]
        self.neighbours = {}


if __name__ == '__main__':
    pass
    # Examples of adding vertices:
    # g = TickerGraph()
    # g.add_vertices_period({'F', 'V', 'JPM'}, period='1mo', interval='1wk')
    # g.add_vertices_period('AAPL', period='5d', interval='1d')  # Period and interval can be different
    # # in add_vertices_start_end(), it goes from dates start to end exclusive [start, end)
    # Can do start, end times
    # g.add_vertices_start_end({'GOOGL'}, start='2026-03-01', end='2026-03-06', interval='1d')
    # g.add_vertices_start_end({'META', 'NVDA'}, start='2026-03-02', end='2026-03-06', interval='1d')

    # Vertice retrieval. pprint statement is for visualization.
    # pprint.pprint(g.get_vertices())
    # pprint.pprint(g.get_vertices_ticker('NVDA'))
    # pprint.pprint(g.get_vertices_ticker({'GOOGL', 'JPM', 'META'}))
    # pprint.pprint(g.get_vertices_date('2026-03-03'))
    # pprint.pprint(g.get_vertices_date({'2026-03-02', '2026-02-09'}))

    # I don't remember what's below this, so ignore it.

    # Example tickers. This is used for testing.
    # For user input, they would simply call download_tickers() and assign it to a variable.
    # TICKERS = {'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'NVDA', 'KO', 'WMT', 'DIS', 'F', 'JPM', 'V'}
    # TICKERS_SMALLER = {'F', 'V', 'JPM'}
    # all_tickers = download_tickers(TICKERS_SMALLER)
    # print()
    # Accessing ONE STOCK:
    # one_stock = access_one_stock('V')
    # pprint.pprint(one_stock)

    # For ALL stocks:
    # all_stock = access_all_stocks(all_tickers)
    # pprint.pprint(all_stock)
    #
    # target_dates = {pd.Timestamp('2026-03-04'), pd.Timestamp('2026-03-05'), pd.Timestamp('2026-03-06')}
    # Prints info for every stock PER DATE
    # for date, group in all_tickers.groupby('Date'):
    #     if date in target_dates:
    #         for row in group.itertuples(index=False):
    #             print(f"{row.Ticker}    {row.Date}    {row.Open}    {row.Close}    {row.Volume}")

    # Prints info for every date for each stock
    # for ticker, group in all_tickers.groupby('Ticker'):
    #     for row in group.itertuples(index=False):
    #         if getattr(row, 'Date') in target_dates:
    #             print(f"{row.Ticker}    {row.Date}    {row.Open}    {row.Close}    {row.Volume}")

    # Access ONE stock at ONE time:
    # target_date = random.choice(list(target_dates))
    # target_ticker = random.choice(list(TICKERS_SMALLER))
    #
    # filer_ticker = all_tickers[(all_tickers['Ticker'] == target_ticker) &
    #                           (all_tickers['Date'] == pd.Timestamp(target_date))]
    # for row in filer_ticker.itertuples(index=False):
    #     print(f"{row.Ticker}    {row.Date}    {row.Open}    {row.Close}    {row.Volume}")

    # To show how we can access each column in the row:
    #   for row in db_flattened.itertuples(index=False): # We don't need to keep track of the index number
    #     print(f"Ticker: {row.Ticker} | Open: {row.Open} | Close: {row.Close}")

    # ///////////////////////// TESTING
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    #
    # import doctest
    #
    # doctest.testmod()
    #
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['csv', 'networkx'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
