"""
report_generator.py
-------------------
Executive Financial Report Generation Engine.
Compiles analysis data into structured text, markdown, and CSV audit reports.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
from src.analytics import (
    get_summary_kpis,
    get_category_summary,
    get_monthly_trends,
    get_payment_method_breakdown,
    get_budget_vs_actual,
    calculate_financial_health
)


def generate_text_report(
    df: pd.DataFrame,
    budgets: Dict[str, float],
    output_txt_path: Optional[str] = None
) -> str:
    """Creates a formatted plain text financial health report."""
    if df.empty:
        return "No transaction data available to generate report."

    kpis = get_summary_kpis(df)
    cat_df = get_category_summary(df)
    health = calculate_financial_health(df, budgets)
    budget_df = get_budget_vs_actual(df, budgets)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=" * 70,
        "          PERSONAL EXPENSE TRACKER - FINANCIAL AUDIT REPORT         ",
        "=" * 70,
        f"Generated On          : {timestamp}",
        f"Analysis Date Range   : {df['date'].min()} to {df['date'].max()}",
        f"Total Recorded Outflow: ₹{kpis['total_spending']:,.2f}",
        f"Total Transactions    : {kpis['transaction_count']:,}",
        f"Average Daily Spend   : ₹{kpis['avg_daily_spending']:,.2f}",
        f"Average Ticket Size   : ₹{kpis['avg_transaction_size']:,.2f}",
        f"Top Spending Category : {kpis['top_category']['category']} (₹{kpis['top_category']['amount']:,.2f} | {kpis['top_category']['percentage']:.1f}%)",
        f"Preferred Payment Mode: {kpis['top_payment_method']}",
        "-" * 70,
        f"Largest Single Expense: ₹{kpis['highest_expense']['amount']:,.2f}",
        f"  Description         : {kpis['highest_expense']['description']}",
        f"  Category            : {kpis['highest_expense']['category']}",
        f"  Date                : {kpis['highest_expense']['date']}",
        "-" * 70,
        "FINANCIAL HEALTH & BUDGET INTEGRITY SCORE:",
        f"Score  : {health['score']} / 100",
        f"Rating : {health['rating']}",
        "-" * 70,
        "CATEGORY SPENDING BREAKDOWN:",
        f"{'Category':<22} | {'Amount (INR)':<14} | {'Share (%)':<10} | {'Txns':<6}",
        "-" * 70
    ]

    for _, row in cat_df.iterrows():
        report_lines.append(
            f"{row['category']:<22} | ₹{row['total_amount']:>12,.2f} | {row['percentage']:>8.1f}% | {row['txn_count']:>5}"
        )

    report_lines.extend([
        "-" * 70,
        "BUDGET VARIANCE AUDIT (CURRENT PERIOD):",
        f"{'Category':<20} | {'Budget':<10} | {'Actual':<10} | {'Variance':<10} | {'Status'}",
        "-" * 70
    ])

    for _, row in budget_df.iterrows():
        report_lines.append(
            f"{row['category']:<20} | ₹{row['budget']:>8,.0f} | ₹{row['actual']:>8,.0f} | ₹{row['variance']:>8,.0f} | {row['status']}"
        )

    report_lines.extend([
        "-" * 70,
        "ACTIONABLE RECOMMENDATIONS:",
    ])
    for rec in health["recommendations"]:
        report_lines.append(f"  • {rec}")

    report_lines.extend([
        "=" * 70,
        "End of Report. Stay disciplined and invest for compounding wealth!",
        "=" * 70
    ])

    full_report = "\n".join(report_lines)

    if output_txt_path:
        os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_report)

    return full_report


def export_reports_bundle(
    df: pd.DataFrame,
    budgets: Dict[str, float],
    reports_dir: str = "reports"
) -> Dict[str, str]:
    """Generates and exports text, markdown, and CSV tables to the reports folder."""
    os.makedirs(reports_dir, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")

    txt_file = os.path.join(reports_dir, f"financial_summary_{today_str}.txt")
    md_file = os.path.join(reports_dir, f"financial_summary_{today_str}.md")
    cat_csv_file = os.path.join(reports_dir, f"category_breakdown_{today_str}.csv")
    budget_csv_file = os.path.join(reports_dir, f"budget_variance_{today_str}.csv")

    # Generate text report
    txt_content = generate_text_report(df, budgets, output_txt_path=txt_file)

    # Markdown version
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Personal Financial Executive Report\n\n```text\n{txt_content}\n```\n")

    # Export CSV tables
    cat_df = get_category_summary(df)
    cat_df.to_csv(cat_csv_file, index=False)

    budget_df = get_budget_vs_actual(df, budgets)
    budget_df.to_csv(budget_csv_file, index=False)

    return {
        "text_report": txt_file,
        "markdown_report": md_file,
        "category_csv": cat_csv_file,
        "budget_csv": budget_csv_file
    }
