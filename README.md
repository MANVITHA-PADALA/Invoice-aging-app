# Invoice Aging & Collections Dashboard

A Streamlit + MySQL application to track invoices, payments, outstanding balances, and aging buckets.

## Features
- List invoices with customer, amount, total paid, outstanding, and aging.
- Record payments (partial or full).
- KPI tiles: Total Invoiced, Total Received, Total Outstanding, % Overdue.
- Table of invoices with overdue highlighting.
- Top 5 customers by outstanding chart.
- Unit tests for compute_aging_bucket.

## Setup
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Create `.env` with DB credentials:
   ```env
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_DB=invoice_db
   MYSQL_USER=root
   MYSQL_PASSWORD=secret
   ```
3. Load schema and seed data:
   ```bash
   mysql -u root -p invoice_db < schema.sql
   mysql -u root -p invoice_db < seed.sql
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Screenshots
See `screenshots/` folder.
