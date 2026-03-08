# Clustock – Stock Market Correlation Network

CSC111 Winter 2026 Project 2: Applications of trees and graphs.

**Team:** Tyler Christopher Lin, Brandon Zento Li, Houssam Kadri, Frank Huang

## Research Question

> To what extent do traditional GICS sectors remain mathematically distinct during periods of high market volatility, and can graph-based detection identify 'pivot stocks' that connect unrelated industries?

## Setup

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the program
python main.py
```

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point – runs full pipeline |
| `data_reader.py` | Fetches stock data from Yahoo Finance, GICS sectors |
| `correlation_graph.py` | Weighted graph, BFS, density, pivot detection |
| `compute.py` | Log returns, Pearson correlation, graph building |
| `visualization.py` | Plotly interactive graph |
| `constants.py` | S&P 100 tickers, thresholds |
| `WORK_SPLIT.md` | Task allocation for group of 4 |

## GitHub

```bash
git init
git remote add origin https://github.com/brandonli5211/clustock.git
git add .
git commit -m "Initial Clustock setup"
git push -u origin main
```

If the repo is private or returns 404, create it first at https://github.com/new named `clustock`.
