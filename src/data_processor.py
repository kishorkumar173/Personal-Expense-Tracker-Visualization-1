"""
data_processor.py
-----------------
Data Ingestion, Cleaning, Normalization, and Synthetic Generation Module.
Transforms raw inputs (manual or CSV) into analysis-ready Pandas DataFrames.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Optional
from src.categorizer import predict_category


VALID_PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]


def clean_expense_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes raw expense transaction data.
    
    Operations:
    1. Standardizes column names (lowercase, stripped).
    2. Enforces required fields ('date', 'amount').
    3. Auto-generates categories for missing/empty values using categorizer.
    4. Parses and validates date formats into standard YYYY-MM-DD.
    5. Strips currency symbols and casts amounts to positive floats.
    6. Adds feature-engineered time dimensions (Year, Month, YearMonth, DayOfWeek).
    """
    if df.empty:
        return df

    # Normalize column names
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    # Map possible alternative column names to canonical schema
    column_mapping = {
        "txn_date": "date",
        "transaction_date": "date",
        "cost": "amount",
        "price": "amount",
        "spend": "amount",
        "payment_mode": "payment_method",
        "mode": "payment_method",
        "method": "payment_method",
        "desc": "description",
        "note": "description",
        "merchant": "description"
    }
    df.rename(columns=column_mapping, inplace=True)

    # Check mandatory columns
    if "date" not in df.columns or "amount" not in df.columns:
        raise ValueError("Dataset must contain at least 'date' and 'amount' columns.")

    # 1. Clean Amount
    if df["amount"].dtype == object:
        # Remove currency symbols ($, Rs., INR, ₹) and commas
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] > 0]  # Only keep positive expenses

    # 2. Clean Dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # 3. Clean Description
    if "description" not in df.columns:
        df["description"] = "General Expense"
    else:
        df["description"] = df["description"].fillna("General Expense").astype(str).str.strip()

    # 4. Clean & Auto-fill Category
    if "category" not in df.columns:
        df["category"] = ""
    df["category"] = df["category"].fillna("").astype(str).str.strip()

    # Auto-categorize empty categories
    for idx, row in df.iterrows():
        cat = str(row["category"]).strip()
        if not cat or cat.lower() in ["", "none", "nan", "uncategorized", "other"]:
            pred_cat, _ = predict_category(row["description"])
            df.at[idx, "category"] = pred_cat

    # 5. Clean Payment Method
    if "payment_method" not in df.columns:
        df["payment_method"] = "UPI"
    else:
        df["payment_method"] = df["payment_method"].fillna("UPI").astype(str).str.strip()
        # Default fallback if unknown
        df["payment_method"] = df["payment_method"].apply(
            lambda x: x if x in VALID_PAYMENT_METHODS else "UPI"
        )

    # 6. Feature Engineering (Time intelligence)
    date_dt = pd.to_datetime(df["date"])
    df["year"] = date_dt.dt.year
    df["month"] = date_dt.dt.month
    df["month_name"] = date_dt.dt.strftime("%b %Y")
    df["year_month"] = date_dt.dt.strftime("%Y-%m")
    df["day"] = date_dt.dt.day
    df["day_name"] = date_dt.dt.strftime("%A")
    df["is_weekend"] = date_dt.dt.dayofweek >= 5

    # Sort in chronological order
    df = df.sort_values(by="date", ascending=True).reset_index(drop=True)
    return df


