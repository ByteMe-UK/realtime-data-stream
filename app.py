"""
Real-Time Data Streaming Dashboard — Plotly Dash

Simulates live stock/crypto price feeds with auto-updating charts.
Uses Dash's dcc.Interval component for client-side polling (no WebSockets needed).

Run locally:   python app.py
Deploy:        Render (Procfile included)
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px

from stream.producer import initialise, tick, get_history, get_current_prices

# Seed with 60 initial data points
initialise()

TICKERS = ["AAPL", "GOOGL", "MSFT", "BTC"]
COLORS = {
    "AAPL":  "#6C63FF",
    "GOOGL": "#00C9A7",
    "MSFT":  "#FFD93D",
    "BTC":   "#FF6584",
}

DARK_BG    = "#0E1117"
CARD_BG    = "#1A1F2E"
BORDER     = "#2D3748"
TEXT_COLOR = "#FAFAFA"
MUTED      = "#888"


def kpi_card(ticker: str, price: float, change_pct: float) -> html.Div:
    arrow = "▲" if change_pct >= 0 else "▼"
    color = "#00C9A7" if change_pct >= 0 else "#FF6584"
    prefix = "$" if ticker != "BTC" else "$"
    return html.Div([
        html.P(ticker, style={"color": MUTED, "fontSize": "13px", "margin": "0"}),
        html.H3(f"{prefix}{price:,.2f}", style={"color": TEXT_COLOR, "margin": "4px 0"}),
        html.P(f"{arrow} {abs(change_pct):.2f}%", style={"color": color, "fontSize": "13px", "margin": "0"}),
    ], style={
        "background": CARD_BG, "border": f"1px solid {BORDER}",
        "borderRadius": "10px", "padding": "16px 20px",
        "flex": "1", "minWidth": "140px",
    })


app = dash.Dash(
    __name__,
    title="Real-Time Data Stream",
    update_title=None,
)
server = app.server  # expose for Render/gunicorn

app.layout = html.Div([
    # ── Header ──────────────────────────────────────────────
    html.Div([
        html.H1("📈 Real-Time Data Stream", style={"color": TEXT_COLOR, "margin": "0"}),
        html.P("Live simulated stock & crypto prices — updates every second",
               style={"color": MUTED, "margin": "4px 0 0"}),
    ], style={"padding": "24px 32px 16px"}),

    # ── KPI cards ───────────────────────────────────────────
    html.Div(id="kpi-cards", style={
        "display": "flex", "gap": "12px", "padding": "0 32px 20px", "flexWrap": "wrap",
    }),

    # ── Charts row ──────────────────────────────────────────
    html.Div([
        html.Div([
            dcc.Graph(id="line-chart", config={"displayModeBar": False}),
        ], style={"flex": "2", "minWidth": "400px"}),

        html.Div([
            dcc.Graph(id="bar-chart", config={"displayModeBar": False}),
        ], style={"flex": "1", "minWidth": "280px"}),
    ], style={"display": "flex", "gap": "16px", "padding": "0 32px 16px", "flexWrap": "wrap"}),

    # ── Second row ──────────────────────────────────────────
    html.Div([
        html.Div([
            dcc.Graph(id="volatility-chart", config={"displayModeBar": False}),
        ], style={"flex": "1", "minWidth": "300px"}),

        html.Div([
            dcc.Graph(id="ohlc-chart", config={"displayModeBar": False}),
        ], style={"flex": "1", "minWidth": "300px"}),
    ], style={"display": "flex", "gap": "16px", "padding": "0 32px 24px", "flexWrap": "wrap"}),

    # ── Footer ──────────────────────────────────────────────
    html.Div("⚠️ Simulated data only — not financial advice",
             style={"textAlign": "center", "color": MUTED, "fontSize": "12px", "paddingBottom": "20px"}),

    # Interval — triggers update every 1 second
    dcc.Interval(id="interval", interval=1000, n_intervals=0),

], style={"background": DARK_BG, "minHeight": "100vh", "fontFamily": "Inter, sans-serif"})


LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_COLOR, family="Inter, sans-serif", size=12),
    margin=dict(l=40, r=20, t=40, b=30),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
    xaxis=dict(gridcolor=BORDER, showgrid=True),
    yaxis=dict(gridcolor=BORDER, showgrid=True),
)


@callback(
    Output("kpi-cards",        "children"),
    Output("line-chart",       "figure"),
    Output("bar-chart",        "figure"),
    Output("volatility-chart", "figure"),
    Output("ohlc-chart",       "figure"),
    Input("interval",          "n_intervals"),
)
def update_all(n: int):
    tick()  # advance all tickers by one step

    history = get_history()
    prices  = get_current_prices()

    # ── KPI cards ─────────────────────────────────────────
    cards = []
    for t in TICKERS:
        df = history.get(t)
        if df is not None and len(df) >= 2:
            first = df["price"].iloc[0]
            last  = df["price"].iloc[-1]
            chg   = (last - first) / first * 100
        else:
            last, chg = prices.get(t, 0), 0.0
        cards.append(kpi_card(t, last, chg))

    # ── Line chart — price over time ───────────────────────
    fig_line = go.Figure()
    for t in TICKERS:
        df = history.get(t)
        if df is not None and not df.empty:
            # Normalise to % change from first point for fair comparison
            base = df["price"].iloc[0]
            fig_line.add_trace(go.Scatter(
                x=df["time"], y=(df["price"] / base - 1) * 100,
                name=t, line=dict(color=COLORS[t], width=2),
                hovertemplate=f"{t}: %{{y:.2f}}%<extra></extra>",
            ))
    fig_line.update_layout(title="Price Change (%)", yaxis_ticksuffix="%", **LAYOUT)

    # ── Bar chart — current prices ─────────────────────────
    tickers_display = ["AAPL", "GOOGL", "MSFT"]  # exclude BTC (different scale)
    fig_bar = go.Figure(go.Bar(
        x=tickers_display,
        y=[prices.get(t, 0) for t in tickers_display],
        marker_color=[COLORS[t] for t in tickers_display],
        hovertemplate="%{x}: $%{y:,.2f}<extra></extra>",
    ))
    fig_bar.update_layout(title="Current Prices (USD)", showlegend=False,
                          yaxis_tickprefix="$", **LAYOUT)

    # ── Volatility chart — rolling std ────────────────────
    fig_vol = go.Figure()
    for t in TICKERS:
        df = history.get(t)
        if df is not None and len(df) >= 10:
            vol = df["price"].pct_change().rolling(10).std() * 100
            fig_vol.add_trace(go.Scatter(
                x=df["time"], y=vol, name=t,
                fill="tozeroy", line=dict(color=COLORS[t], width=1.5),
                hovertemplate=f"{t}: %{{y:.3f}}%<extra></extra>",
            ))
    fig_vol.update_layout(title="Rolling Volatility (10-tick std)", yaxis_ticksuffix="%", **LAYOUT)

    # ── BTC candlestick-style area chart ──────────────────
    fig_ohlc = go.Figure()
    df_btc = history.get("BTC")
    if df_btc is not None and not df_btc.empty:
        fig_ohlc.add_trace(go.Scatter(
            x=df_btc["time"], y=df_btc["price"],
            fill="tozeroy", line=dict(color=COLORS["BTC"], width=2),
            hovertemplate="BTC: $%{y:,.0f}<extra></extra>",
        ))
    fig_ohlc.update_layout(title="BTC/USD", yaxis_tickprefix="$", **LAYOUT)

    return cards, fig_line, fig_bar, fig_vol, fig_ohlc


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
