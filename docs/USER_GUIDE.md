# 📘 Personal Expense Tracker - User Manual & Operating Guide

## 1. Quick Start Guide

### Step 1: Open Terminal in Project Directory
```powershell
cd "E:\IIT PROJECT\PYTHON 1\Personal-Expense-Tracker-Visualization"
```

### Step 2: Run CLI Automated Processing
```powershell
python main.py
```
This single command:
1. Creates `expenses.db` SQLite database (if it doesn't already exist).
2. Generates 200 synthetic 6-month transactions in `data/expenses_sample.csv`.
3. Cleans, checks and inserts records into SQLite.
4. Calculates Month-over-Month (MoM) trajectories and budget variances.
5. Saves all 5 high-resolution PNG charts in `outputs/`.
6. Generates full financial reports in `reports/`.

---

## 2. Interactive Web Dashboard (Streamlit)

To launch the web interface:
```powershell
streamlit run app.py
```

### How to use the Web App:
- **Date & Category Filter**: Use the left sidebar to isolate specific date ranges, categories, or payment instruments.
- **Add Transactions**: Go to the **➕ Add Expense** tab. When you type "Starbucks latte", the auto-categorizer automatically detects **Food & Dining** with its confidence rating. Click "Save Expense" to store it in SQLite immediately.
- **Upload CSV Bank Statements**: Under **➕ Add Expense**, click "Upload CSV Statement" to batch-import transactions.
- **Budget Tracking**: Switch to the **🎯 Budget Variance** tab to see which categories exceeded monthly budgets with alert tags (`🚨 Over Budget`, `⚠️ Near Limit`, `✅ On Track`).
- **Download Reports**: Go to **📄 Executive Report** tab to download your customized audit report in `.txt` or `.md`.
