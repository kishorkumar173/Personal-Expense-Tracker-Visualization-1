# 💰 Personal Expense Tracker with Data Visualization



An end-to-end, industry-oriented personal finance analytics platform and interactive web application built with **Python, Pandas, SQLite, Seaborn, Matplotlib, and Streamlit**. It automates expense ingestion, applies rule-based heuristic auto-categorization, calculates Month-over-Month (MoM) cashflow velocity, audits budget-to-actual variances, renders publication-grade visualizations, and exports executive financial health audit reports.

---

## 📌 Table of Contents
- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Industry Relevance](#-industry-relevance)
- [Key Features](#-key-features)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation Guide](#-installation-guide)
- [How to Run](#-how-to-run)
- [Generated Visualizations](#-generated-visualizations)
- [Sample Executive Audit Report](#-sample-executive-audit-report)
- [Cloud Deployment Guide](#-cloud-deployment-guide)
- [Learning Outcomes](#-learning-outcomes)

---

## 📖 Project Overview

Managing personal cashflows and adhering to monthly financial budgets is one of the most critical challenges for students, freelancers, salaried professionals, and small business owners. Without granular visibility into where money flows, individuals suffer from lifestyle inflation, undisciplined impulsive spending, and poor savings habits.

The **Personal Expense Tracker with Data Visualization** bridges the gap between raw transaction ledgers and actionable financial intelligence. By combining automated data cleaning, regex-powered merchant auto-categorization, relational SQLite persistence, and high-DPI data visualizations, users receive instant insights into their spending habits and budget utilization.

---

## 🎯 Problem Statement

Traditional expense tracking via paper receipts or raw spreadsheets suffers from major shortcomings:
1. **Manual Friction**: Manually labeling categories for dozens of purchases every week leads to fatigue and abandonment.
2. **Lack of Timely Visibility**: Spreadsheets lack automated variance checks against budget limits, so overspending is only discovered after it happens.
3. **Absence of Trend Analytics**: Raw tables do not reveal burn velocity, payment instrument distribution, or rolling moving averages.
4. **Data Isolation**: Static files do not provide interactive filtering, search, or automated executive PDF/Text summaries.

**Our Solution**: A modular Python ecosystem that ingests dirty CSV or manual inputs, normalizes dates and currency figures, uses natural language keyword heuristics to classify merchants into 9 budget categories, tracks budget variances with warning thresholds, and renders interactive web dashboards alongside automated PDF/Text executive summaries.

---

## 💼 Industry Relevance

This project directly maps to the real-world responsibilities of:
- **Data Analysts**: Designing ETL data cleaning pipelines, aggregating multi-dimensional time series, calculating Month-over-Month (MoM) growth, and crafting executive KPI dashboards.
- **Python / Software Engineers**: Structuring clean, decoupled modules (`src/`), designing relational database schemas with SQLite, handling exception cascades, and writing unit-testable functions.
- **Business Intelligence (BI) Engineers**: Designing Budget vs. Actual variance scorecards, calculating composite health metrics, and visualizing distributions with Seaborn and Matplotlib.
- **Automation / FinTech Engineers**: Building rule-based NLP classifiers for unstructured financial notes and automating report generation.

---

## 🚀 Key Features

- **⚡ Smart Heuristic Auto-Categorization**: Natural keyword matching engine classifies transactions (e.g., `"Starbucks cappuccino"` -> `Food & Dining`, `"Uber ride"` -> `Transportation`) without user intervention.
- **💾 Relational SQLite Database**: Persistent storage for transactions and budget caps with ACID compliance and full CRUD operations.
- **🧹 Automated Data Hygiene**: Cleans currency symbols (`₹`, `$`, `,`), enforces positive numbers, standardizes date formats to ISO 8601 (`YYYY-MM-DD`), and handles missing values.
- **🎯 Budget vs. Actual Variance Tracking**: Real-time evaluation of spending against monthly limits with alert levels (`✅ On Track`, `⚠️ Near Limit (>85%)`, `🚨 Over Budget (>100%)`).
- **📊 5 Publication-Quality Visualizations**:
  - Category Spending Horizontal Bar Chart
  - Monthly Trajectory & Growth Line Plot
  - Payment Method Share Donut Plot
  - Daily Spending Velocity & 7-Day Rolling Moving Average
  - Budget vs. Actual Variance Side-by-Side Comparison
- **🌐 Interactive Streamlit Web Dashboard**: Real-time multi-select filtering by date range, categories, and payment modes; live transaction logging; CSV upload; and instant audit export.
- **📄 Automated Executive Audit Reports**: Generates detailed financial health summaries with savings recommendations in `.txt`, `.md`, and `.csv`.
- **🧪 Synthetic 6-Month Data Generator**: Built-in generator creates 200+ realistic multi-month transactions for instant offline demonstration.

---

## 🏗️ Architecture & Data Flow

```
[Raw CSV / Manual Entry] 
          │
          ▼
[ETL & Normalization] ──> [Smart Auto-Categorizer (Regex / Keywords)]
          │
          ▼
[SQLite Storage (expenses.db)]
          │
          ▼
[Analytical Engine (KPIs, MoM Velocity, Budget Variance)]
          │
     ┌────┴───────────────────────────┐
     ▼                                ▼
[Static High-Res Charts]     [Streamlit Web App (Interactive UI)]
[Executive Audit Reports]    [Live Ledger & Filtering]
```

---

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Language** | Python | 3.10 - 3.13 | Core programming language |
| **Data Processing** | Pandas, NumPy | >= 2.0.0 | Tabular data manipulation, time series feature engineering |
| **Persistence** | SQLite3 | Built-in | Relational transaction ledger & budget persistence |
| **Visualization** | Matplotlib, Seaborn | >= 3.7.0 | High-resolution publication charts (DPI 300) |
| **Interactive UI** | Streamlit | >= 1.30.0 | Web application, live filters, and executive dashboard |
| **Text Parsing** | Regex (`re`) | Built-in | Tokenization and merchant pattern heuristics |
| **Time Series** | Datetime, Dateutil | Built-in | Calendar calculations and rolling moving averages |

---

## 📁 Project Directory Structure

```text
Personal-Expense-Tracker-Visualization/
│
├── data/
│   ├── expenses_sample.csv          # Sample 6-month synthetic dataset (200 records)
│   └── synthetic_expenses.csv       # Generated test datasets
│
├── notebooks/
│   └── 01_expense_data_exploration.ipynb  # Interactive Jupyter notebook for EDA
│
├── src/
│   ├── __init__.py                  # Package initializer
│   ├── database.py                  # SQLite schema creation, CRUD operations & connections
│   ├── categorizer.py               # Rule-based auto-categorizer & regex engine
│   ├── data_processor.py            # Data ingestion, cleaning, normalization & synthetic generator
│   ├── analytics.py                 # Summary KPIs, category aggregates, MoM trends & budget metrics
│   ├── visualizer.py                # High-res Matplotlib & Seaborn chart rendering functions
│   └── report_generator.py          # Executive report compiler (Text, Markdown, CSV)
│
├── outputs/                         # Generated high-resolution static charts (.png)
│   ├── category_spending_bar.png
│   ├── monthly_trend_line.png
│   ├── payment_method_pie.png
│   ├── daily_spending_trend.png
│   └── budget_vs_actual_bar.png
│
├── images/                          # Visual assets for GitHub README documentation
│
├── reports/                         # Automated executive financial audit reports
│   ├── financial_summary_YYYYMMDD.txt
│   ├── financial_summary_YYYYMMDD.md
│   ├── category_breakdown_YYYYMMDD.csv
│   └── budget_variance_YYYYMMDD.csv
│
├── docs/
│   ├── ARCHITECTURE.md              # Detailed technical design & database schema
│   └── USER_GUIDE.md                 # Step-by-step user operation manual
│
├── app.py                           # Interactive Streamlit Web Application
├── main.py                          # Automated CLI pipeline orchestrator
├── requirements.txt                 # Project dependencies
├── .gitignore                       # Git exclusion rules
└── README.md                        # Project documentation
```

---

## 💻 Installation Guide

### 1. Prerequisites
Ensure you have **Python 3.10 or higher** installed:
```bash
python --version
```

### 2. Clone Repository or Navigate to Project Folder
```bash
cd "E:\IIT PROJECT\PYTHON 1\Personal-Expense-Tracker-Visualization"
```

### 3. Create and Activate Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚡ How to Run

### Option 1: Run the Automated CLI Pipeline
To initialize the SQLite database, ingest data, perform analytics, save all high-res charts to `outputs/`, and generate reports into `reports/`:
```bash
python main.py
```

**Expected Terminal Output:**
```text
========================================================================
    💰 PERSONAL EXPENSE TRACKER & DATA VISUALIZATION SYSTEM 📊
========================================================================
[1/6] 🛠️  Initializing SQLite Database schema...
      Database ready at: expenses.db
[2/6] 📥 Ingesting transaction dataset...
      Saved 200 realistic records to: data/expenses_sample.csv
[3/6] 🧹 Cleaning and validating transaction data...
      Valid records processed: 200
[4/6] 📈 Performing analytical calculations & KPI derivations...

-----------------------------------------------------------------
                    EXECUTIVE KPI SUMMARY                     
-----------------------------------------------------------------
  Total Spend Outflow    : ₹  270,993.03
  Total Transactions     :          200
  Average Daily Spending : ₹    1,575.54
  Average Ticket Size    : ₹    1,354.97
  Top Spending Category  : Food & Dining (29.0%)
  Financial Health Score : 80 / 100 (Excellent (Healthy))
-----------------------------------------------------------------

[5/6] 🎨 Rendering high-resolution Matplotlib/Seaborn charts...
      Saved: category_spending_bar.png
      Saved: monthly_trend_line.png
      Saved: payment_method_pie.png
      Saved: daily_spending_trend.png
      Saved: budget_vs_actual_bar.png
[6/6] 📑 Compiling audit reports and data summaries...
======================================================================
  ✅ PIPELINE EXECUTION COMPLETE!
======================================================================
```

---

### Option 2: Launch the Interactive Streamlit Web Dashboard
To open the interactive browser-based dashboard:
```bash
streamlit run app.py
```
The browser will automatically launch at `http://localhost:8501`.

**Dashboard Features:**
1. **Analytics & Insights**: Live KPI cards, dynamic horizontal bar charts, time-series trajectory, payment share donut, and 7-day rolling moving averages.
2. **Budget Variance**: Visual comparison of actual outflows against category budgets with color-coded alerts (`🚨 Over Budget`, `⚠️ Near Limit`, `✅ On Track`).
3. **Add Expense**: Instant form with **Smart Auto-Categorization** that guesses your category as you type the description.
4. **Transaction Ledger**: Searchable, filterable ledger with instant CSV export and record deletion.
5. **Executive Report**: Live generated audit document downloadable as `.txt` or `.md`.

---

## 📈 Generated Visualizations

All visualizations are rendered using professional color palettes, clear labels, and 300 DPI output:

| Visualization | Description | File Location |
| :--- | :--- | :--- |
| **Category Spending Bar** | Horizontal ranked bars showing total spend and share per category | `outputs/category_spending_bar.png` |
| **Monthly Trend Line** | Chronological line plot displaying Month-over-Month cashflow velocity | `outputs/monthly_trend_line.png` |
| **Payment Mode Donut** | Distribution of transactions across UPI, Cards, and Net Banking | `outputs/payment_method_pie.png` |
| **Daily Spending Velocity** | Scatter plot of daily transactions overlaid with a 7-day rolling average | `outputs/daily_spending_trend.png` |
| **Budget vs. Actual Variance** | Comparative bar chart displaying budget caps against actual spending | `outputs/budget_vs_actual_bar.png` |

---

## 📑 Sample Executive Audit Report

Generated automatically in `reports/financial_summary_YYYYMMDD.txt`:

```text
======================================================================
          PERSONAL EXPENSE TRACKER - FINANCIAL AUDIT REPORT         
======================================================================
Analysis Date Range   : 2026-06-02 to 2026-11-20
Total Recorded Outflow: ₹270,993.03
Total Transactions    : 200
Average Daily Spend   : ₹1,575.54
Average Ticket Size   : ₹1,354.97
Top Spending Category : Food & Dining (₹78,690.26 | 29.0%)
Preferred Payment Mode: UPI
----------------------------------------------------------------------
FINANCIAL HEALTH & BUDGET INTEGRITY SCORE:
Score  : 80 / 100
Rating : Excellent (Healthy)
----------------------------------------------------------------------
CATEGORY SPENDING BREAKDOWN:
Category               | Amount (INR)   | Share (%)  | Txns  
----------------------------------------------------------------------
Food & Dining          | ₹   78,690.26 |     29.0% |    62
Shopping               | ₹   57,870.00 |     21.4% |    22
Rent & Utilities       | ₹   48,970.00 |     18.1% |    10
Transportation         | ₹   27,123.82 |     10.0% |    46
Entertainment          | ₹   19,638.00 |      7.2% |    21
Personal Care          | ₹   14,459.87 |      5.3% |    15
Healthcare             | ₹   13,497.07 |      5.0% |    10
Education              | ₹    7,990.00 |      2.9% |     7
Miscellaneous          | ₹    2,754.01 |      1.0% |     7
----------------------------------------------------------------------
ACTIONABLE RECOMMENDATIONS:
  • Category 'Food & Dining' is over budget by ₹6,118.65 (161.2% used).
  • Category 'Rent & Utilities' is over budget by ₹1,990.00 (113.3% used).
======================================================================
```

---

## ☁️ Cloud Deployment Guide

You can deploy this dashboard to the cloud for free so recruiters can interact with it online:

### Deploying to Streamlit Community Cloud (Free & 1-Click)
1. Push this project to your GitHub repository.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **"New App"**.
4. Select your repository: `Personal-Expense-Tracker-Visualization`.
5. Set **Main file path**: `app.py`.
6. Click **Deploy!** Your app will be live with a shareable URL in under 2 minutes.

---

## 🎓 Learning Outcomes

By building and presenting this project, you demonstrate mastery in:
1. **End-to-End Data Pipeline Architecture**: Decoupled ingestion, normalization, database persistence, and analytics.
2. **Relational Database Design**: Designing schema constraints, handling parameterized queries, and ACID transactions in SQLite.
3. **Data Cleansing & Feature Engineering**: Parsing diverse datetime series, handling null values, and deriving rolling statistical features.
4. **Natural Language Heuristics**: Crafting rule-based token classification models.
5. **Data Storytelling**: Building interactive visual analytics that drive financial discipline.

---

## 📄 License
This project is open-source and licensed under the MIT License.
