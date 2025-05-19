import yfinance as yf
from datetime import datetime, timezone
import pandas as pd

def check_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        latest = data.tail(1)

        if latest.empty:
            return {
                "symbol": symbol,
                "status": "⚠️ No Data",
                "price": "-",
                "timestamp": "-",
                "details": "No latest data"
            }

        price = latest["Close"].values[0]
        timestamp = latest.index[-1]
        volume = latest["Volume"].values[0]

        now = datetime.now(timezone.utc)
        time_diff = (now - timestamp).total_seconds()

        status_list = []

        # Check for missing price
        if pd.isna(price):
            status_list.append("❌ Missing Price")
        elif price == 0:
            status_list.append("❌ Price is Zero")

        # Check for outdated timestamp
        if time_diff > 180:
            status_list.append("⚠️ Outdated Timestamp")

        # Volume check
        if volume == 0:
            status_list.append("⚠️ Zero Volume")
        elif volume < 100:  # Adjust based on symbol type
            status_list.append("⚠️ Low Volume")

        # Sudden price spike check
        if len(data) >= 2:
            prev_price = data["Close"].iloc[-2]
            if prev_price > 0:
                pct_change = ((price - prev_price) / prev_price) * 100
                if abs(pct_change) > 5:
                    status_list.append(f"⚠️ Sudden Price Change ({pct_change:.2f}%)")

        # Missing intervals check (last 10 minutes)
        recent_data = data.last("10min")
        expected_intervals = 10
        actual_intervals = len(recent_data)
        if actual_intervals < expected_intervals:
            missing = expected_intervals - actual_intervals
            status_list.append(f"⚠️ Missing {missing} Intervals in 10 min")

        # Final status
        status = "✅ OK" if not status_list else ", ".join(status_list)

        return {
            "symbol": symbol,
            "status": status,
            "price": f"${price:.2f}",
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "details": "; ".join(status_list) if status_list else "All checks passed"
        }

    except Exception as e:
        return {
            "symbol": symbol,
            "status": "❌ Error",
            "price": "-",
            "timestamp": "-",
            "details": str(e)
        }   