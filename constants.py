"""CSC111 Winter 2026 - Project 2: Clustock

Constants: tickers, periods, BFS depth, and visualization settings.
"""

# S&P 100  tickers (as of 2024-2025)
# Source: S&P Dow Jones Indices, various financial sources
# Update periodically as the index rebalances
SP100_TICKERS = [
    'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'GOOG', 'META', 'BRK-B',
    'JPM', 'V', 'UNH', 'JNJ', 'XOM', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
    'PEP', 'KO', 'AVGO', 'COST', 'LLY', 'WMT', 'MCD', 'CSCO', 'ACN', 'ABT',
    'TMO', 'DHR', 'NEE', 'ADBE', 'NKE', 'CRM', 'PM', 'TXN', 'BMY', 'UNP',
    'RTX', 'HON', 'UPS', 'LOW', 'AMGN', 'QCOM', 'INTU', 'SPGI', 'CAT', 'AXP',
    'DE', 'BKNG', 'AMAT', 'SBUX', 'GILD', 'ADI', 'LMT', 'MDT', 'VZ', 'ISRG',
    'REGN', 'PLD', 'BLK', 'T', 'SYK', 'CI', 'NOW', 'CMCSA', 'ZTS',
    'DUK', 'SO', 'BDX', 'BSX', 'EOG', 'SLB', 'PGR', 'EQIX', 'ITW', 'MO',
    'APD', 'APTV', 'KLAC', 'SHW', 'MCK', 'PANW', 'PSA', 'WM', 'CB', 'MDLZ',
    'CME', 'ADP', 'ELV', 'NXPI', 'ORLY', 'SNPS', 'CDNS', 'MAR', 'CL', 'ECL',
    'AON', 'ICE', 'FIS', 'AIG', 'MET', 'GM', 'USB', 'PNC', 'FCX',
]

# Period definitions for Stable vs Volatile comparison
# Stable: Calm market period (e.g., 2023 recovery)
# Volatile: High volatility period (e.g., 2022 bear market, or COVID March 2020)
STABLE_PERIOD = '4mo'   # Will use specific start/end dates
VOLATILE_PERIOD = '4mo'

# BFS depth for crash simulation (degrees of separation)
BFS_DEPTH = 2

# Node size mode for visualization:
# - 'linear' keeps size tied directly to degree
# - 'relative' scales size relative to the largest degree in the current graph
NODE_SIZE_MODE = 'relative'
