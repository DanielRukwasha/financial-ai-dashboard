import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Couleurs du thème
COLORS = {
    "primary":    "#0070C0",
    "success":    "#10B981",
    "warning":    "#F59E0B",
    "danger":     "#EF4444",
    "background": "#0E1117",
    "card":       "#1A1F2E",
}

def make_line_chart(data, title, color=None, y_label=""):
    """Graphique ligne générique pour séries temporelles"""
    if color is None:
        color = COLORS["primary"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data.values,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=color.replace(")", ", 0.1)").replace("rgb", "rgba"),
    ))

    fig.update_layout(
        title=title,
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["card"],
        font=dict(color="white"),
        xaxis=dict(showgrid=False, color="white"),
        yaxis=dict(showgrid=True, gridcolor="#2D3748",
                   color="white", title=y_label),
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified",
    )
    return fig

def make_candlestick(data, title):
    """Graphique chandelier pour le S&P 500"""
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        increasing_line_color=COLORS["success"],
        decreasing_line_color=COLORS["danger"],
    )])

    fig.update_layout(
        title=title,
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["card"],
        font=dict(color="white"),
        xaxis=dict(showgrid=False, color="white",
                   rangeslider=dict(visible=False)),
        yaxis=dict(showgrid=True, gridcolor="#2D3748", color="white"),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig

def make_multi_line(dataframes, labels, title):
    """Graphique multi-lignes pour comparer plusieurs actifs"""
    fig = go.Figure()
    palette = [COLORS["primary"], COLORS["warning"],
               COLORS["success"], COLORS["danger"]]

    for i, (df, label) in enumerate(zip(dataframes, labels)):
        # Normaliser à 100 pour comparaison équitable
        normalized = (df["Close"] / df["Close"].iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=df.index,
            y=normalized,
            mode="lines",
            name=label,
            line=dict(color=palette[i % len(palette)], width=2),
        ))

    fig.update_layout(
        title=title,
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["card"],
        font=dict(color="white"),
        xaxis=dict(showgrid=False, color="white"),
        yaxis=dict(showgrid=True, gridcolor="#2D3748",
                   color="white", title="Performance (base 100)"),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor=COLORS["card"], bordercolor="#2D3748"),
        hovermode="x unified",
    )
    return fig