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
from typing import Any
import pandas as pd
import yfinance_cache as yf


def download_tickers(tickers_list: set[str]) -> pd.DataFrame:
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
    """
    # Main arguments for yf.download(): tickers list, period, interval, threads=False
    # Without threads=False, download may not work.
    # pandas imported from the download, so we can flatten the table given by yf.download().
    #     # doing this will make accessing the data much easier and more readable.
    data = yf.download(tickers_list, period='5d', interval='1d', threads=False)

    # .stack() turns level 1 columns (which are the ticker names) into rows of Date (level 0 cols were Date)
    # .reset_index() removes Ticker out of index, so the column name becomes Date and Ticker, like an Excel spreadsheet
    # This way, we can access each row and the data points like Date, Ticker, etc. will be our attributes
    data_flattened = data.stack(level=1, future_stack=True).reset_index()
    # Renaming columns to match data.
    data_flattened.rename(columns={'level_0': 'Date', 'level_1': 'Ticker'}, inplace=True)
    return data_flattened


if __name__ == '__main__':
    # Example tickers.
    TICKERS = {'AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'NVDA', 'KO', 'WMT', 'DIS', 'F', 'JPM', 'V'}
    all_tickers = download_tickers(TICKERS)
    print()
    # Accessing one stock's info
    # Use double brackets [['JPM']] to always return a DataFrame, then reset_index()
    # so 'Ticker' becomes a regular column again (not the index).
    ticker_index = all_tickers.set_index('Ticker').sort_index()
    # For one stock:
    # jpm_data = ticker_index.loc[['JPM']].reset_index()
    # for row in jpm_data.itertuples(index=False):
    #     print(f"{row.Ticker}    {row.Date}    {row.Open}   {row.Close}  {row.Volume}")

    # For ALL stocks:
    for ticker, group in all_tickers.groupby('Ticker'):
        group = group.reset_index(drop=True)
        for row in group.itertuples(index=False):
            # Two ways to write:
            #             print(f"{getattr(row, 'Ticker')}    {getattr(row, 'Date')}    \
            # {getattr(row, 'Open')}   {getattr(row, 'Close')}  {getattr(row, 'Volume')}")
            print(f"{row.Ticker}    {row.Date}    {row.Open}    {row.Close}    {row.Volume}")

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
