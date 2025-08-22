import os
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv()

def get_engine() -> Engine:
    url = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600)

def fetch_invoices(engine: Engine, customer_id=None, start_date=None, end_date=None, today=None):
    if not today:
        today = dt.date.today().isoformat()
    where = ["1=1"]
    params = {"today": today}
    if customer_id:
        where.append("i.customer_id = :customer_id")
        params["customer_id"] = customer_id
    if start_date:
        where.append("i.invoice_date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        where.append("i.invoice_date <= :end_date")
        params["end_date"] = end_date
    sql = f"""
    SELECT
      i.invoice_id,
      c.name AS customer_name,
      i.invoice_date,
      i.due_date,
      i.amount,
      IFNULL(SUM(p.amount), 0.00) AS total_paid,
      GREATEST(i.amount - IFNULL(SUM(p.amount), 0.00), 0.00) AS outstanding,
      CASE
        WHEN GREATEST(i.amount - IFNULL(SUM(p.amount), 0.00), 0.00) <= 0 THEN 'Paid'
        ELSE compute_aging_bucket(i.due_date, :today)
      END AS aging_bucket
    FROM invoices i
    JOIN customers c ON c.customer_id = i.customer_id
    LEFT JOIN payments p ON p.invoice_id = i.invoice_id
    WHERE {" AND ".join(where)}
    GROUP BY i.invoice_id, c.name, i.invoice_date, i.due_date, i.amount
    ORDER BY i.invoice_date DESC, i.invoice_id DESC;
    """
    with engine.connect() as conn:
        return conn.execute(text(sql), params).mappings().all()

def add_payment(engine: Engine, invoice_id: int, payment_date: str, amount: float):
    if amount <= 0:
        raise ValueError("Payment must be > 0")
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT i.amount AS invoice_amount, IFNULL(SUM(p.amount), 0.00) AS total_paid
            FROM invoices i
            LEFT JOIN payments p ON p.invoice_id = i.invoice_id
            WHERE i.invoice_id = :invoice_id
            FOR UPDATE
        """), {"invoice_id": invoice_id}).first()
        if row is None:
            raise ValueError("Invoice not found")
        outstanding = float(row.invoice_amount) - float(row.total_paid)
        if amount > outstanding + 1e-6:
            raise ValueError(f"Payment {amount:.2f} exceeds outstanding {outstanding:.2f}")
        conn.execute(text("""
            INSERT INTO payments (invoice_id, payment_date, amount)
            VALUES (:invoice_id, :payment_date, :amount)
        """), {"invoice_id": invoice_id, "payment_date": payment_date, "amount": amount})

def top5_outstanding(engine: Engine, today=None):
    if not today:
        today = dt.date.today().isoformat()
    sql = """
    SELECT c.customer_id, c.name AS customer_name,
           SUM(GREATEST(i.amount - IFNULL(paid.total_paid, 0.00), 0.00)) AS total_outstanding
    FROM customers c
    JOIN invoices i ON i.customer_id = c.customer_id
    LEFT JOIN (SELECT invoice_id, SUM(amount) AS total_paid FROM payments GROUP BY invoice_id) paid
    ON paid.invoice_id = i.invoice_id
    GROUP BY c.customer_id, c.name
    HAVING total_outstanding > 0
    ORDER BY total_outstanding DESC
    LIMIT 5;
    """
    with get_engine().connect() as conn:
        return conn.execute(text(sql), {"today": today}).mappings().all()
