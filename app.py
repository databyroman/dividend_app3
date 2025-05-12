# app.py
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Dividend-Reinvested Growth",
                   layout="centered")

st.title("📈  Total-Return Calculator (Price + Reinvested Dividends)")

# --- user inputs -----------------------------------------------------------
symbol   = st.text_input("Stock symbol", value="AAPL")
initial  = st.number_input("Initial investment (USD)", min_value=1.0, value=1000.0, step=100.0)

# choose either a fixed year range or “max” history with a slider
years_back = st.slider("Look-back period (years)", 1, 40, 10)

# button avoids expensive API calls on every keystroke
if st.button("Calculate"):
    # -----------------------------------------------------------------------
    # 1. Pull price history and dividend history with yfinance
    # -----------------------------------------------------------------------
    ticker = yf.Ticker(symbol)
    end    = pd.Timestamp.today().normalize()
    start  = end - pd.DateOffset(years=years_back)

    hist   = ticker.history(start=start, end=end, actions=True)   # includes 'Dividends'
    if hist.empty:
        st.error("No data returned. Check the symbol or date range.")
        st.stop()

    # -----------------------------------------------------------------------
    # 2. Simulate dividend-reinvestment
    # -----------------------------------------------------------------------
    # shares purchased on day 0
    first_price = hist["Close"].iloc[0]
    shares      = initial / first_price
    portfolio_value = []

    for date, row in hist.iterrows():
        # reinvest cash dividends *that arrive on this date* at close price
        if row["Dividends"] > 0:
            cash        = shares * row["Dividends"]
            extra_sh    = cash / row["Close"]
            shares     += extra_sh
        # record total value each day
        portfolio_value.append(shares * row["Close"])

    hist["Total Value"] = portfolio_value

    # -----------------------------------------------------------------------
    # 3. Display results
    # -----------------------------------------------------------------------
    final_val = hist["Total Value"].iloc[-1]
    absolute  = final_val - initial
    percent   = (final_val / initial - 1) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Final value",      f"${final_val:,.2f}")
    col2.metric("Gain / loss",      f"${absolute:,.2f}")
    col3.metric("Total return",     f"{percent:,.2f}%")

    st.subheader("Growth curve")
    st.line_chart(hist[["Total Value"]])

    with st.expander("Raw data"):
        st.dataframe(hist[["Close", "Dividends", "Total Value"]].assign(
            Close=lambda x: x["Close"].round(2),
            Dividends=lambda x: x["Dividends"].round(2),
            **{"Total Value": lambda x: x["Total Value"].round(2)}
        ))

# ---------------------------------------------------------------------------
# 4. Installation / launch notes (once per machine)
# ---------------------------------------------------------------------------
# $ python -m venv .venv
# $ .\.venv\Scripts\activate           # or source .venv/bin/activate (mac/Linux)
# $ pip install streamlit yfinance pandas
# $ streamlit run app.py
#Fix app.py content
