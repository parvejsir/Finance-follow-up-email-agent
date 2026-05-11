import streamlit as st
import pandas as pd
import os
from models.database import init_db, SessionLocal, Invoice
from agents.graph import build_v2_graph
from services.scheduler import start_scheduler
from services.invoice_service import add_new_invoice
from ui.dashboard import render_stats, render_human_review_queue, render_audit_logs
from utils.visualizer import save_graph_image
from dotenv import load_dotenv

# 1. INITIALIZATION
load_dotenv()
init_db()
start_scheduler()
agent_app = build_v2_graph()
save_graph_image(agent_app, "graph.png")

# 2. PAGE CONFIG
st.set_page_config(page_title="AI Enablement Finance", layout="wide", page_icon="💰")

# 3. SIDEBAR
st.sidebar.title("AI Enablement")
mode = st.sidebar.radio("Mode", ["Auto-Process", "Human Review"])

if st.sidebar.button("🗑️ Reset Database"):
    db = SessionLocal()
    db.query(Invoice).delete()
    db.commit()
    db.close()
    st.rerun()

# 4. BRANDING HEADERS
st.title("💰 AI Enablement: Finance Follow-Up")
st.markdown("Strategic Information Management & Automated Credit Routing System.")

render_stats()

tab1, tab2, tab3 = st.tabs(["📊 Management", "👀 Review Queue", "🛡️ Audit"])

with tab1:
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📥 Data Ingestion")
        uploaded_file = st.file_uploader("Upload Invoices", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            if st.button("Sync to System"):
                for _, row in df.iterrows():
                    add_new_invoice({"invoice_no": str(row['Invoice No.']), "client_name": row['Client Name'], "amount": row['Amount'], "due_date": pd.to_datetime(row['Due Date']), "contact_email": row['Contact Email']})
                st.success("Data Synced.")

    with col_b:
        st.subheader("⚙️ Agent Interpretation")
        st.image("graph.png", caption="Multi-Agent Workflow Path")
        
        if st.button("🚀 Run Follow-up Engine", type="primary"):
            from services.scheduler import process_eligible_invoices
            # Interpreted Processing Visualization
            with st.status("Agent initialized... checking eligible invoices") as status:
                st.write("🔍 Identifying overdue accounts...")
                process_eligible_invoices()
                status.update(label="Engine Run Complete", state="complete")
            st.rerun()

    st.divider()
    db = SessionLocal()
    current_invoices = pd.read_sql(db.query(Invoice).statement, db.bind)
    st.dataframe(current_invoices, use_container_width=True)
    db.close()

with tab2:
    if mode == "Human Review":
        render_human_review_queue(agent_app)
    else:
        st.info("Switch to 'Human Review' mode in sidebar to approve drafts.")

with tab3:
    render_audit_logs()