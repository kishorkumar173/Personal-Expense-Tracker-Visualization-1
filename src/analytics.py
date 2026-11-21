"""
analytics.py
------------
Analytical Engine for Personal Expense Tracker.
Calculates summary KPIs, category distributions, monthly trajectories,
payment mode utilization, daily velocities, and budget variance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple


def get_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes high-level executive financial KPIs from cleaned transactions."""
    if df.empty:
        return {
            "total_spending": 0.0,
            "transaction_count": 0,
            "avg_daily_spending": 0.0,
            "avg_transaction_size": 0.0,
            "highest_expense": {"amount": 0.0, "category": "N/A", "description": "N/A", "date": "N/A"},
            "top_category": {"category": "N/A", "amount": 0.0, "percentage": 0.0},
            "top_payment_method": "N/A"
        }

    total_spending = float(df["amount"].sum())
    transaction_count = len(df)
    avg_txn = float(df["amount"].mean())

    # Date span calculation
    min_date = pd.to_datetime(df["date"].min())
    max_date = pd.to_datetime(df["date"].max())
    days_span = max(1, (max_date - min_date).days + 1)
    avg_daily = total_spending / days_span

    # Highest expense record
    max_row = df.loc[df["amount"].idxmax()]
    highest_expense = {
        "amount": float(max_row["amount"]),
        "category": str(max_row["category"]),
        "description": str(max_row["description"]),
        "date": str(max_row["date"])
    }

    # Top spending category
    cat_totals = df.groupby("category")["amount"].sum()
    top_cat_name = cat_totals.idxmax()
    top_cat_amt = float(cat_totals.max())
    top_cat_pct = (top_cat_amt / total_spending * 100) if total_spending > 0 else 0.0

    # Top payment method
    pay_counts = df["payment_method"].value_counts()
    top_pay_method = pay_counts.index[0] if not pay_counts.empty else "N/A"

    return {
        "total_spending": total_spending,
        "transaction_count": transaction_count,
        "avg_daily_spending": avg_daily,
        "avg_transaction_size": avg_txn,
        "days_span": days_span,
        "highest_expense": highest_expense,
        "top_category": {
            "category": top_cat_name,
            "amount": top_cat_amt,
            "percentage": top_cat_pct
        },
        "top_payment_method": top_pay_method
    }


def get_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a consolidated summary of spend by category with share %."""
    if df.empty:
        return pd.DataFrame(columns=["category", "total_amount", "percentage", "txn_count", "avg_txn"])

    total = df["amount"].sum()
    cat_df = df.groupby("category").agg(
        total_amount=("amount", "sum"),
        txn_count=("amount", "count"),
        avg_txn=("amount", "mean")
    ).reset_index()

    cat_df["percentage"] = (cat_df["total_amount"] / total * 100) if total > 0 else 0.0
    cat_df = cat_df.sort_values(by="total_amount", ascending=False).reset_index(drop=True)
    return cat_df


def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes chronological monthly spending totals and Month-over-Month (MoM) % changes.
    """
    if df.empty:
        return pd.DataFrame(columns=["year_month", "total_amount", "txn_count", "mom_growth_pct"])

    monthly = df.groupby(["year_month", "month_name"]).agg(
        total_amount=("amount", "sum"),
        txn_count=("amount", "count")
    ).reset_index()

    monthly = monthly.sort_values(by="year_month", ascending=True).reset_index(drop=True)
    monthly["mom_growth_pct"] = monthly["total_amount"].pct_change() * 100
    monthly["mom_growth_pct"] = monthly["mom_growth_pct"].fillna(0.0)
    return monthly


def get_payment_method_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates total spending and count by payment instrument."""
    if df.empty:
        return pd.DataFrame(columns=["payment_method", "total_amount", "percentage", "txn_count"])

    total = df["amount"].sum()
    pay_df = df.groupby("payment_method").agg(
        total_amount=("amount", "sum"),
        txn_count=("amount", "count")
    ).reset_index()

    pay_df["percentage"] = (pay_df["total_amount"] / total * 100) if total > 0 else 0.0
    pay_df = pay_df.sort_values(by="total_amount", ascending=False).reset_index(drop=True)
    return pay_df


def get_daily_spending_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Returns daily spending totals along with a 7-day smoothing rolling average."""
    if df.empty:
        return pd.DataFrame(columns=["date", "daily_total", "rolling_7d_avg"])

    daily = df.groupby("date")["amount"].sum().reset_index()
    daily.rename(columns={"amount": "daily_total"}, inplace=True)
    daily = daily.sort_values(by="date", ascending=True).reset_index(drop=True)
    daily["rolling_7d_avg"] = daily["daily_total"].rolling(window=7, min_periods=1).mean()
    return daily


