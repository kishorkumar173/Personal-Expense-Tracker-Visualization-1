"""
main.py
-------
Command-Line Interface & Automated Pipeline Orchestrator.
Runs the complete end-to-end expense tracking and visual analytics pipeline:
Ingestion -> SQLite Storage -> Cleaning -> Analytics -> High-Res Plotting -> Audit Reports.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Configure UTF-8 stdout for Windows command prompt / powershell compatibility
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path to ensure modular imports work seamlessly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.database import (
    init_db,
    bulk_insert_transactions,
    get_all_transactions,
    get_budgets,
    clear_all_transactions
)
from src.data_processor import (
    generate_synthetic_expenses,
    clean_expense_data
)
from src.analytics import (
    get_summary_kpis,
    get_category_summary,
    get_monthly_trends,
    get_payment_method_breakdown,
    get_daily_spending_trend,
    get_budget_vs_actual,
    calculate_financial_health
)
from src.visualizer import (
    plot_category_bar,
    plot_monthly_trend_line,
    plot_payment_method_pie,
    plot_daily_trend,
    plot_budget_vs_actual_bar
)
from src.report_generator import export_reports_bundle, generate_text_report


def print_banner():
    banner = """
========================================================================
    💰 PERSONAL EXPENSE TRACKER & DATA VISUALIZATION SYSTEM 📊
========================================================================
  Industry-grade Personal Finance Analytics & Data Science Showcase
========================================================================
"""
    print(banner)


def run_pipeline():
    print_banner()

    # Define paths
    db_path = os.path.join(CURRENT_DIR, "expenses.db")
    data_dir = os.path.join(CURRENT_DIR, "data")
    outputs_dir = os.path.join(CURRENT_DIR, "outputs")
    reports_dir = os.path.join(CURRENT_DIR, "reports")
    sample_csv_path = os.path.join(data_dir, "expenses_sample.csv")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Initialize SQLite Database
    print("[1/6] 🛠️  Initializing SQLite Database schema...")
    init_db(db_path)
    budgets = get_budgets(db_path)
    print(f"      Database ready at: {db_path}")
    print(f"      Loaded {len(budgets)} category budget rules.")

    # 2. Check or Create Synthetic Data
    print("\n[2/6] 📥 Ingesting transaction dataset...")
    if not os.path.exists(sample_csv_path):
        print("      No existing dataset detected. Generating synthetic 6-month expense dataset...")
        df_raw = generate_synthetic_expenses(n_transactions=200, start_date="2026-06-01", end_date="2026-11-20")
        df_raw.to_csv(sample_csv_path, index=False)
        print(f"      Saved {len(df_raw)} realistic records to: {sample_csv_path}")
    else:
        print(f"      Found existing dataset: {sample_csv_path}")
        df_raw = pd.read_csv(sample_csv_path)

    # 3. Data Cleaning and Validation
    print("\n[3/6] 🧹 Cleaning and validating transaction data...")
    cleaned_df = clean_expense_data(df_raw)
    print(f"      Valid records processed: {len(cleaned_df)}")

    # Synchronize with SQLite
    existing_records = get_all_transactions(db_path)
    if existing_records.empty:
        print("      Seeding SQLite database with transactions...")
        bulk_insert_transactions(db_path, cleaned_df)
    else:
        print(f"      SQLite already contains {len(existing_records)} records.")

    # Fetch fresh DataFrame from DB for downstream analytics
    db_df = get_all_transactions(db_path)
    analyzable_df = clean_expense_data(db_df)

    # 4. Perform Analytics
    print("\n[4/6] 📈 Performing analytical calculations & KPI derivations...")
    kpis = get_summary_kpis(analyzable_df)
    cat_df = get_category_summary(analyzable_df)
    monthly_df = get_monthly_trends(analyzable_df)
    pay_df = get_payment_method_breakdown(analyzable_df)
    daily_df = get_daily_spending_trend(analyzable_df)
    budget_df = get_budget_vs_actual(analyzable_df, budgets)
    health = calculate_financial_health(analyzable_df, budgets)

    print("\n" + "-" * 65)
    print("                    EXECUTIVE KPI SUMMARY                     ")
    print("-" * 65)
    print(f"  Total Spend Outflow    : ₹{kpis['total_spending']:>12,.2f}")
    print(f"  Total Transactions     : {kpis['transaction_count']:>12,}")
    print(f"  Average Daily Spending : ₹{kpis['avg_daily_spending']:>12,.2f}")
    print(f"  Average Ticket Size    : ₹{kpis['avg_transaction_size']:>12,.2f}")
    print(f"  Top Spending Category  : {kpis['top_category']['category']} ({kpis['top_category']['percentage']:.1f}%)")
    print(f"  Financial Health Score : {health['score']} / 100 ({health['rating']})")
    print("-" * 65)

    # 5. Generate and Export Visualizations
    print("\n[5/6] 🎨 Rendering high-resolution Matplotlib/Seaborn charts...")
    chart_files = {
        "Category Bar Chart": os.path.join(outputs_dir, "category_spending_bar.png"),
        "Monthly Trend Line": os.path.join(outputs_dir, "monthly_trend_line.png"),
        "Payment Mode Donut": os.path.join(outputs_dir, "payment_method_pie.png"),
        "Daily Velocity Plot": os.path.join(outputs_dir, "daily_spending_trend.png"),
        "Budget vs Actual": os.path.join(outputs_dir, "budget_vs_actual_bar.png")
    }

    plot_category_bar(cat_df, chart_files["Category Bar Chart"])
    plot_monthly_trend_line(monthly_df, chart_files["Monthly Trend Line"])
    plot_payment_method_pie(pay_df, chart_files["Payment Mode Donut"])
    plot_daily_trend(daily_df, chart_files["Daily Velocity Plot"])
    plot_budget_vs_actual_bar(budget_df, chart_files["Budget vs Actual"])

    for name, path in chart_files.items():
        print(f"      Saved: {os.path.basename(path)}")

    # 6. Generate and Export Audit Reports
    print("\n[6/6] 📑 Compiling audit reports and data summaries...")
    bundle = export_reports_bundle(analyzable_df, budgets, reports_dir=reports_dir)
    print(f"      Executive Text Report : {bundle['text_report']}")
    print(f"      Markdown Report       : {bundle['markdown_report']}")
    print(f"      Category CSV Breakdown: {bundle['category_csv']}")
    print(f"      Budget Variance CSV   : {bundle['budget_csv']}")

    print("\n" + "=" * 70)
    print("  ✅ PIPELINE EXECUTION COMPLETE!")
    print("  🌐 To launch the interactive Streamlit dashboard:")
    print("     streamlit run app.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_pipeline()
