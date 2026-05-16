from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models.database import SessionLocal, Invoice
from agents.graph import build_v2_graph
import streamlit as st

scheduler = BackgroundScheduler()

def process_eligible_invoices():
    db = SessionLocal()
    now = datetime.now()
    
    eligible = db.query(Invoice).filter(
        Invoice.status == "Active",
        Invoice.next_followup_due <= now
    ).all()
    
    if not eligible:
        db.close()
        return

    agent = build_v2_graph()
    
    current_mode = "Auto-Process"
    try:
        if "mode" in st.session_state:
            current_mode = st.session_state["mode"]
    except:
        pass

    for inv in eligible:
        state = {
            "invoice_no": inv.invoice_no,
            "client_name": inv.client_name,
            "amount": inv.amount,
            "due_date": inv.due_date.strftime("%Y-%m-%d"),
            "contact_email": inv.contact_email,
            "contact_phone": inv.contact_phone, # <-- Map the text destination data
            "follow_up_count": inv.follow_up_count,
            "current_stage": inv.follow_up_count + 1,
            "retry_count": inv.retry_count or 0,
            "generated_content": inv.last_generated_email,
            "processing_mode": current_mode 
        }
        
        output = agent.invoke(state)
        
        inv.last_generated_email = output.get("final_email_body")
        db.commit()
            
    db.close()

def start_scheduler():
    if not scheduler.running:
        if not scheduler.get_job('daily_finance_check'):
            scheduler.add_job(process_eligible_invoices, 'cron', hour=10, minute=0, id='daily_finance_check')
        scheduler.start()