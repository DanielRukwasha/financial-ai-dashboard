# financial-ai-dashboard
Real-Time Financial dashboard wih AI-powered markel analysis
# Financial AI Dashboard

> Real-time financial dashboard with AI-powered market analysis

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Groq AI](https://img.shields.io/badge/Groq-AI-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## Live Demo
**[https://daniel-financial-dashboard-ai.streamlit.app](https://daniel-financial-dashboard-ai.streamlit.app)**

---

## What it does

A full-stack financial intelligence app that tracks real-time market data
and generates AI-powered analysis automatically.

| Page | Description |
|------|-------------|
| Market Overview | S&P 500 live prices, KPIs, AI market summary |
| Macro Economics | US Inflation (CPI) and Fed Funds Rate charts |
| ₿ Crypto | Bitcoin and Ethereum 30-day performance |
| Comparator | Multi-asset normalized performance comparison |

---

## AI Feature

Every time the dashboard loads, it automatically generates a market
commentary using **Groq AI (Llama 3.3)** based on live data:
- S&P 500 daily change
- US Inflation (CPI)
- Fed Funds Rate
- Bitcoin and Ethereum daily change

---

## Tech Stack

- **Frontend**: Streamlit
- **Data Sources**: Yahoo Finance (yfinance), FRED API (Federal Reserve)
- **AI**: Groq API — Llama 3.3 70B
- **Charts**: Plotly
- **Data Processing**: Pandas, NumPy
- **Deployment**: Streamlit Cloud

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/DanielRukwasha/financial-ai-dashboard.git
cd financial-ai-dashboard

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your API keys
cp .env.example .env
# Edit .env with your keys

# Run the app
streamlit run app.py
```

---

## API Keys Required

| API | Free Tier | Link |
|-----|-----------|------|
| FRED API | Free | [fred.stlouisfed.org](https://fred.stlouisfed.org) |
| Alpha Vantage | Free | [alphavantage.co](https://alphavantage.co) |
| Groq API | Free | [console.groq.com](https://console.groq.com) |

---

## Project Structure
financial-ai-dashboard/
├── app.py                  # Main Streamlit app
├── data/
│   └── fetchers.py         # Data fetching from APIs
├── ai/
│   └── analyst.py          # Groq AI market analysis
├── charts/
│   └── builder.py          # Plotly chart functions
├── .streamlit/
│   └── config.toml         # Dark theme configuration
└── requirements.txt

---

##  Author

Daniel Rukwasha
CS + Quantitative Economics @ Berea College, Kentucky
[GitHub](https://github.com/DanielRukwasha) · [LinkedIn](https://linkedin.com/in/daniel-rukwasha)

---

*Built as part of a fintech portfolio project targeting Summer 2027 internships.*