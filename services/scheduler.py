from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models.database import SessionLocal, Invoice
from agents.graph import build_v2_graph
import streamlit as st

scheduler = BackgroundScheduler()

def process_eligible_invoices():
    """
    Core engine to process overdue invoices.
    Optimized to cache drafts in DB to prevent Gemini Quota issues.
    """
    db = SessionLocal()
    now = datetime.now()
    
    # Filter for invoices that are due for a follow-up
    eligible = db.query(Invoice).filter(
        Invoice.status == "Active",
        Invoice.next_followup_due <= now
    ).all()
    
    if not eligible:
        db.close()
        return

    agent = build_v2_graph()
    
    # We check the UI session state to see if we are in Human Review mode
    # If this is running as a background CRON, default to Auto-Process
    mode = "Auto-Process"
    try:
        if "mode" in st.session_state:
            mode = st.session_state["mode"]
    except:
        pass

    for inv in eligible:
        # Prepare state for the agent
        state = {
            "invoice_no": inv.invoice_no,
            "client_name": inv.client_name,
            "amount": inv.amount,
            "due_date": inv.due_date.strftime("%Y-%m-%d"),
            "contact_email": inv.contact_email,
            "follow_up_count": inv.follow_up_count,
            "current_stage": inv.follow_up_count + 1,
            "retry_count": inv.retry_count or 0,
            "generated_content": inv.last_generated_email # Pass existing draft if any
        }
        
        # 1. RUN GENERATION & VALIDATION
        # We only invoke the generator if no draft exists to save QUOTA
        output = agent.invoke(state)
        
        # 2. CACHE THE RESULT
        inv.last_generated_email = output.get("final_email_body")
        db.commit()

        # 3. AUTO-SEND LOGIC
        # Only move to the 'sender' logic if mode is Auto-Process
        if mode == "Auto-Process":
            from agents.nodes import sender_agent
            sender_agent(output)
            
    db.close()

def start_scheduler():
    """Starts the background cron job for 10:00 AM daily."""
    if not scheduler.running:
        # Avoid duplicate job IDs if scheduler restarts
        if not scheduler.get_job('daily_finance_check'):
            scheduler.add_job(
                process_eligible_invoices, 
                'cron', 
                hour=10, 
                minute=0, 
                id='daily_finance_check'
            )
        scheduler.start()