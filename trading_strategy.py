class TradingStrategy:
    """
    Base class for the different trading strategies. The different strategies must implement the perform_action method.
    """

    def __init__(self, df, symbols):
        self.df = df
        self.symbols = symbols

    def perform_action(self, date, data, portfolio, cash):
        pass
