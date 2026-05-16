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

# Sync current processing state globally for LangGraph conditional branches
st.session_state["mode"] = mode

if st.sidebar.button("🗑️ Reset Database", use_container_width=True):
    db = SessionLocal()
    db.query(Invoice).delete()
    db.commit()
    db.close()
    st.sidebar.success("Database wiped successfully!")
    st.rerun()

# 4. BRANDING HEADERS
st.title("💰 AI Enablement: Finance Follow-Up")
st.markdown("Strategic Information Management & Automated Credit Routing System.")

render_stats()

# 5. WORKFLOW MIGRATION INTERFACE
tab1, tab2, tab3 = st.tabs(["📊 Management", "👀 Review Queue", "🛡️ Audit"])

with tab1:
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📥 Data Ingestion")
        uploaded_file = st.file_uploader("Upload Invoices", type=["xlsx", "csv"])
        
        if uploaded_file:
            # Multi-extension file interpreter layer
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.dataframe(df.head(5), use_container_width=True)

            # CRITICAL STRUCTURAL RE-ALIGNMENT: Nested safely back under file layout context
            if st.button("Sync to System", use_container_width=True):
                for _, row in df.iterrows():
                    excel_count = int(row.get('Follow Up Count', 0))
                    
                    invoice_data = {
                        "invoice_no": str(row['Invoice No.']),
                        "client_name": row['Client Name'],
                        "amount": float(row['Amount']),
                        "due_date": pd.to_datetime(row['Due Date']),
                        "contact_email": row['Contact Email'],
                        "contact_phone": str(row['Contact Phone']).strip() if 'Contact Phone' in row and pd.notna(row['Contact Phone']) else None,
                        "follow_up_count": excel_count 
                    }
                    add_new_invoice(invoice_data)
                # Green notification flag is now securely restored to the interface layout view!
                # 1. Show an immediate popup notification that survives page reruns
                st.toast(f"✅ Synced {len(df)} records into the pipeline!", icon="🚀")
                # 2. Display the green success block on the layout
                st.success(f"✅ Successfully synced {len(df)} records into multi-channel routing pipeline.")
                # 3. Use st.session_state to hold the view rather than an aggressive hard rerun
                st.info("🔄 Refreshing metrics... Scroll down to view the active database updates.")

    with col_b:
        st.subheader("⚙️ Agent Interpretation")
        st.image("graph.png", caption="Multi-Agent Workflow Path")
        
        if st.button("🚀 Run Follow-up Engine", type="primary", use_container_width=True):
            from services.scheduler import process_eligible_invoices
            with st.status("Agent initialized... executing credit check logic") as status:
                st.write("🔍 Extracting current timeline schedules...")
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