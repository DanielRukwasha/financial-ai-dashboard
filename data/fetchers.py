import yfinance as yf
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

def get_secret(key):
    """Lit les clés API depuis st.secrets (cloud) ou .env (local)"""
    try:
        return st.secrets[key]
    except:
        return os.getenv(key)

# ── FRED API ──────────────────────────────────────────────────
def get_fred():
    return Fred(api_key=get_secret("FRED_API_KEY"))

def get_inflation():
    """Retourne l'inflation US (CPI) sur 3 ans"""
    fred = get_fred()
    data = fred.get_series("CPIAUCSL", observation_start="2022-01-01")
    return data

def get_fed_rate():
    """Retourne le taux directeur de la Fed sur 3 ans"""
    fred = get_fred()
    data = fred.get_series("FEDFUNDS", observation_start="2022-01-01")
    return data

# ── MARCHÉ ────────────────────────────────────────────────────
def get_sp500():
    """Retourne le S&P 500 sur 1 an"""
    ticker = yf.Ticker("SPY")
    data = ticker.history(period="1y")
    return data

def get_sp500_info():
    """Retourne la variation du jour du S&P 500"""
    ticker = yf.Ticker("SPY")
    data = ticker.history(period="2d")
    if len(data) >= 2:
        yesterday = data["Close"].iloc[-2]
        today = data["Close"].iloc[-1]
        change = ((today - yesterday) / yesterday) * 100
        return round(today, 2), round(change, 2)
    return 0, 0

# ── CRYPTO ────────────────────────────────────────────────────
def get_bitcoin():
    """Retourne Bitcoin sur 30 jours"""
    ticker = yf.Ticker("BTC-USD")
    data = ticker.history(period="30d")
    return data

def get_ethereum():
    """Retourne Ethereum sur 30 jours"""
    ticker = yf.Ticker("ETH-USD")
    data = ticker.history(period="30d")
    return data

def get_crypto_info(symbol):
    """Retourne prix et variation du jour pour une crypto"""
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="2d")
    if len(data) >= 2:
        yesterday = data["Close"].iloc[-2]
        today = data["Close"].iloc[-1]
        change = ((today - yesterday) / yesterday) * 100
        return round(today, 2), round(change, 2)
    return 0, 0