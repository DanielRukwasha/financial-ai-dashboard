from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_market_summary(sp500_change, inflation, fed_rate, btc_change, eth_change):
    """Génère un résumé IA des conditions du marché"""

    prompt = f"""You are a senior financial analyst. Based on the following real-time market data, 
write a concise market summary in 3 sentences maximum. Be factual, professional, and insightful.

Current Market Data:
- S&P 500 today: {sp500_change:+.2f}%
- US Inflation (CPI latest): {inflation:.1f}
- Fed Funds Rate: {fed_rate:.2f}%
- Bitcoin today: {btc_change:+.2f}%
- Ethereum today: {eth_change:+.2f}%

Write a brief market commentary focusing on the most significant observations."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    return response.choices[0].message.content

def generate_asset_analysis(ticker, price, change, period_high, period_low):
    """Génère une analyse courte pour un actif spécifique"""

    prompt = f"""You are a financial analyst. In 2 sentences maximum, give a brief technical 
commentary on this asset:

Asset: {ticker}
Current Price: ${price:,.2f}
Today's Change: {change:+.2f}%
30-day High: ${period_high:,.2f}
30-day Low: ${period_low:,.2f}

Be concise and factual."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7,
    )

    return response.choices[0].message.content