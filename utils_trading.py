import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import datetime
from trading_constants import *


def get_data(symbols, start_date, end_date):
    """
    Get the historical price data of a single stock or a list of stocks.

    :param symbols: str|list[str]
    :param start_date: datetime.datetime
    :param end_date: datetime.datetime
    :return: data: pd.DataFrame
    """

    df = yf.download(symbols, start=start_date, end=end_date, progress=False)
    df.dropna(inplace=True)
    data = df[~df.index.duplicated()]
    return data


def get_price(data, symbol, date):
    return data.iloc[date][(CLOSE, symbol)]


def get_volume(data, symbol, date):
    return data.iloc[date][(VOLUME, symbol)]


def get_high(data, symbol, date):
    return data.iloc[date][(HIGH, symbol)]


def get_low(data, symbol, date):
    return data.iloc[date][(LOW, symbol)]


def calculate_portfolio_value(date, data, portfolio, cash):
    portfolio_value = cash
    for symbol in portfolio.keys():
        symbol_value = portfolio[symbol] * get_price(data, symbol, date)
        portfolio_value += symbol_value

    return portfolio