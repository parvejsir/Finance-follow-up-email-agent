import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import init_db, SessionLocal, Invoice
from src.utils import is_eligible_for_followup
from src.graph import build_graph
from dotenv import load_dotenv

load_dotenv()
init_db()

st.set_page_config(page_title="Finance Credit Agent", layout="wide")
st.title("💰 Finance Credit Follow-Up Agent")

# Sidebar - Settings
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Database"):
        db = SessionLocal()
        db.query(Invoice).delete()
        db.commit()
        db.close()
        st.warning("Database cleared.")

# 1. Upload Section
uploaded_file = st.file_uploader("Upload Overdue Invoices (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Preview Uploaded Data", df)
    
    if st.button("Sync to Database"):
        db = SessionLocal()
        for _, row in df.iterrows():
            # Using the exact names from your Excel preview: 
            # "Invoice No.", "Client Name", "Amount", etc.
            inv_id = str(row['Invoice No.'])
            
            existing = db.query(Invoice).filter(Invoice.invoice_no == inv_id).first()
            if not existing:
                new_inv = Invoice(
                    invoice_no=inv_id,
                    client_name=row['Client Name'],
                    amount=row['Amount'],
                    due_date=pd.to_datetime(row['Due Date']),
                    contact_email=row['Contact Email'],
                    follow_up_count=row.get('Follow-up Count', 0)
                )
                db.add(new_inv)
        db.commit()
        db.close()
        st.success("Database Updated!")

# 2. Processing Section
st.divider()
st.subheader("Process Follow-ups")

if st.button("Run Follow-up Engine"):
    db = SessionLocal()
    # Get all active invoices
    active_invoices = db.query(Invoice).filter(Invoice.status == "Active").all()
    
    agent = build_graph()
    
    results = []
    for inv in active_invoices:
        # THE 7-DAY LOGIC
        if is_eligible_for_followup(inv.last_email_send_timestamp):
            st.info(f"Processing {inv.client_name} (Inv: {inv.invoice_no})...")
            
            # Prepare state for LangGraph
            initial_state = {
                "invoice_no": inv.invoice_no,
                "client_name": inv.client_name,
                "amount": inv.amount,
                "due_date": inv.due_date.strftime("%Y-%m-%d"),
                "contact_email": inv.contact_email,
                "follow_up_count": inv.follow_up_count
            }
            
            # Run the Graph
            final_output = agent.invoke(initial_state)
            results.append(final_output)
        else:
            st.write(f"⏩ {inv.client_name} skip: Last email was less than 7 days ago.")

    db.close()
    if results:
        st.success(f"Batch complete. Processed {len(results)} invoices.")

# 3. View Current Status
st.divider()
st.subheader("Database Status")
db = SessionLocal()
current_db_df = pd.read_sql(db.query(Invoice).statement, db.bind)
st.dataframe(current_db_df)
db.close()