def get_budget_vs_actual(
    df: pd.DataFrame,
    budgets: Dict[str, float],
    target_month: Optional[str] = None
) -> pd.DataFrame:
    """
    Performs Budget vs. Actual variance analysis.
    
    Args:
        df: Cleaned transactions DataFrame.
        budgets: Dictionary mapping category to monthly budget cap.
        target_month: Filter for specific Year-Month (e.g., '2026-11'). If None, uses latest month.
    """
    if df.empty:
        return pd.DataFrame()

    if target_month is None:
        target_month = df["year_month"].max()

    month_df = df[df["year_month"] == target_month]
    actual_spending = month_df.groupby("category")["amount"].sum().to_dict()

    rows = []
    all_categories = sorted(set(list(budgets.keys()) + list(actual_spending.keys())))

    for cat in all_categories:
        budget_limit = budgets.get(cat, 0.0)
        actual_spend = actual_spending.get(cat, 0.0)
        variance = actual_spend - budget_limit  # positive means overspent
        pct_used = (actual_spend / budget_limit * 100) if budget_limit > 0 else 100.0

        if pct_used > 100:
            status = "🚨 Over Budget"
        elif pct_used >= 85:
            status = "⚠️ Near Limit"
        else:
            status = "✅ On Track"

        rows.append({
            "category": cat,
            "budget": budget_limit,
            "actual": actual_spend,
            "variance": variance,
            "pct_utilized": round(pct_used, 1),
            "status": status
        })

    budget_df = pd.DataFrame(rows)
    return budget_df.sort_values(by="actual", ascending=False).reset_index(drop=True)


def calculate_financial_health(df: pd.DataFrame, budgets: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculates a Composite Financial Health Score (0 - 100) based on:
    1. Overall Budget Adherence (40 points)
    2. Essential vs. Discretionary ratio (30 points)
    3. Daily spending consistency (30 points)
    """
    if df.empty:
        return {"score": 50, "rating": "Moderate", "recommendations": ["No transactions recorded."]}

    b_df = get_budget_vs_actual(df, budgets)
    total_budget = b_df["budget"].sum()
    total_actual = b_df["actual"].sum()

    score = 100
    recommendations = []

    # 1. Budget Adherence penalty
    if total_actual > total_budget and total_budget > 0:
        over_pct = ((total_actual - total_budget) / total_budget) * 100
        penalty = min(35, over_pct * 0.8)
        score -= penalty
        recommendations.append(f"Total spending exceeds overall budget by {over_pct:.1f}%. Consider trimming discretionary purchases.")

    # 2. Overspent categories count
    overspent_cats = b_df[b_df["variance"] > 0]
    if len(overspent_cats) > 0:
        penalty = min(25, len(overspent_cats) * 5)
        score -= penalty
        for _, row in overspent_cats.iterrows():
            recommendations.append(
                f"Category '{row['category']}' is over budget by ₹{row['variance']:,.2f} ({row['pct_utilized']}% used)."
            )

    # 3. Discretionary vs Essential
    essential_cats = {"Rent & Utilities", "Food & Dining", "Healthcare", "Education"}
    cat_summary = get_category_summary(df)
    essential_spend = cat_summary[cat_summary["category"].isin(essential_cats)]["total_amount"].sum()
    essential_ratio = (essential_spend / total_actual) if total_actual > 0 else 0.5

    if essential_ratio < 0.50:
        score -= 10
        recommendations.append("Discretionary spending (Shopping, Entertainment) exceeds 50% of your total outflows.")

    if not recommendations:
        recommendations.append("Excellent financial discipline! All categories are well within allocated budgets.")

    score = max(10, min(100, int(score)))
    if score >= 80:
        rating = "Excellent (Healthy)"
    elif score >= 60:
        rating = "Good (Stable)"
    elif score >= 40:
        rating = "Needs Attention"
    else:
        rating = "Critical Overspending"

    return {
        "score": score,
        "rating": rating,
        "total_budget": total_budget,
        "total_actual": total_actual,
        "recommendations": recommendations
    }
