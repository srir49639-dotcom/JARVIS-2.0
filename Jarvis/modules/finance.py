# ============================================================
# JARVIS - Finance Module (Stocks & Crypto)
# ============================================================

import requests

class FinanceModule:
    """Fetches live stock and crypto prices."""

    @staticmethod
    def get_crypto_price(coin):
        """Fetch cryptocurrency price using CoinGecko API."""
        coin = coin.lower().strip()
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
            r = requests.get(url, timeout=5).json()
            if coin in r:
                price = r[coin]['usd']
                return True, f"The current price of {coin} is ${price}, sir."
            return False, f"Could not find cryptocurrency {coin}, sir."
        except Exception as e:
            return False, f"Error fetching crypto price: {e}"

    @staticmethod
    def get_stock_price(ticker):
        """Fetch stock price using yfinance."""
        ticker = ticker.upper().strip()
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            history = stock.history(period="1d")
            if not history.empty:
                price = history["Close"].iloc[-1]
                return True, f"The current stock price for {ticker} is ${price:.2f}, sir."
            return False, f"Could not find stock data for {ticker}, sir."
        except ImportError:
            return False, "yfinance library not installed, sir. Run pip install yfinance."
        except Exception as e:
            return False, f"Error fetching stock price: {e}"
