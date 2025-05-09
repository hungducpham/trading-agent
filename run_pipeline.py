import datetime
from trading_environment import TradingEnvironment
from trading_strageties.trading_strategy_simple_price_action import  SimplePriceActionStrategy


START_DATE = datetime.datetime(2010, 1, 1)
END_DATE = datetime.datetime(2010, 12, 31)

if __name__ == "__main__":
    trading_strategy = SimplePriceActionStrategy()
    trading_environment = TradingEnvironment(symbols=["SPY"], start_date=START_DATE, end_date=END_DATE, trading_strategy=trading_strategy)
    trading_environment.perform_trade()
    metrics, portfolio_df = trading_environment.evaluate_strategy(START_DATE, END_DATE)
    # Display metrics
    for key, value in metrics.items():
        print(f"{key}: {value:.2f}")