import streamlit as st
from data.fetchers import (
    get_sp500, get_sp500_info,
    get_inflation, get_fed_rate,
    get_bitcoin, get_ethereum,
    get_crypto_info
)
from charts.builder import (
    make_line_chart,
    make_candlestick,
    make_multi_line
)
from ai.analyst import generate_market_summary

st.set_page_config(
    page_title="Financial AI Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("📈 Financial AI")
    st.caption("Real-time market dashboard")
    st.divider()
    st.markdown("**Navigation**")
    page = st.radio(
        "",
        ["🏠 Market Overview",
         "🏦 Macro Economics",
         "₿ Crypto",
         "📊 Comparator"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Data: Yahoo Finance · FRED API")
    st.caption("Built by Daniel Rukwasha")

@st.cache_data(ttl=3600)
def load_sp500():
    return get_sp500()

@st.cache_data(ttl=3600)
def load_inflation():
    return get_inflation()

@st.cache_data(ttl=3600)
def load_fed_rate():
    return get_fed_rate()

@st.cache_data(ttl=3600)
def load_bitcoin():
    return get_bitcoin()

@st.cache_data(ttl=3600)
def load_ethereum():
    return get_ethereum()

if page == "🏠 Market Overview":
    st.title("🏠 Market Overview")
    st.caption("S&P 500 — Live data from Yahoo Finance")

    sp500_price, sp500_change = get_sp500_info()
    btc_price, btc_change = get_crypto_info("BTC-USD")
    eth_price, eth_change = get_crypto_info("ETH-USD")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("S&P 500 (SPY)", f"${sp500_price}", f"{sp500_change}%")
    with col2:
        st.metric("Bitcoin", f"${btc_price:,}", f"{btc_change}%")
    with col3:
        st.metric("Ethereum", f"${eth_price:,}", f"{eth_change}%")

    st.divider()

    with st.expander("🤖 AI Market Analysis", expanded=True):
        with st.spinner("Generating AI analysis..."):
            fed = load_fed_rate()
            inf = load_inflation()
            summary = generate_market_summary(
                sp500_change,
                inf.iloc[-1],
                fed.iloc[-1],
                btc_change,
                eth_change
            )
            st.info(summary)

    st.divider()

    with st.spinner("Loading S&P 500 data..."):
        sp500_data = load_sp500()
        fig = make_candlestick(sp500_data, "S&P 500 — Last 12 months")
        st.plotly_chart(fig, use_container_width=True)

elif page == "🏦 Macro Economics":
    st.title("🏦 Macro Economics")
    st.caption("US Inflation & Fed Rate — Data from FRED API")

    col1, col2 = st.columns(2)
    with col1:
        with st.spinner("Loading inflation data..."):
            inflation = load_inflation()
            fig = make_line_chart(
                inflation,
                "US Inflation (CPI)",
                color="#EF4444",
                y_label="CPI Index"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        with st.spinner("Loading Fed rate data..."):
            fed_rate = load_fed_rate()
            fig = make_line_chart(
                fed_rate,
                "Fed Funds Rate (%)",
                color="#F59E0B",
                y_label="Rate %"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Latest Values")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latest CPI", f"{inflation.iloc[-1]:.1f}")
    with col2:
        st.metric("Fed Rate", f"{fed_rate.iloc[-1]:.2f}%")

elif page == "₿ Crypto":
    st.title("₿ Crypto")
    st.caption("Bitcoin & Ethereum — Last 30 days")

    btc_price, btc_change = get_crypto_info("BTC-USD")
    eth_price, eth_change = get_crypto_info("ETH-USD")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Bitcoin (BTC)", f"${btc_price:,}", f"{btc_change}%")
    with col2:
        st.metric("Ethereum (ETH)", f"${eth_price:,}", f"{eth_change}%")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.spinner("Loading Bitcoin data..."):
            btc_data = load_bitcoin()
            fig = make_line_chart(
                btc_data["Close"],
                "Bitcoin — 30 days",
                color="#F59E0B",
                y_label="Price USD"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        with st.spinner("Loading Ethereum data..."):
            eth_data = load_ethereum()
            fig = make_line_chart(
                eth_data["Close"],
                "Ethereum — 30 days",
                color="#0070C0",
                y_label="Price USD"
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Comparator":
    st.title("📊 Multi-Asset Comparator")
    st.caption("Compare performance across assets (normalized to 100)")

    with st.spinner("Loading data..."):
        sp500_data = load_sp500()
        btc_data = load_bitcoin()
        eth_data = load_ethereum()
        fig = make_multi_line(
            [sp500_data, btc_data, eth_data],
            ["S&P 500", "Bitcoin", "Ethereum"],
            "Asset Performance Comparison (Base 100)"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.info("📌 All assets normalized to 100 at start date for fair comparison.")