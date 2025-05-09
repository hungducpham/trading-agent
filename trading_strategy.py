class TradingStrategy:
    """
    Base class for the different trading strategies. The different strategies must implement the perform_action method.
    """

    def perform_action(self, date, data, portfolio, cash):
        pass
