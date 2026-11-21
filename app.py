"""
app.py
------
Production-Grade Interactive Streamlit Web Application.
Advanced Option Dashboard featuring Real-time Analytics, Auto-Categorization,
Budget Tracking, Interactive Plotting, and Report Generation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, date

# Set page configuration FIRST
st.set_page_config(
    page_title="Personal Expense Tracker | FinAnalytics",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.database import (
    init_db,
    add_transaction,
    bulk_insert_transactions,
    get_all_transactions,
    delete_transaction,
    get_budgets,
    set_budget,
    clear_all_transactions
)
from src.categorizer import predict_category
from src.data_processor import clean_expense_data, generate_synthetic_expenses
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
from src.report_generator import generate_text_report

# Custom CSS for Modern UI
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #1f77b4;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .badge-success {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-danger {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


DB_PATH = os.path.join(CURRENT_DIR, "expenses.db")
SAMPLE_CSV_PATH = os.path.join(CURRENT_DIR, "data", "expenses_sample.csv")


@st.cache_resource
def setup_database():
    """Ensure database tables exist on startup."""
    init_db(DB_PATH)


setup_database()


def load_data():
    """Loads and standardizes transaction data from SQLite."""
    df_raw = get_all_transactions(DB_PATH)
    if df_raw.empty:
        # Check if sample csv exists, otherwise generate synthetic
        if os.path.exists(SAMPLE_CSV_PATH):
            df_sample = pd.read_csv(SAMPLE_CSV_PATH)
        else:
            df_sample = generate_synthetic_expenses(n_transactions=180)
            os.makedirs(os.path.join(CURRENT_DIR, "data"), exist_ok=True)
            df_sample.to_csv(SAMPLE_CSV_PATH, index=False)
        bulk_insert_transactions(DB_PATH, df_sample)
        df_raw = get_all_transactions(DB_PATH)

    cleaned = clean_expense_data(df_raw)
    return cleaned


# Load current data
df = load_data()
budgets = get_budgets(DB_PATH)

# ==========================================
# SIDEBAR: FILTERS & ACTIONS
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/bullish.png", width=70)
st.sidebar.title("Personal Finance Pro")
st.sidebar.caption("Smart Expense Tracker & Analytics")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filter Transactions")

if not df.empty:
    min_date = pd.to_datetime(df["date"].min()).date()
    max_date = pd.to_datetime(df["date"].max()).date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    all_categories = sorted(df["category"].unique())
    selected_categories = st.sidebar.multiselect(
        "Filter by Category",
        options=all_categories,
        default=all_categories
    )

    all_payment_methods = sorted(df["payment_method"].unique())
    selected_payments = st.sidebar.multiselect(
        "Filter by Payment Mode",
        options=all_payment_methods,
        default=all_payment_methods
    )

    # Apply Filters
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
        filtered_df = df[
            (pd.to_datetime(df["date"]).dt.date >= start_d) &
            (pd.to_datetime(df["date"]).dt.date <= end_d) &
            (df["category"].isin(selected_categories)) &
            (df["payment_method"].isin(selected_payments))
        ].copy()
    else:
        filtered_df = df[
            (df["category"].isin(selected_categories)) &
            (df["payment_method"].isin(selected_payments))
        ].copy()
else:
    filtered_df = df.copy()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Database Actions")

if st.sidebar.button("🔄 Reset to Synthetic 6-Month Data"):
    clear_all_transactions(DB_PATH)
    new_data = generate_synthetic_expenses(n_transactions=200)
    bulk_insert_transactions(DB_PATH, new_data)
    st.cache_data.clear()
    st.sidebar.success("Database re-seeded with 200 synthetic records!")
    st.rerun()

# ==========================================
# MAIN PANEL TABS
# ==========================================
tab_overview, tab_budget, tab_add, tab_ledger, tab_report = st.tabs([
    "📊 Analytics & Insights",
    "🎯 Budget Variance",
    "➕ Add Expense",
    "📋 Transaction Ledger",
    "📄 Executive Report"
])

# ----------------------------------------------------
# TAB 1: OVERVIEW & INSIGHTS
# ----------------------------------------------------
with tab_overview:
    st.title("💰 Personal Expense & Cashflow Analytics")
    st.caption("Gain complete visibility into your spending velocity, categories, and financial health.")

    if filtered_df.empty:
        st.warning("No transactions found for the selected filter range.")
    else:
        kpis = get_summary_kpis(filtered_df)
        health = calculate_financial_health(filtered_df, budgets)

        # 4 Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Total Spend Outflow",
                value=f"₹{kpis['total_spending']:,.2f}",
                delta=f"{kpis['transaction_count']} txns"
            )
        with col2:
            st.metric(
                label="Avg Daily Burn",
                value=f"₹{kpis['avg_daily_spending']:,.2f}",
                delta=f"Span: {kpis['days_span']} days",
                delta_color="off"
            )
        with col3:
            st.metric(
                label="Top Category",
                value=kpis["top_category"]["category"],
                delta=f"{kpis['top_category']['percentage']:.1f}% share"
            )
        with col4:
            st.metric(
                label="Financial Health Score",
                value=f"{health['score']} / 100",
                delta=health["rating"]
            )

        st.markdown("---")

        # Visualizations Row 1
        cat_df = get_category_summary(filtered_df)
        monthly_df = get_monthly_trends(filtered_df)
        pay_df = get_payment_method_breakdown(filtered_df)
        daily_df = get_daily_spending_trend(filtered_df)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("Category-wise Spending (INR ₹)")
            fig_cat = plot_category_bar(cat_df)
            st.pyplot(fig_cat, use_container_width=True)

        with row1_col2:
            st.subheader("Monthly Spending Trajectory")
            fig_month = plot_monthly_trend_line(monthly_df)
            st.pyplot(fig_month, use_container_width=True)

        st.markdown("---")

        # Visualizations Row 2
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("Payment Method Utilization")
            fig_pay = plot_payment_method_pie(pay_df)
            st.pyplot(fig_pay, use_container_width=True)

        with row2_col2:
            st.subheader("Daily Spending & 7-Day Moving Average")
            fig_daily = plot_daily_trend(daily_df)
            st.pyplot(fig_daily, use_container_width=True)


# ----------------------------------------------------
# TAB 2: BUDGET VS ACTUAL
# ----------------------------------------------------
with tab_budget:
    st.title("🎯 Monthly Budget Tracking & Variance Analysis")
    st.write("Compare actual spending against category budget caps to eliminate overspending.")

    if df.empty:
        st.info("No data available.")
    else:
        # Month selector for budget analysis
        available_months = sorted(df["year_month"].unique(), reverse=True)
        selected_month = st.selectbox("Select Target Billing Month:", options=available_months)

        budget_df = get_budget_vs_actual(df, budgets, target_month=selected_month)
        
        col_b1, col_b2 = st.columns([1.2, 0.8])
        with col_b1:
            st.subheader(f"Spending vs. Budget for {selected_month}")
            fig_budget = plot_budget_vs_actual_bar(budget_df)
            st.pyplot(fig_budget, use_container_width=True)

        with col_b2:
            st.subheader("Budget Allocation & Utilization")
            for _, row in budget_df.iterrows():
                pct = row["pct_utilized"]
                cat_name = row["category"]
                act = row["actual"]
                bud = row["budget"]
                
                # Progress bar clamped to 1.0 for visual safety
                prog_val = min(1.0, act / bud) if bud > 0 else 1.0
                st.write(f"**{cat_name}**: ₹{act:,.0f} / ₹{bud:,.0f} ({pct}%)")
                
                if pct > 100:
                    st.progress(prog_val)
                    st.error(f"🚨 Over budget by ₹{row['variance']:,.0f}")
                elif pct >= 85:
                    st.progress(prog_val)
                    st.warning(f"⚠️ Close to limit! Remaining: ₹{-row['variance']:,.0f}")
                else:
                    st.progress(prog_val)
                    st.success(f"✅ On track! Remaining: ₹{-row['variance']:,.0f}")

        st.markdown("---")
        st.subheader("⚙️ Update Category Monthly Budgets")
        with st.form("update_budget_form"):
            b_cat = st.selectbox("Category to Update", options=list(budgets.keys()))
            current_val = budgets.get(b_cat, 5000.0)
            new_val = st.number_input("New Monthly Budget Cap (₹)", min_value=100.0, max_value=500000.0, value=current_val, step=500.0)
            save_b = st.form_submit_button("Save Budget Limit")
            if save_b:
                set_budget(DB_PATH, b_cat, new_val)
                st.success(f"Budget for '{b_cat}' updated to ₹{new_val:,.2f}!")
                st.rerun()


# ----------------------------------------------------
# TAB 3: ADD EXPENSE (WITH SMART AUTO-CATEGORIZATION)
# ----------------------------------------------------
with tab_add:
    st.title("➕ Record a New Transaction")
    st.write("Type a merchant name or note, and our **Smart Auto-Categorizer** will auto-detect the category!")

    with st.form("manual_expense_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            txn_date = st.date_input("Transaction Date", value=date.today())
            description_input = st.text_input(
                "Description / Merchant Note",
                placeholder="e.g. Starbucks cappuccino, Uber to office, Apollo pharmacy..."
            )
            # Run prediction on note
            pred_cat, conf = predict_category(description_input)

        with col_f2:
            amount_input = st.number_input("Amount (INR ₹)", min_value=1.0, max_value=1000000.0, value=250.0, step=50.0)
            payment_input = st.selectbox("Payment Instrument", options=["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"])

        # Category selection with intelligent pre-selection
        cat_options = [
            "Food & Dining", "Rent & Utilities", "Transportation", "Shopping",
            "Entertainment", "Healthcare", "Education", "Personal Care", "Miscellaneous"
        ]
        default_idx = cat_options.index(pred_cat) if pred_cat in cat_options else 0
        
        category_choice = st.selectbox(
            f"Category (Smart Auto-Detected: '{pred_cat}' [Confidence: {conf*100:.0f}%])",
            options=cat_options,
            index=default_idx
        )

        submit_btn = st.form_submit_button("💾 Save Expense to Database")

        if submit_btn:
            if not description_input:
                description_input = "General Expense"
            add_transaction(
                db_path=DB_PATH,
                date=txn_date.strftime("%Y-%m-%d"),
                category=category_choice,
                amount=amount_input,
                payment_method=payment_input,
                description=description_input
            )
            st.success(f"✅ Successfully recorded ₹{amount_input:,.2f} for '{description_input}' under '{category_choice}'!")
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")
    st.subheader("📂 Batch CSV Ingestion")
    st.caption("Upload your custom bank statement or manual CSV. Required columns: `date`, `amount`. Optional: `category`, `payment_method`, `description`.")
    uploaded_file = st.file_uploader("Upload CSV Statement", type=["csv"])
    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file)
            cleaned_user_df = clean_expense_data(user_df)
            st.write("Preview of cleaned records to ingest:", cleaned_user_df.head(5))
            if st.button("🚀 Ingest Records into SQLite"):
                inserted = bulk_insert_transactions(DB_PATH, cleaned_user_df)
                st.success(f"Successfully imported {inserted} transactions into database!")
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing uploaded CSV: {str(e)}")


# ----------------------------------------------------
# TAB 4: TRANSACTION LEDGER
# ----------------------------------------------------
with tab_ledger:
    st.title("📋 Transaction Ledger")
    st.write(f"Showing {len(filtered_df)} recorded transactions based on active filters.")

    if not filtered_df.empty:
        # Display table
        display_cols = ["id", "date", "description", "category", "amount", "payment_method", "created_at"]
        existing_cols = [c for c in display_cols if c in filtered_df.columns]
        
        st.dataframe(
            filtered_df[existing_cols].style.format({"amount": "₹{:,.2f}"}),
            use_container_width=True,
            height=400
        )

        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            # Download CSV
            csv_data = filtered_df[existing_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv_data,
                file_name="expenses_filtered_export.csv",
                mime="text/csv"
            )

        with col_d2:
            # Delete transaction
            with st.expander("🗑️ Delete a Transaction Record"):
                tx_to_del = st.number_input("Enter Transaction ID to delete", min_value=1, step=1)
                if st.button("Confirm Delete Record"):
                    if delete_transaction(DB_PATH, int(tx_to_del)):
                        st.success(f"Transaction ID {tx_to_del} removed.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Transaction ID not found.")


# ----------------------------------------------------
# TAB 5: EXECUTIVE REPORT
# ----------------------------------------------------
with tab_report:
    st.title("📄 Executive Financial Audit & Health Report")
    st.write("Automated financial report containing spending velocity, category metrics, and budget recommendations.")

    if not filtered_df.empty:
        report_text = generate_text_report(filtered_df, budgets)
        st.code(report_text, language="text")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.download_button(
                label="📥 Download Audit Report (.TXT)",
                data=report_text,
                file_name="financial_audit_report.txt",
                mime="text/plain"
            )
        with col_r2:
            st.download_button(
                label="📥 Download Audit Report (.MD)",
                data=f"# Financial Report\n\n```text\n{report_text}\n```",
                file_name="financial_audit_report.md",
                mime="text/markdown"
            )
