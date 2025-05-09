from trading_strategy import TradingStrategy
from trading_constants import *
import utils_trading as ut


class SimplePriceActionStrategy(TradingStrategy):

    def perform_action(self, date, data, portfolio, cash):
        """
        Perform actions based on simple price increase strategy.

        Parameters:
        - date: datetime
        - data: pandas DataFrame with DateTimeIndex and columns: ['symbol', 'open', 'close', 'high', 'low']
        - portfolio: dict mapping symbol to quantity held
        - cash: available cash before action

        Returns:
        - updated_portfolio: dict with updated quantities
        - updated_cash: updated cash after action
        - actions_log: list of executed actions
        """

        updated_portfolio = portfolio.copy()
        updated_cash = cash
        trading_history = []

        # Filter today's and yesterday's data
        if date not in data.index:
            # Skip if date not available (i.e. outside of date range, or weekends)
            return updated_portfolio, updated_cash, trading_history

        today_data = data.loc[date]
        try:
            yesterday = data.index[data.index.get_loc(date) - 1]
        except IndexError:
            return updated_portfolio, updated_cash, trading_history  # Skip if no previous day
        yesterday_data = data.loc[yesterday]

        for symbol in portfolio.keys():
            today_close = today_data[(CLOSE, symbol)]
            yesterday_close = yesterday_data[(CLOSE, symbol)]

            # Buy as much as possible if price increased
            if today_close > yesterday_close:
                shares_to_buy = int(updated_cash / today_close)
                if shares_to_buy > 0:
                    updated_cash -= shares_to_buy * today_close
                    updated_portfolio[symbol] = updated_portfolio.get(symbol, 0) + shares_to_buy
                    trading_history.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'Buy',
                        'quantity': shares_to_buy,
                        'portfolio': updated_portfolio,
                        'cash': updated_cash,
                        "total_value": ut.calculate_portfolio_value(date, data, updated_portfolio, updated_cash)
                    })

            # Sell all if price decreased
            elif today_close < yesterday_close and updated_portfolio.get(symbol, 0) > 0:
                shares_to_sell = updated_portfolio[symbol]
                updated_cash += shares_to_sell * today_close
                updated_portfolio[symbol] = 0
                trading_history.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'Sell',
                    'quantity': shares_to_sell,
                    'portfolio': updated_portfolio,
                    'cash': updated_cash,
                    "total_value": ut.calculate_portfolio_value(date, data, updated_portfolio, updated_cash)
                })

        return updated_portfolio, updated_cash, trading_history