import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import wrds
from io import BytesIO

# -----------------------------
# Page settings
# -----------------------------
st.set_page_config(page_title="Monthly Stock Analysis Tool", layout="wide")

st.title("Monthly Stock Analysis Tool")
st.markdown("This app retrieves monthly stock data from WRDS CSMAR and provides descriptive analysis, visualisations, and exportable results.")

# -----------------------------
# User inputs
# -----------------------------
st.sidebar.header("Input Parameters")
stock_code = st.sidebar.text_input("Enter stock code", value="000001")
start_month = st.sidebar.number_input(
    "Enter start month (YYYYMM)",
    min_value=190001,
    max_value=210012,
    value=202101,
    step=1
)

run_button = st.sidebar.button("Run Analysis")

# -----------------------------
# Excel export helper
# -----------------------------
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Analysis")
    return output.getvalue()

# -----------------------------
# Main analysis
# -----------------------------
if run_button:
    if stock_code.strip() == "":
        st.warning("Please enter a valid stock code.")
        st.stop()

    # Connect to WRDS
    try:
        with st.spinner("Connecting to WRDS..."):
            db = wrds.Connection(wrds_username="xiaoyashi24")
    except Exception as e:
        st.error(f"WRDS connection failed: {e}")
        st.stop()

    # SQL query
    query = f"""
    SELECT stkcd, trdmnt, mclsprc, mretwd, mretnd, mnshrtrd, mnvaltrd
    FROM csmar.trd_mnth
    WHERE stkcd = '{stock_code}'
      AND trdmnt >= {start_month}
    """

    # Execute query
    try:
        with st.spinner("Retrieving data..."):
            df = db.raw_sql(query)
    except Exception as e:
        st.error(f"Query failed: {e}")
        st.stop()

    st.subheader("1. Raw Data Overview")
    st.write("Raw data shape:", df.shape)

    if df.empty:
        st.warning("No data found. Please check the stock code or start month.")
        st.stop()

    # -----------------------------
    # Data cleaning
    # -----------------------------
    df = df[['stkcd', 'trdmnt', 'mclsprc', 'mretwd', 'mretnd', 'mnshrtrd', 'mnvaltrd']].copy()

    # Drop missing key values
    df = df.dropna(subset=['trdmnt', 'mretwd', 'mclsprc'])

    # Convert YYYYMM to datetime
    df['trdmnt'] = pd.to_datetime(df['trdmnt'].astype(str), format='%Y%m', errors='coerce')

    # Remove invalid dates
    df = df.dropna(subset=['trdmnt'])

    # Stop if empty after cleaning
    if df.empty:
        st.warning("Data became empty after cleaning. No valid records available.")
        st.stop()

    # Sort data
    df = df.sort_values('trdmnt').reset_index(drop=True)

    # Create year-month label
    df['year_month'] = df['trdmnt'].dt.strftime('%Y-%m')

    # Derived metrics
    df['cum_return'] = (1 + df['mretwd']).cumprod() - 1
    df['price_change'] = df['mclsprc'].diff()

    st.write("Cleaned data shape:", df.shape)
    st.dataframe(df.head(10), use_container_width=True)

    # -----------------------------
    # Summary statistics
    # -----------------------------
    mean_return = df['mretwd'].mean()
    std_return = df['mretwd'].std()
    max_return = df['mretwd'].max()
    min_return = df['mretwd'].min()

    mean_price = df['mclsprc'].mean()
    std_price = df['mclsprc'].std()
    max_price = df['mclsprc'].max()
    min_price = df['mclsprc'].min()

    valid_return_df = df.dropna(subset=['mretwd'])

    if valid_return_df.empty:
        st.warning("No valid return data available.")
        st.stop()

    best_month = valid_return_df.loc[valid_return_df['mretwd'].idxmax()]
    worst_month = valid_return_df.loc[valid_return_df['mretwd'].idxmin()]

    st.subheader("2. Summary Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Return Statistics")
        st.write(f"**Average monthly return:** {mean_return:.4f}")
        st.write(f"**Return volatility (std):** {std_return:.4f}")
        st.write(f"**Highest monthly return:** {max_return:.4f}")
        st.write(f"**Lowest monthly return:** {min_return:.4f}")

    with col2:
        st.markdown("### Price Statistics")
        st.write(f"**Average monthly closing price:** {mean_price:.2f}")
        st.write(f"**Price volatility (std):** {std_price:.2f}")
        st.write(f"**Highest monthly closing price:** {max_price:.2f}")
        st.write(f"**Lowest monthly closing price:** {min_price:.2f}")

    st.markdown("### Best and Worst Month")
    c1, c2 = st.columns(2)

    with c1:
        st.success(
            f"Best month: **{best_month['trdmnt'].strftime('%Y-%m')}**  \n"
            f"Monthly return: **{best_month['mretwd']:.4f}**"
        )

    with c2:
        st.error(
            f"Worst month: **{worst_month['trdmnt'].strftime('%Y-%m')}**  \n"
            f"Monthly return: **{worst_month['mretwd']:.4f}**"
        )

    # -----------------------------
    # Visualisations
    # -----------------------------
    st.subheader("3. Visualisations")

    # Monthly return trend
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df['trdmnt'], df['mretwd'], marker='o')
    ax1.set_title(f'Monthly Return Trend for Stock {stock_code}')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Monthly Return')
    ax1.grid(True)
    st.pyplot(fig1)

    # Cumulative return
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(df['trdmnt'], df['cum_return'], marker='o', color='green')
    ax2.set_title(f'Cumulative Return for Stock {stock_code}')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Cumulative Return')
    ax2.grid(True)
    st.pyplot(fig2)

    # Monthly closing price
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(df['trdmnt'], df['mclsprc'], marker='o', color='orange')
    ax3.set_title(f'Monthly Closing Price Trend for Stock {stock_code}')
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Monthly Closing Price')
    ax3.grid(True)
    st.pyplot(fig3)

    # Bar chart
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    ax4.bar(df['year_month'].astype(str), df['mretwd'], color='steelblue')
    ax4.set_title(f'Monthly Return Bar Chart for Stock {stock_code}')
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Monthly Return')
    plt.xticks(rotation=90)
    st.pyplot(fig4)

    # -----------------------------
    # Analytical insight
    # -----------------------------
    st.subheader("4. Analytical Insight")

    insights = []

    if mean_return > 0:
        insights.append(f"Stock {stock_code} delivered a positive average monthly return over the selected period.")
    else:
        insights.append(f"Stock {stock_code} delivered a negative average monthly return over the selected period.")

    if std_return > 0.1:
        insights.append("The stock shows relatively high volatility in monthly returns.")
    else:
        insights.append("The stock shows relatively moderate monthly return volatility.")

    insights.append(
        f"The best-performing month was {best_month['trdmnt'].strftime('%Y-%m')}, "
        f"with a return of {best_month['mretwd']:.4f}."
    )

    insights.append(
        f"The worst-performing month was {worst_month['trdmnt'].strftime('%Y-%m')}, "
        f"with a return of {worst_month['mretwd']:.4f}."
    )

    if df['cum_return'].iloc[-1] > 0:
        insights.append("Overall cumulative return is positive over the selected period.")
    else:
        insights.append("Overall cumulative return is negative over the selected period.")

    if df['mclsprc'].iloc[-1] > df['mclsprc'].iloc[0]:
        insights.append("The monthly closing price shows an overall upward trend.")
    else:
        insights.append("The monthly closing price does not show a clear upward trend.")

    for item in insights:
        st.write(f"- {item}")

    # -----------------------------
    # Full dataset
    # -----------------------------
    st.subheader("5. Full Processed Dataset")
    st.dataframe(df, use_container_width=True)

    # -----------------------------
    # Download
    # -----------------------------
    st.subheader("6. Download Results")
    excel_data = to_excel_bytes(df)

    st.download_button(
        label="Download processed data as Excel",
        data=excel_data,
        file_name=f"{stock_code}_monthly_stock_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please enter parameters in the left sidebar and click 'Run Analysis'.")