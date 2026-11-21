"""
database.py
-----------
SQLite Database Management Module for Personal Expense Tracker.
Handles table schemas, connection pooling, and CRUD transactions.
"""

import sqlite3
import os
import pandas as pd
from typing import Dict, Optional, List


def get_db_connection(db_path: str = "expenses.db") -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = "expenses.db") -> None:
    """
    Initializes database tables:
    1. transactions: Records each expense item.
    2. budgets: Monthly spending budget thresholds per category.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Create Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            payment_method TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create Budgets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            monthly_limit REAL NOT NULL CHECK(monthly_limit > 0)
        );
    """)

    # Populate default realistic budgets if table is empty
    cursor.execute("SELECT COUNT(*) FROM budgets;")
    if cursor.fetchone()[0] == 0:
        default_budgets = [
            ("Food & Dining", 10000.0),
            ("Rent & Utilities", 15000.0),
            ("Transportation", 4000.0),
            ("Shopping", 6000.0),
            ("Entertainment", 3500.0),
            ("Healthcare", 3000.0),
            ("Education", 4000.0),
            ("Personal Care", 2500.0),
            ("Miscellaneous", 2000.0)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO budgets (category, monthly_limit)
            VALUES (?, ?);
        """, default_budgets)

    conn.commit()
    conn.close()


def add_transaction(
    db_path: str,
    date: str,
    category: str,
    amount: float,
    payment_method: str,
    description: str = ""
) -> int:
    """Inserts a single transaction record into SQLite."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (date, category, amount, payment_method, description)
        VALUES (?, ?, ?, ?, ?);
    """, (date, category, float(amount), payment_method, description.strip()))
    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tx_id


def bulk_insert_transactions(db_path: str, df: pd.DataFrame) -> int:
    """Inserts a pandas DataFrame of transactions into SQLite."""
    if df.empty:
        return 0

    required_cols = {"date", "category", "amount", "payment_method"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")

    if "description" not in df.columns:
        df["description"] = "N/A"

    records = [
        (
            str(row["date"]),
            str(row["category"]),
            float(row["amount"]),
            str(row["payment_method"]),
            str(row["description"])
        )
        for _, row in df.iterrows()
    ]

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO transactions (date, category, amount, payment_method, description)
        VALUES (?, ?, ?, ?, ?);
    """, records)
    inserted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return inserted_count


def get_all_transactions(db_path: str = "expenses.db") -> pd.DataFrame:
    """Fetches all transactions from SQLite as a clean pandas DataFrame."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    query = """
        SELECT id, date, category, amount, payment_method, description, created_at
        FROM transactions
        ORDER BY date DESC, id DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def delete_transaction(db_path: str, tx_id: int) -> bool:
    """Deletes a transaction by primary key ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?;", (tx_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_budgets(db_path: str = "expenses.db") -> Dict[str, float]:
    """Retrieves all category budget limits as a dictionary."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT category, monthly_limit FROM budgets;")
    rows = cursor.fetchall()
    conn.close()
    return {row["category"]: float(row["monthly_limit"]) for row in rows}


def set_budget(db_path: str, category: str, monthly_limit: float) -> None:
    """Inserts or updates a monthly budget for a category."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (category, monthly_limit)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit;
    """, (category, float(monthly_limit)))
    conn.commit()
    conn.close()


def clear_all_transactions(db_path: str = "expenses.db") -> None:
    """Clears all records in the transactions table (useful for fresh resets)."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions;")
    conn.commit()
    conn.close()
