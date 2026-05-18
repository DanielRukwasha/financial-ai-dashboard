import yfinance as yf
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv
from requests import Session
import os
import streamlit as st

load_dotenv()

session = Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key)

def get_fred():
    return Fred(api_key=get_secret("FRED_API_KEY"))

def get_inflation():
    fred = get_fred()
    return fred.get_series("CPIAUCSL", observation_start="2022-01-01")

def get_fed_rate():
    fred = get_fred()
    return fred.get_series("FEDFUNDS", observation_start="2022-01-01")

def get_sp500():
    ticker = yf.Ticker("SPY", session=session)
    return ticker.history(period="1y")

def get_sp500_info():
    ticker = yf.Ticker("SPY", session=session)
    data = ticker.history(period="2d")
    if len(data) >= 2:
        yesterday = data["Close"].iloc[-2]
        today = data["Close"].iloc[-1]
        change = ((today - yesterday) / yesterday) * 100
        return round(today, 2), round(change, 2)
    return 0, 0

def get_bitcoin():
    ticker = yf.Ticker("BTC-USD", session=session)
    return ticker.history(period="30d")

def get_ethereum():
    ticker = yf.Ticker("ETH-USD", session=session)
    return ticker.history(period="30d")

def get_crypto_info(symbol):
    ticker = yf.Ticker(symbol, session=session)
    data = ticker.history(period="2d")
    if len(data) >= 2:
        yesterday = data["Close"].iloc[-2]
        today = data["Close"].iloc[-1]
        change = ((today - yesterday) / yesterday) * 100
        return round(today, 2), round(change, 2)
    return 0, 0
