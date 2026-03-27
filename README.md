# 📈 Real-Time Streaming Dashboard

A **live data dashboard** simulating stock and crypto price feeds with 4 auto-updating interactive charts — built with **Plotly Dash** and deployed on Render.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Plotly_Dash-2.14+-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Live Demo

> 🔗 **[Open Dashboard on Render →](https://realtime-data-stream.onrender.com)**
>
> ⚠️ Free tier — may take 30–60s to wake up on first request.

## ✨ Features

- **4 live price feeds** — AAPL, GOOGL, MSFT (stocks) + BTC (crypto)
- **Auto-updates every second** via `dcc.Interval` polling
- **4 chart types** — % change line, current price bar, rolling volatility, BTC area chart
- **KPI cards** — live price + % change from session start
- **Dark theme** — consistent Plotly dark styling throughout

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.10+ | Core language |
| Plotly Dash | Dashboard framework + reactive callbacks |
| Plotly | Interactive chart rendering |
| NumPy | Gaussian random walk simulation |
| Pandas | Rolling statistics (volatility) |
| Gunicorn | WSGI server for Render deployment |

## 📦 Getting Started

```bash
git clone https://github.com/ByteMe-UK/realtime-data-stream.git
cd realtime-data-stream

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python app.py
```

Open `http://localhost:8050` — charts update every second automatically.

## 📁 Project Structure

```
realtime-data-stream/
├── app.py              ← Dash app — layout, all 4 chart callbacks
├── stream/
│   └── producer.py     ← Simulated price feeds (random walk, thread-safe)
├── Procfile            ← Render: gunicorn app:server
├── requirements.txt
└── README.md
```

## ⚙️ How It Works

```
dcc.Interval (every 1000ms)
    └─▶ trigger callback
            └─▶ tick() — advance all 4 prices by one Gaussian step
            └─▶ get_history() — return last 120 price points per ticker
            └─▶ rebuild all 4 figures + 4 KPI cards
            └─▶ Dash sends JSON diff to browser
            └─▶ browser re-renders charts in-place (no full page reload)
```

## 🚢 Deployment (Render)

1. Push to GitHub
2. [render.com](https://render.com) → New Web Service → connect repo
3. Start command: `gunicorn app:server --bind 0.0.0.0:$PORT`
4. Deploy

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Part of the [ByteMe-UK](https://github.com/ByteMe-UK) portfolio collection.**
