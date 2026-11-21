"""
visualizer.py
-------------
Publication-Quality Data Visualization Module.
Generates professional Matplotlib and Seaborn charts for reporting and dashboards.
Saves high-resolution PNG assets to the outputs/ directory.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from typing import Dict, Optional, Tuple


# Set cohesive aesthetic style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.labelweight"] = "bold"

PALETTE = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666", "#1b9e77"]


def plot_category_bar(cat_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """Generates a horizontal bar chart of category-wise spending with value tags."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    if cat_df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    # Sort ascending for clean horizontal presentation
    sorted_df = cat_df.sort_values(by="total_amount", ascending=True)
    colors = sns.color_palette("mako", len(sorted_df))

    bars = ax.barh(sorted_df["category"], sorted_df["total_amount"], color=colors, edgecolor="black", linewidth=0.7)

    # Annotate bars with currency value and percentage
    max_val = sorted_df["total_amount"].max()
    for bar in bars:
        width = bar.get_width()
        pct = (width / sorted_df["total_amount"].sum()) * 100
        ax.text(
            width + (max_val * 0.015),
            bar.get_y() + bar.get_height() / 2,
            f"₹{width:,.0f} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=9,
            fontweight="bold",
            color="#222222"
        )

    ax.set_title("Total Spending by Expense Category", pad=15)
    ax.set_xlabel("Total Spend (INR ₹)")
    ax.set_ylabel("Category")
    ax.set_xlim(0, max_val * 1.25)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)

    return fig


def plot_monthly_trend_line(monthly_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """Generates a chronological line chart showing monthly spending trajectory and MoM changes."""
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    if monthly_df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    x_labels = monthly_df["month_name"]
    y_values = monthly_df["total_amount"]

    ax.plot(x_labels, y_values, marker="o", markersize=8, color="#1f77b4", linewidth=2.5, label="Monthly Spending")
    ax.fill_between(x_labels, y_values, color="#1f77b4", alpha=0.15)

    # Annotate points
    for x, y, mom in zip(x_labels, y_values, monthly_df["mom_growth_pct"]):
        mom_label = f" ({mom:+.1f}%)" if mom != 0 else ""
        ax.annotate(
            f"₹{y:,.0f}{mom_label}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color="#0d3b66"
        )

    ax.set_title("Monthly Spending Trajectory & Growth", pad=15)
    ax.set_xlabel("Billing Period")
    ax.set_ylabel("Monthly Expenditure (INR ₹)")
    ax.set_ylim(0, max(y_values) * 1.25)
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)

    return fig


def plot_payment_method_pie(pay_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """Generates a modern donut pie chart for payment method distribution."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    if pay_df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    colors = sns.color_palette("Set2", len(pay_df))
    wedges, texts, autotexts = ax.pie(
        pay_df["total_amount"],
        labels=pay_df["payment_method"],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")
        autotext.set_color("#111111")

    ax.set_title("Payment Method Share (% Outflow)", pad=15)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)

    return fig


def plot_daily_trend(daily_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """Generates a daily expense time series with 7-day rolling average overlay."""
    fig, ax = plt.subplots(figsize=(11, 5), dpi=300)

    if daily_df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    dates = pd.to_datetime(daily_df["date"])
    ax.scatter(dates, daily_df["daily_total"], color="#999999", alpha=0.5, s=25, label="Daily Spend")
    ax.plot(dates, daily_df["rolling_7d_avg"], color="#e63946", linewidth=2.5, label="7-Day Rolling Average")

    ax.set_title("Daily Spending Velocity & 7-Day Moving Trend", pad=15)
    ax.set_xlabel("Transaction Date")
    ax.set_ylabel("Spending (INR ₹)")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)

    return fig


def plot_budget_vs_actual_bar(budget_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """Generates a comparative side-by-side bar chart of Budget vs Actual per Category."""
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

    if budget_df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    x = np.arange(len(budget_df))
    width = 0.35

    ax.bar(x - width/2, budget_df["budget"], width, label="Allocated Budget", color="#457b9d", edgecolor="black", alpha=0.85)
    bars_actual = ax.bar(x + width/2, budget_df["actual"], width, label="Actual Spend", color="#e63946", edgecolor="black", alpha=0.85)

    ax.set_title("Monthly Budget vs. Actual Expenditure Variance", pad=15)
    ax.set_xlabel("Expense Category")
    ax.set_ylabel("Amount (INR ₹)")
    ax.set_xticks(x)
    ax.set_xticklabels(budget_df["category"], rotation=30, ha="right")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)

    return fig
