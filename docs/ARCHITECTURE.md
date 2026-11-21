# System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

The **Personal Expense Tracker & Data Visualization System** is architected as an industry-standard, multi-tier data pipeline designed for local persistence, robust ETL (Extract, Transform, Load), analytical aggregation, statistical reporting, and interactive web dashboarding.

```
+-------------------------------------------------------------------------------+
|                             DATA INGESTION TIER                               |
|  [Manual UI / CLI Entry]          [Batch Bank Statement CSV]    [Synthetic]   |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                        SMART PREPROCESSING & ETL TIER                         |
|   src/categorizer.py                 |   src/data_processor.py                |
|   - Regex Tokenization Matching      |   - Null & Dirty Value Imputation      |
|   - Heuristic Category Classification|   - Datetime Normalization (ISO 8601)  |
|   - Fallback Rule Engine             |   - Feature Engineering (Time Series)  |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                           PERSISTENCE STORAGE TIER                            |
|   src/database.py                                                             |
|   - SQLite Relational Database (`expenses.db`)                                |
|   - ACID Compliant Transactions Table (`id`, `date`, `amount`, `cat`, etc.)   |
|   - Category Monthly Budgets Table (`category`, `monthly_limit`)              |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                            ANALYTICAL ENGINE TIER                             |
|   src/analytics.py                                                            |
|   - Summary KPIs (Burn Rate, Ticket Size, Top Category)                       |
|   - Dimensional Aggregations (Category, Month-over-Month, Payment Methods)    |
|   - Time Series Rolling 7-Day Averages                                        |
|   - Budget Variance Analysis (Over/Under Budget Thresholds)                   |
|   - Financial Health Scoring Algorithm (0 - 100)                              |
+---------------------------------------+---------------------------------------+
                                        |
                     +------------------+------------------+
                     |                                     |
                     v                                     v
+------------------------------------+   +------------------------------------+
|       PRESENTATION & DASHBOARD     |   |         AUTOMATED AUDIT TIER       |
|   app.py (Streamlit Web App)       |   |   src/report_generator.py          |
|   - Interactive Date & Cat Filters |   |   - Plain Text Audit (.txt)        |
|   - Real-time KPI Metric Badges    |   |   - Formatted Executive (.md)      |
|   - Dynamic Matplotlib Charts      |   |   - Aggregated CSV Tables (.csv)   |
|   - Live Transaction CRUD Ledger   |   |   - Actionable Advisory Insights   |
+------------------------------------+   +------------------------------------+
```

---

## 2. Database Schema (SQLite)

### Table 1: `transactions`
Stores immutable individual financial outflows.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique transaction sequence identifier |
| `date` | TEXT | NOT NULL | Transaction date in ISO format (`YYYY-MM-DD`) |
| `category` | TEXT | NOT NULL | Expense category |
| `amount` | REAL | NOT NULL, CHECK(amount > 0) | Outflow value in currency units |
| `payment_method`| TEXT | NOT NULL | Payment instrument (`UPI`, `Card`, etc.) |
| `description` | TEXT | DEFAULT 'General Expense' | Raw merchant name or transaction memo |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Audit log timestamp |

### Table 2: `budgets`
Maintains monthly expenditure thresholds per category.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Budget row identifier |
| `category` | TEXT | UNIQUE NOT NULL | Category name |
| `monthly_limit` | REAL | NOT NULL, CHECK(monthly_limit > 0)| Monthly allocated cap |

---

## 3. Data Processing Pipeline (ETL)

1. **Extraction**: Accepts raw CSVs, synthetic data generators, or manual forms.
2. **Standardization**: Trims whitespace, lowercases keys, strips currency characters (`₹`, `$`, `,`).
3. **Imputation & Heuristics**: If `category` is empty, searches `description` for merchant tokens (e.g. "zomato" -> "Food & Dining").
4. **Enrichment**: Derives `year`, `month`, `month_name`, `day`, `day_name`, and `is_weekend`.
5. **Persistence**: Performs atomic batch insertion into SQLite.
