from datetime import datetime, timedelta
from models.database import SessionLocal, Invoice

def add_new_invoice(data):
    """Adds invoice and schedules Stage-1 for immediate processing."""
    db = SessionLocal()
    
    # Create the invoice record
    new_inv = Invoice(
        invoice_no=data['invoice_no'],
        client_name=data['client_name'],
        amount=data['amount'],
        due_date=data['due_date'],
        contact_email=data['contact_email'],
        # Set next_followup_due to 'now' so it triggers immediately
        next_followup_due=datetime.now(),
        status="Active"
    )
    
    db.add(new_inv)
    db.commit()
    db.close()
    
    # Ideally, call the agent for Stage 1 here or let the next cron tick pick it up