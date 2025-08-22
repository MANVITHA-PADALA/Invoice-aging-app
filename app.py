import datetime as dt
import pandas as pd
import streamlit as st
from db import get_engine, fetch_invoices, add_payment, top5_outstanding

st.set_page_config(page_title="Invoice Aging", layout="wide")
st.title("Invoice Aging & Collections Dashboard")

engine = get_engine()
today = dt.date.today().isoformat()

# --- Filters ---
with st.sidebar:
    st.header("Filters")
    customers = pd.read_sql("SELECT customer_id, name FROM customers ORDER BY name", engine)
    cust_map = {"All": None}
    cust_map.update({row["name"]: int(row["customer_id"]) for _, row in customers.iterrows()})
    customer_name = st.selectbox("Customer", list(cust_map.keys()), index=0)
    customer_id = cust_map[customer_name]

    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("Start (Invoice Date)", value=None)
    with col_b:
        end_date = st.date_input("End (Invoice Date)", value=None)

    if start_date and end_date and start_date > end_date:
        st.error("Start date cannot be after end date.")

invoices = fetch_invoices(
    engine,
    customer_id=customer_id,
    start_date=start_date.isoformat() if start_date else None,
    end_date=end_date.isoformat() if end_date else None,
    today=today
)
df = pd.DataFrame(invoices)

# --- KPIs ---
total_invoiced = df["amount"].sum() if not df.empty else 0
total_received = df["total_paid"].sum() if not df.empty else 0
total_outstanding = df["outstanding"].sum() if not df.empty else 0
overdue_outstanding = df.loc[(df["outstanding"] > 0) & (df["aging_bucket"].isin(["0-30","31-60","61-90","90+"])), "outstanding"].sum()
pct_overdue = (overdue_outstanding / total_outstanding * 100) if total_outstanding else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Invoiced", f"${total_invoiced:,.2f}")
k2.metric("Total Received", f"${total_received:,.2f}")
k3.metric("Total Outstanding", f"${total_outstanding:,.2f}")
k4.metric("% Overdue", f"{pct_overdue:.1f}%")

st.divider()

# --- Table ---
st.subheader("Invoices")
if df.empty:
    st.info("No invoices found for the selected filters.")
else:
    def _row_style(row):
        overdue_buckets = {"0-30","31-60","61-90","90+"}
        if row["outstanding"] > 0 and row["aging_bucket"] in overdue_buckets:
            return ["background-color: #ffeef0"] * len(row)
        return [""] * len(row)
    styled = df[[
        "invoice_id","customer_name","invoice_date","due_date",
        "amount","total_paid","outstanding","aging_bucket"
    ]].style.apply(_row_style, axis=1)
    st.dataframe(styled, hide_index=True, use_container_width=True)

# --- Record Payment ---
st.subheader("Record Payment")
with st.form("record_payment"):
    open_invoices = df[df["outstanding"] > 0][["invoice_id","customer_name","outstanding"]]
    if open_invoices.empty:
        st.caption("All invoices are fully paid for the current filter.")
    else:
        options = {
            f'INV-{r.invoice_id} | {r.customer_name} | Outstanding ${r.outstanding:,.2f}': int(r.invoice_id)
            for r in open_invoices.itertuples(index=False)
        }
        inv_label = st.selectbox("Invoice", list(options.keys()))
        pay_amount = st.number_input("Amount", min_value=0.01, step=0.01)
        pay_date = st.date_input("Payment Date", value=dt.date.today())
        submitted = st.form_submit_button("Save Payment")
        if submitted:
            try:
                add_payment(engine, options[inv_label], pay_date.isoformat(), float(pay_amount))
                st.success("Payment recorded.")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

st.divider()

st.subheader("Top 5 Customers by Outstanding")
top5 = pd.DataFrame(top5_outstanding(engine, today=today))
if top5.empty:
    st.caption("No outstanding balances.")
else:
    st.bar_chart(top5.set_index("customer_name")["total_outstanding"])
