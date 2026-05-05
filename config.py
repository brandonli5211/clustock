"""CSC111 Winter 2026 - Project 2: Clustock

Configuration file for the plotly visualization
"""

# https://plotly.com/python/configuration-options/
CONFIG = {
    'scrollZoom': True,
}


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': [],
        'allowed-io': [],
        'max-line-length': 120
    })
