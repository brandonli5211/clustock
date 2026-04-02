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
import pandas as pd
import yfinance_cache as yf
from pandas import DataFrame


def access_one_stock(ticker: str, ticker_dataframe: DataFrame) -> dict[str, list[Any]]:
    """Access the info for one stock.
        Preconditions:
            - ticker must be a valid ticker

    >>> df = pd.DataFrame({
    ...     'Ticker': ['AAA', 'AAA'],
    ...     'Date': pd.to_datetime(['2026-01-01', '2026-01-02']),
    ...     'Open': [10.0, 11.0],
    ...     'Close': [10.5, 11.5]
    ... })
    >>> access_one_stock('AAA', df)
    {'2026-01-01': [10.0, 10.5], '2026-01-02': [11.0, 11.5]}
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

    >>> df = pd.DataFrame({
    ...     'Ticker': ['AAA', 'AAA', 'BBB'],
    ...     'Date': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-01']),
    ...     'Open': [10.0, 11.0, 20.0],
    ...     'Close': [10.5, 11.5, 20.5]
    ... })
    >>> result = access_all_stocks(df)
    >>> sorted(result.keys())
    ['AAA', 'BBB']
    >>> result['BBB']
    {'2026-01-01': [20.0, 20.5]}
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

    >>> old_ticker = yf.Ticker
    >>> class FakeTicker:
    ...     def __init__(self, ticker):
    ...         self.info = {'sector': 'Tech'} if ticker == 'AAA' else {}
    >>> yf.Ticker = FakeTicker
    >>> get_sectors_for_tickers({'AAA', 'BBB'}) == {'AAA': 'Tech', 'BBB': 'Unknown'}
    True
    >>> yf.Ticker = old_ticker
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

    >>> old_download = yf.download
    >>> def fake_download(_tickers, threads=False, progress=True, **params):
    ...     index = pd.to_datetime(['2026-01-01', '2026-01-02'])
    ...     cols = pd.MultiIndex.from_product([['Open', 'Close'], ['AAA', 'BBB']])
    ...     values = [[10.0, 20.0, 10.5, 20.5], [11.0, 21.0, 11.5, 21.5]]
    ...     return pd.DataFrame(values, index=index, columns=cols)
    >>> yf.download = fake_download
    >>> downloaded = download_tickers({'AAA', 'BBB'}, period='1mo', interval='1d')
    >>> sorted(downloaded.columns.tolist())
    ['Close', 'Date', 'Open', 'Ticker']
    >>> sorted(downloaded['Ticker'].unique().tolist())
    ['AAA', 'BBB']
    >>> yf.download = old_download
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


if __name__ == '__main__':
    import doctest
    import python_ta

    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['typing', 'pandas', 'yfinance_cache'],
        'allowed-io': [],
        'max-line-length': 120
    })
