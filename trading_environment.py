import copy
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import trading_constants
from trading_constants import *
import utils_trading as ut
import matplotlib.pyplot as plt


class TradingEnvironment:
    start_date = None
    end_date = None

    current_step = None
    cash = None
    portfolio = None
    total_value = None
    portfolio_history = None

    """
    Trading history is a dictionary with the following keys:
     - "date": date of the history step
     - "symbol": The stock symbol
     - "action": "Sell" or "Buy"
     - "price": the stock price of the action
     - "quantity": the stock quantity of the action
     - "portfolio": the resulting portfolio
     - "cash": the remaining cash
     - "total_value": the value of the portfolio at that point + remaining cash
    """
    trading_history = None
    trading_strategy = None

    def __init__(self, symbols, start_date, end_date, trading_strategy, data=None, initial_cash=100000, transaction_cost=0.001):
        self.initial_cash = initial_cash
        self.symbols = symbols
        self.trading_strategy = trading_strategy
        if data is None:
            self.data = ut.get_data(symbols, start_date, end_date)
        else:
            self.data = data
        self.start_date = start_date
        self.end_date = end_date
        self.transaction_cost = transaction_cost
        self.reset()

    def reset(self):
        self.current_step = 0
        self.cash = self.initial_cash
        self.portfolio = {
            symbol: 0 for symbol in self.symbols
        }
        self.trading_history = []
        self.portfolio_history = {}

    def get_portfolio_value(self, portfolio, date):
        portfolio_value = 0
        date_data = self.data.loc[date]
        
        for symbol in portfolio:
            symbol_closing_price = date_data[(CLOSE, symbol)]
            portfolio_value += portfolio[symbol] * symbol_closing_price

        return portfolio_value

    def perform_trade(self):
        days_delta = (self.end_date - self.start_date).days

        for current_step in range(days_delta):
            current_day = self.start_date + timedelta(days=current_step)
            self.portfolio, self.cash, trading_history_steps = self.trading_strategy.perform_action(current_day, self.data, self.symbols, self.portfolio, self.cash)

            # Update history
            self.trading_history.append(trading_history_steps)

            # Update the final portfolio of the day and total value of the portfolio
            self.portfolio_history[current_day] = {
                    "portfolio": copy.deepcopy(self.portfolio),
                    "cash": self.cash,
                    "value": ut.calculate_portfolio_value(current_day, self.data, self.portfolio, self.cash)
                }


    def get_features(self):
        """
        :return: features
        """

        # Nothing for now
        return None

    def get_total_value_history(self, start_date, end_date):
        # Convert to DataFrame as above
        data = [(date, info['value']) for date, info in self.portfolio_history.items()]
        df = pd.DataFrame(data, columns=['date', 'total_value'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()

        # Filter by date range
        mask = (df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))
        return df.loc[mask]

    def evaluate_strategy(self, start_date, end_date, risk_free_rate=0.0):
        """
        Evaluates strategy using common financial metrics.

        Parameters:
        - start_date, end_date: date range for evaluation
        - risk_free_rate: annual risk-free rate (default 0.0)

        Returns:
        - metrics: dict of evaluation metrics
        - portfolio_df: DataFrame of portfolio values over time
        """

        # Retrieve daily portfolio values
        portfolio_df = self.get_total_value_history(start_date, end_date)
        portfolio_df = portfolio_df.sort_index()

        # Compute daily returns
        portfolio_df['daily_return'] = portfolio_df['total_value'].pct_change().fillna(0)

        # Cumulative return
        cumulative_return = (portfolio_df['total_value'].iloc[-1] / portfolio_df['total_value'].iloc[0]) - 1

        # Sharpe Ratio (assuming daily returns, 252 trading days)
        avg_daily_return = portfolio_df['daily_return'].mean()
        std_daily_return = portfolio_df['daily_return'].std()
        sharpe_ratio = (avg_daily_return - risk_free_rate / 252) / std_daily_return * np.sqrt(
            252) if std_daily_return > 0 else 0

        # Maximum Drawdown
        cumulative = portfolio_df['total_value'].cummax()
        drawdown = (portfolio_df['total_value'] - cumulative) / cumulative
        max_drawdown = drawdown.min()

        # Store Metrics
        metrics = {
            'Total Return (%)': cumulative_return * 100,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown (%)': max_drawdown * 100,
            'Final Portfolio Value': portfolio_df['total_value'].iloc[-1]
        }

        # Plot cumulative portfolio value
        plt.figure(figsize=(12, 6))
        portfolio_df['total_value'].plot(title="Cumulative Portfolio Value")
        plt.show()

        return metrics, portfolio_df