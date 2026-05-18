"""
valuation.py — Fundamental Valuation Module
Financial AI Dashboard | Daniel Rukwasha
─────────────────────────────────────────
Provides:
  • Multiples screen  : P/E, Forward P/E, EV/EBITDA, P/S, P/B
  • DCF valuation     : intrinsic value from FCF with adjustable assumptions
  • Peer comparison   : side-by-side multiples for a default watchlist

Usage: called from app.py as   from valuation import render_valuation_page
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ── Default watchlist ──────────────────────────────────────────────────────
DEFAULT_WATCHLIST = {
    "KO":   "Coca-Cola",
    "PEP":  "PepsiCo",
    "MNST": "Monster Beverage",
    "KDP":  "Keurig Dr Pepper",
    "CELH": "Celsius Holdings",
}

# ── Fetch helpers ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_info(ticker: str) -> dict:
    """Pull all fundamental data for one ticker. Cached 1 hour."""
    try:
        t = yf.Ticker(ticker.upper().strip())
        info = t.info
        # Pull trailing FCF history for DCF
        cf = t.cashflow
        fcf_series = None
        if cf is not None and not cf.empty:
            try:
                op  = cf.loc["Operating Cash Flow"]  if "Operating Cash Flow"  in cf.index else None
                cap = cf.loc["Capital Expenditure"]   if "Capital Expenditure"   in cf.index else None
                if op is not None and cap is not None:
                    fcf_series = (op + cap).dropna()   # capex is negative in yf
            except Exception:
                pass
        return {"info": info, "fcf_series": fcf_series, "error": None}
    except Exception as e:
        return {"info": {}, "fcf_series": None, "error": str(e)}


def safe_get(info: dict, key: str, fallback=None):
    v = info.get(key, fallback)
    return v if v not in (None, "N/A", "Infinity", float("inf")) else fallback


def fmt_num(val, prefix="", suffix="", decimals=2, billions=False):
    if val is None:
        return "N/A"
    if billions:
        val = val / 1e9
        suffix = "B" + suffix
    return f"{prefix}{val:,.{decimals}f}{suffix}"


def fmt_mult(val, decimals=1):
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}x"


def fmt_pct(val, decimals=1):
    if val is None:
        return "N/A"
    return f"{val*100:.{decimals}f}%"


# ── DCF calculator ─────────────────────────────────────────────────────────
def run_dcf(base_fcf: float, growth_r1: float, growth_r2: float,
            terminal_g: float, wacc: float, years_r1: int,
            shares: float) -> dict:
    """
    Two-stage DCF.
      Stage 1 : years_r1 years at growth_r1
      Stage 2 : remaining (10 - years_r1) years at growth_r2
      Terminal : Gordon growth model at terminal_g
    Returns dict with intrinsic_value_per_share and yearly cash flows.
    """
    total_years = 10
    fcf = base_fcf
    pv_flows = []
    yearly   = []

    for yr in range(1, total_years + 1):
        g   = growth_r1 if yr <= years_r1 else growth_r2
        fcf = fcf * (1 + g)
        pv  = fcf / (1 + wacc) ** yr
        pv_flows.append(pv)
        yearly.append({"Year": f"Yr {yr}", "FCF ($B)": fcf / 1e9,
                        "PV ($B)": pv / 1e9,
                        "Growth": g,
                        "Stage": "High Growth" if yr <= years_r1 else "Fade"})

    terminal_value = (fcf * (1 + terminal_g)) / (wacc - terminal_g)
    pv_terminal    = terminal_value / (1 + wacc) ** total_years

    total_pv       = sum(pv_flows) + pv_terminal
    intrinsic      = total_pv / shares if shares else None

    return {
        "intrinsic_per_share": intrinsic,
        "pv_fcf":              sum(pv_flows),
        "pv_terminal":         pv_terminal,
        "total_pv":            total_pv,
        "terminal_value":      terminal_value,
        "yearly":              yearly,
    }


# ── Peer comparison table ──────────────────────────────────────────────────
def build_peer_table(tickers: dict) -> pd.DataFrame:
    rows = []
    for ticker, name in tickers.items():
        d    = fetch_info(ticker)
        info = d["info"]
        rows.append({
            "Ticker":        ticker,
            "Company":       name,
            "Price":         safe_get(info, "currentPrice"),
            "Mkt Cap ($B)":  round(safe_get(info, "marketCap", 0) / 1e9, 1),
            "P/E (TTM)":     safe_get(info, "trailingPE"),
            "Forward P/E":   safe_get(info, "forwardPE"),
            "EV/EBITDA":     safe_get(info, "enterpriseToEbitda"),
            "P/S":           safe_get(info, "priceToSalesTrailingTwelveMonths"),
            "P/B":           safe_get(info, "priceToBook"),
            "Rev Growth":    safe_get(info, "revenueGrowth"),
            "Net Margin":    safe_get(info, "profitMargins"),
        })
    return pd.DataFrame(rows)


# ── Main render function ───────────────────────────────────────────────────
def render_valuation_page():
    st.title("📊 Fundamental Valuation")
    st.caption("Multiples screen · DCF intrinsic value · Peer comparison")

    # ── Ticker input ──
    col_in, col_btn = st.columns([3, 1])
    with col_in:
        raw_ticker = st.text_input(
            "Search any ticker",
            value="KO",
            placeholder="e.g. AAPL, MSFT, KO",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("Analyse", use_container_width=True)

    ticker = raw_ticker.upper().strip()

    # ── Tabs ──
    tab1, tab2, tab3 = st.tabs(["📋 Multiples", "💰 DCF Model", "🔭 Peer Comparison"])

    # ════════════════════════════════════════════════════════════
    # TAB 1 — MULTIPLES SCREEN
    # ════════════════════════════════════════════════════════════
    with tab1:
        with st.spinner(f"Fetching {ticker} fundamentals…"):
            d    = fetch_info(ticker)
            info = d["info"]
            err  = d["error"]

        if err:
            st.error(f"Could not fetch data for **{ticker}**: {err}")
            st.stop()

        name    = safe_get(info, "longName", ticker)
        price   = safe_get(info, "currentPrice")
        mktcap  = safe_get(info, "marketCap")
        ev      = safe_get(info, "enterpriseValue")
        sector  = safe_get(info, "sector", "—")
        summary = safe_get(info, "longBusinessSummary", "")

        st.subheader(f"{name}  ({ticker})")
        st.caption(f"{sector}  ·  As of {datetime.today().strftime('%B %d, %Y')}")

        # Key price metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price",        fmt_num(price, prefix="$"))
        m2.metric("Market Cap",   fmt_num(mktcap, prefix="$", billions=True))
        m3.metric("Enterprise Value", fmt_num(ev, prefix="$", billions=True))
        m4.metric("52-Wk High",   fmt_num(safe_get(info, "fiftyTwoWeekHigh"), prefix="$"))

        st.divider()

        # Multiples table
        st.markdown("#### Valuation Multiples")
        multiples = {
            "P/E (TTM)":          (safe_get(info, "trailingPE"),                    "Trailing earnings multiple"),
            "Forward P/E":        (safe_get(info, "forwardPE"),                     "Based on next-year EPS estimate"),
            "EV / EBITDA":        (safe_get(info, "enterpriseToEbitda"),            "Enterprise value to EBITDA"),
            "Price / Sales":      (safe_get(info, "priceToSalesTrailingTwelveMonths"), "Revenue multiple"),
            "Price / Book":       (safe_get(info, "priceToBook"),                   "Book value multiple"),
            "PEG Ratio":          (safe_get(info, "pegRatio"),                      "P/E relative to growth rate"),
        }

        mult_col1, mult_col2 = st.columns(2)
        items = list(multiples.items())
        for i, (label, (val, desc)) in enumerate(items):
            col = mult_col1 if i < 3 else mult_col2
            with col:
                st.metric(label, fmt_mult(val) if val else "N/A", help=desc)

        st.divider()

        # Profitability
        st.markdown("#### Profitability & Growth")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Revenue Growth",  fmt_pct(safe_get(info, "revenueGrowth")))
        p2.metric("Gross Margin",    fmt_pct(safe_get(info, "grossMargins")))
        p3.metric("Operating Margin",fmt_pct(safe_get(info, "operatingMargins")))
        p4.metric("Net Margin",      fmt_pct(safe_get(info, "profitMargins")))

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("ROE",             fmt_pct(safe_get(info, "returnOnEquity")))
        r2.metric("ROA",             fmt_pct(safe_get(info, "returnOnAssets")))
        r3.metric("Debt / Equity",   fmt_mult(safe_get(info, "debtToEquity"), decimals=2) if safe_get(info, "debtToEquity") else "N/A")
        r4.metric("Current Ratio",   fmt_mult(safe_get(info, "currentRatio"), decimals=2) if safe_get(info, "currentRatio") else "N/A")

        if summary:
            with st.expander("Business description"):
                st.write(summary[:800] + "…" if len(summary) > 800 else summary)

    # ════════════════════════════════════════════════════════════
    # TAB 2 — DCF MODEL
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("#### Two-Stage DCF — Intrinsic Value Estimator")
        st.caption("All assumptions are editable. Model updates instantly.")

        with st.spinner(f"Loading {ticker} cash flow data…"):
            d2       = fetch_info(ticker)
            info2    = d2["info"]
            fcf_ser  = d2["fcf_series"]

        # Base FCF
        ltm_fcf = safe_get(info2, "freeCashflow")
        shares  = safe_get(info2, "sharesOutstanding")
        curr_p  = safe_get(info2, "currentPrice")

        if ltm_fcf is None:
            st.warning("Free cash flow data unavailable for this ticker. Enter manually below.")
            ltm_fcf = 0.0

        st.markdown("**Step 1 — Base Free Cash Flow**")
        base_fcf = st.number_input(
            "LTM Free Cash Flow ($)",
            value=float(ltm_fcf),
            step=1e8,
            format="%.0f",
            help="Last twelve months free cash flow. Pre-filled from yfinance."
        )

        st.markdown("**Step 2 — Growth Assumptions**")
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            years_r1  = st.slider("High-growth years",   min_value=1, max_value=7,  value=5)
            growth_r1 = st.slider("Stage 1 growth rate", min_value=0, max_value=30, value=8) / 100
        with dc2:
            growth_r2 = st.slider("Stage 2 growth rate", min_value=0, max_value=20, value=4) / 100
            terminal_g= st.slider("Terminal growth rate", min_value=0, max_value=5,  value=2) / 100
        with dc3:
            wacc      = st.slider("Discount rate (WACC)", min_value=5, max_value=20, value=9) / 100
            margin_s  = safe_get(info2, "profitMargins")
            st.metric("Net Margin (ref)", fmt_pct(margin_s))

        if wacc <= terminal_g:
            st.error("⚠️ WACC must be greater than terminal growth rate. Adjust the sliders.")
            st.stop()

        if base_fcf == 0:
            st.info("Enter a non-zero base FCF above to compute intrinsic value.")
            st.stop()

        # Run model
        result = run_dcf(
            base_fcf=base_fcf,
            growth_r1=growth_r1,
            growth_r2=growth_r2,
            terminal_g=terminal_g,
            wacc=wacc,
            years_r1=years_r1,
            shares=shares or 1,
        )

        iv   = result["intrinsic_per_share"]
        updn = ((iv - curr_p) / curr_p) if (iv and curr_p) else None

        st.divider()
        st.markdown("**Step 3 — Results**")

        res1, res2, res3, res4 = st.columns(4)
        res1.metric("Intrinsic Value / Share", fmt_num(iv, prefix="$") if iv else "N/A")
        res2.metric("Current Price",           fmt_num(curr_p, prefix="$") if curr_p else "N/A")
        res3.metric("Upside / Downside",       fmt_pct(updn) if updn else "N/A",
                    delta=f"{'Undervalued' if updn and updn > 0 else 'Overvalued'}")
        res4.metric("Terminal Value ($B)",     fmt_num(result["pv_terminal"] / 1e9, prefix="$", decimals=1))

        # Value bridge chart
        bridge_fig = go.Figure(go.Bar(
            x=["PV of FCFs (10 yr)", "PV of Terminal Value", "Total Enterprise Value"],
            y=[result["pv_fcf"] / 1e9, result["pv_terminal"] / 1e9, result["total_pv"] / 1e9],
            marker_color=["#1D9E75", "#185FA5", "#1F3864"],
            text=[f"${v/1e9:.1f}B" for v in
                  [result["pv_fcf"], result["pv_terminal"], result["total_pv"]]],
            textposition="outside",
        ))
        bridge_fig.update_layout(
            title="DCF Value Bridge ($B)",
            yaxis_title="Value ($B)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial"),
            showlegend=False,
        )
        st.plotly_chart(bridge_fig, use_container_width=True)

        # Yearly FCF table
        df_yr = pd.DataFrame(result["yearly"])
        df_yr["FCF ($B)"]  = df_yr["FCF ($B)"].map(lambda x: f"${x:.2f}B")
        df_yr["PV ($B)"]   = df_yr["PV ($B)"].map(lambda x: f"${x:.2f}B")
        df_yr["Growth"]    = df_yr["Growth"].map(lambda x: f"{x*100:.1f}%")
        with st.expander("View yearly cash flow detail"):
            st.dataframe(df_yr[["Year", "Stage", "Growth", "FCF ($B)", "PV ($B)"]],
                         use_container_width=True, hide_index=True)

        # Sensitivity: intrinsic value vs WACC & terminal growth
        st.markdown("**Sensitivity — Intrinsic Value by WACC × Terminal Growth**")
        waccs    = [w/100 for w in range(7, 13)]
        term_gs  = [g/100 for g in range(1, 5)]
        sens_data = []
        for w in waccs:
            row = []
            for tg in term_gs:
                if w > tg:
                    r = run_dcf(base_fcf, growth_r1, growth_r2, tg, w, years_r1, shares or 1)
                    row.append(round(r["intrinsic_per_share"], 2) if r["intrinsic_per_share"] else None)
                else:
                    row.append(None)
            sens_data.append(row)

        df_sens = pd.DataFrame(
            sens_data,
            index=[f"WACC {w*100:.0f}%" for w in waccs],
            columns=[f"TG {tg*100:.0f}%" for tg in term_gs],
        )
        st.dataframe(df_sens.style.format("${:.2f}").background_gradient(cmap="RdYlGn"),
                     use_container_width=True)
        st.caption("Green = higher intrinsic value. Current price shown for reference: "
                   + (fmt_num(curr_p, prefix="$") if curr_p else "N/A"))

    # ════════════════════════════════════════════════════════════
    # TAB 3 — PEER COMPARISON
    # ════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("#### Peer Comparison — Valuation Multiples")

        # Allow user to add tickers to watchlist
        extra = st.text_input("Add tickers to comparison (comma-separated)",
                              placeholder="e.g. AAPL, NVDA")
        watchlist = dict(DEFAULT_WATCHLIST)
        if ticker not in watchlist:
            name_fallback = safe_get(fetch_info(ticker)["info"], "shortName", ticker)
            watchlist[ticker] = name_fallback
        if extra:
            for t in [x.strip().upper() for x in extra.split(",") if x.strip()]:
                watchlist[t] = t

        with st.spinner("Loading peer data…"):
            df_peer = build_peer_table(watchlist)

        # Highlight current ticker row
        def highlight_row(row):
            return ["background-color: #D9E1F2; font-weight: bold"
                    if row["Ticker"] == ticker else "" for _ in row]

        fmt_cols = {
            "Price":        "${:.2f}",
            "Mkt Cap ($B)": "${:.1f}B",
            "P/E (TTM)":    "{:.1f}x",
            "Forward P/E":  "{:.1f}x",
            "EV/EBITDA":    "{:.1f}x",
            "P/S":          "{:.2f}x",
            "P/B":          "{:.2f}x",
            "Rev Growth":   "{:.1%}",
            "Net Margin":   "{:.1%}",
        }
        styled = (df_peer.style
                  .apply(highlight_row, axis=1)
                  .format(fmt_cols, na_rep="N/A"))

        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.divider()

        # Bar chart — P/E comparison
        df_valid = df_peer.dropna(subset=["P/E (TTM)"])
        if not df_valid.empty:
            colors = ["#1F3864" if t == ticker else "#A8B8D0"
                      for t in df_valid["Ticker"]]
            fig_pe = go.Figure(go.Bar(
                x=df_valid["Ticker"],
                y=df_valid["P/E (TTM)"],
                marker_color=colors,
                text=df_valid["P/E (TTM)"].map(lambda x: f"{x:.1f}x"),
                textposition="outside",
            ))
            fig_pe.update_layout(
                title="P/E (TTM) Comparison",
                yaxis_title="P/E Multiple",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Arial"),
                showlegend=False,
            )
            st.plotly_chart(fig_pe, use_container_width=True)

        # Scatter — P/E vs Net Margin (valuation vs quality)
        df_scatter = df_peer.dropna(subset=["P/E (TTM)", "Net Margin"])
        if not df_scatter.empty:
            fig_sc = px.scatter(
                df_scatter,
                x="Net Margin",
                y="P/E (TTM)",
                text="Ticker",
                size="Mkt Cap ($B)",
                color="Ticker",
                title="Valuation vs Quality: P/E vs Net Margin",
                labels={"Net Margin": "Net Margin (%)", "P/E (TTM)": "P/E Multiple"},
            )
            fig_sc.update_traces(textposition="top center")
            fig_sc.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Arial"),
                showlegend=False,
            )
            st.plotly_chart(fig_sc, use_container_width=True)
            st.caption("Bubble size = market cap. "
                       "Upper-right = expensive but high-quality. "
                       "Lower-right = cheap and high-quality (value opportunity).")
