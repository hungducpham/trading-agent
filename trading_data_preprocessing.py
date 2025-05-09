# trading_data_preprocessing.py

import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# ---------------------------
# Config
# ---------------------------
SYMBOL = "SPY"
START_DATE = "2010-01-01"
END_DATE = "2024-12-31"
FEATURES = [('SMA_20', SYMBOL), ('RSI_14', SYMBOL)]


# ---------------------------
# 2. Feature Engineering
# ---------------------------
def add_technical_indicators(df):
    # SMA
    df[FEATURES[0]] = df[('Close', SYMBOL)].rolling(window=20).mean()

    # RSI
    delta = df[('Close', SYMBOL)].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df[FEATURES[1]] = 100 - (100 / (1 + rs))

    return df


# ---------------------------
# 3. Create target (binary: price up/down next day)
# ---------------------------
def create_target(df):
    df[('Target', SYMBOL)] = (df[('Close', SYMBOL)].shift(-1) > df[('Close', SYMBOL)]).astype(int)
    return df


# ---------------------------
# 4. Scale features
# ---------------------------
def scale_features(df, features):
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])
    return df


# ---------------------------
# Main Pipeline
# ---------------------------
def prepare_data(scale_feature=False):
    df = get_data(SYMBOL, START_DATE, END_DATE)
    df = add_technical_indicators(df)
    df = create_target(df)
    # df.dropna(inplace=True)
    if scale_feature:
        df = scale_features(df, FEATURES)
    return df