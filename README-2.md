# Monthly Stock Analysis Based on WRDS CSMAR

## Project Overview
This project provides a simple Python-based framework for analysing **monthly stock performance** using data from the **WRDS CSMAR database**.

The analysis is implemented in a **Jupyter Notebook** format and is designed to support academic learning, especially for coursework related to finance, investment, data analysis, and business analytics.

The notebook retrieves stock-level monthly trading data, performs cleaning and preprocessing, generates descriptive statistics, visualises trends, and exports processed results to Excel.

---

## Objectives
The main objectives of this project are to:

- retrieve monthly stock data from WRDS
- clean and preprocess financial time series data
- calculate descriptive return and price statistics
- visualise stock return and price behaviour over time
- generate basic analytical insights
- export results for further analysis or reporting

---

## Data Source
The data used in this project comes from:

- **Platform**: WRDS
- **Database**: CSMAR
- **Table**: `csmar.trd_mnth`

This table contains monthly stock trading information for Chinese listed firms.

---

## Variables Used
The notebook uses the following variables from the monthly stock table:

- `stkcd` — stock code
- `trdmnt` — trading month
- `mclsprc` — monthly closing price
- `mretwd` — monthly return with cash dividend reinvested
- `mretnd` — monthly return without cash dividend reinvested
- `mnshrtrd` — monthly trading volume
- `mnvaltrd` — monthly trading value

---

## Main Features
The notebook includes the following analytical steps:

### 1. User Input
Users are asked to provide:
- WRDS username
- stock code
- start month in `YYYYMM` format

### 2. WRDS Connection
The notebook connects to WRDS using the user-provided WRDS username.

### 3. Data Retrieval
Monthly stock data is queried from `csmar.trd_mnth` based on the selected stock code and starting month.

### 4. Data Cleaning and Processing
The notebook:
- keeps relevant columns only
- removes missing values in key fields
- converts the month variable to datetime format
- sorts the data chronologically
- creates derived variables such as cumulative return and price change

### 5. Descriptive Statistics
It calculates:
- average monthly return
- return volatility
- highest and lowest monthly return
- average monthly closing price
- price volatility
- highest and lowest monthly closing price

### 6. Performance Highlights
The notebook identifies:
- best-performing month
- worst-performing month

### 7. Visualisation
The notebook generates:
- monthly return trend plot
- cumulative return plot
- monthly closing price trend plot
- monthly return bar chart

### 8. Analytical Insights
The notebook provides a simple text-based interpretation of:
- average return performance
- volatility level
- cumulative return outcome
- general price trend

### 9. Export
The processed dataset and summary statistics are exported to an Excel file.

---

## File Structure
A typical project structure may look like this:

```bash
project-folder/
│
├── Monthly_Stock_Analysis.ipynb
├── README.md
└── output/
    └── 000001_monthly_stock_analysis.xlsx