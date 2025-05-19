import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from data_quality import check_stock_data
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Stock Data Quality", layout="wide")
st.title("📈 Real-Time Stock Data Quality Dashboard")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="auto_refresh")

# Sidebar stock selection
symbols = st.sidebar.multiselect(
    "Choose stocks to monitor:",
    ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"],
    default=["AAPL", "TSLA"]
)

# CSV Log File
LOG_FILE = "quality_log.csv"

# Function to color-code rows
def color_status(val):
    if "✅" in val:
        return "background-color: #d4edda"  # Light green
    elif "❌" in val:
        return "background-color: #f8d7da"  # Light red
    elif "⚠️" in val:
        return "background-color: #fff3cd"  # Light yellow
    else:
        return ""

# Check current stock data
results = []
for symbol in symbols:
    result = check_stock_data(symbol)
    results.append(result)

df = pd.DataFrame(results)

# Show latest quality check (visibly styled)
st.subheader("🧪 Latest Quality Check")
styled_df = df.style.applymap(color_status, subset=["status"])
st.dataframe(styled_df, use_container_width=True)

# Append to historical log
now = datetime.now()
log_df = pd.DataFrame(results)
log_df["checked_at"] = now.strftime("%Y-%m-%d %H:%M:%S")

# Load and append to log file
try:
    old_log = pd.read_csv(LOG_FILE)
except FileNotFoundError:
    old_log = pd.DataFrame()

log_all = pd.concat([old_log, log_df], ignore_index=True)
log_all.to_csv(LOG_FILE, index=False)

# Historical Quality Summary
st.subheader("📊 Quality Summary Over Time")

for symbol in symbols:
    st.markdown(f"### 📌 {symbol}")

    # Filter historical data
    df_hist = log_all[log_all["symbol"] == symbol]
    total = len(df_hist)
    valid = len(df_hist[df_hist["status"] == "✅ OK"])

    percent_valid = (valid / total * 100) if total > 0 else 0
    st.markdown(f"<b>✅ Valid Data: {percent_valid:.2f}%</b>", unsafe_allow_html=True)

    # Quality chart
    recent = df_hist.tail(50)  # Last 50 records
    fig, ax = plt.subplots(figsize=(8, 3))
    sns.lineplot(data=recent, x="checked_at", y=recent["status"].apply(lambda x: 1 if x == "✅ OK" else 0), ax=ax)
    ax.set_title("Data Quality Over Time")
    ax.set_ylabel("Valid (1=OK, 0=Issue)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

# Manual Refresh
if st.button("🔄 Refresh Now"):
    st.rerun()

st.caption("⏱️ Auto-refreshes every 60 seconds. Manual refresh available.")