def generate_synthetic_expenses(
    n_transactions: int = 180,
    start_date: str = "2026-06-01",
    end_date: str = "2026-11-20"
) -> pd.DataFrame:
    """
    Generates a realistic, diverse synthetic dataset simulating 6 months of personal expenses.
    Ideal for students, demos, proof-of-work, and offline analysis.
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta_days = (end_dt - start_dt).days

    merchants_and_catalogs = [
        # (Description, Category, Min_Amt, Max_Amt, Weight)
        ("Starbucks Cappuccino & Croissant", "Food & Dining", 250, 650, 15),
        ("Swiggy Biryani & Dinner Order", "Food & Dining", 300, 950, 20),
        ("Zomato Pizza Delivery", "Food & Dining", 400, 1200, 18),
        ("Blinkit Supermarket Groceries", "Food & Dining", 600, 3200, 25),
        ("Local Supermarket Weekly Groceries", "Food & Dining", 1200, 4500, 20),
        ("Apartment Monthly Rent", "Rent & Utilities", 12000, 15000, 6),
        ("State Electricity Board Power Bill", "Rent & Utilities", 1100, 2800, 6),
        ("Airtel Fiber Broadband Internet Bill", "Rent & Utilities", 899, 1199, 6),
        ("Piped Cooking Gas Utility Bill", "Rent & Utilities", 450, 950, 6),
        ("Uber City Cab Ride", "Transportation", 180, 750, 20),
        ("Ola Auto Commute to College/Office", "Transportation", 80, 260, 22),
        ("Petrol Refill Shell Fuel Station", "Transportation", 500, 2500, 15),
        ("Metro Smart Card Recharge", "Transportation", 300, 1000, 10),
        ("Amazon Prime Shopping Order", "Shopping", 450, 3500, 14),
        ("Flipkart Electronic Gadget", "Shopping", 800, 6500, 8),
        ("Zara Casual Clothing Store", "Shopping", 1200, 4800, 6),
        ("Myntra Footwear & Accessories", "Shopping", 700, 3200, 9),
        ("Netflix Monthly Premium Subscription", "Entertainment", 649, 649, 6),
        ("Spotify Premium Music Family Plan", "Entertainment", 179, 179, 6),
        ("PVR Cinema Movie Weekend Tickets & Popcorn", "Entertainment", 600, 1600, 10),
        ("Steam Game Festival Purchase", "Entertainment", 350, 2200, 5),
        ("Apollo Pharmacy Prescription Medicines", "Healthcare", 250, 1450, 8),
        ("Dental Checkup & Cleaning Consultation", "Healthcare", 800, 2500, 3),
        ("Diagnostic Lab Blood Work & Tests", "Healthcare", 900, 2800, 3),
        ("Udemy Python & Data Engineering Course", "Education", 499, 1299, 6),
        ("Technical Books & College Stationery", "Education", 350, 1800, 7),
        ("Cult.fit Fitness & Gym Membership", "Personal Care", 1500, 2500, 5),
        ("Salon Haircut & Grooming Services", "Personal Care", 300, 1200, 8),
        ("Courier & Miscellaneous Essentials", "Miscellaneous", 120, 650, 10)
    ]

    descriptions = [item[0] for item in merchants_and_catalogs]
    categories = [item[1] for item in merchants_and_catalogs]
    weights = [item[4] for item in merchants_and_catalogs]

    data = []
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
    payment_weights = [0.45, 0.25, 0.15, 0.10, 0.05]

    for _ in range(n_transactions):
        # Pick merchant template
        chosen_idx = random.choices(range(len(merchants_and_catalogs)), weights=weights)[0]
        desc, cat, min_amt, max_amt, _ = merchants_and_catalogs[chosen_idx]

        # Generate realistic amount (round to 2 decimals or 10s)
        amt = round(random.uniform(min_amt, max_amt), 2)
        if amt > 500:
            amt = round(amt, -1)  # realistic clean numbers like 750, 1200

        # Generate random date in range
        rand_offset = random.randint(0, delta_days)
        txn_date = (start_dt + timedelta(days=rand_offset)).strftime("%Y-%m-%d")

        # Pick payment method
        pay_method = random.choices(payment_methods, weights=payment_weights)[0]

        data.append({
            "date": txn_date,
            "category": cat,
            "amount": amt,
            "payment_method": pay_method,
            "description": desc
        })

    df = pd.DataFrame(data)
    return clean_expense_data(df)
