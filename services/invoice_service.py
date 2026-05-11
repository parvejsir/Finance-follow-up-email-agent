from datetime import datetime, timedelta
from models.database import SessionLocal, Invoice

def add_new_invoice(data):
    db = SessionLocal()
    # Check if exists
    existing = db.query(Invoice).filter(Invoice.invoice_no == data['invoice_no']).first()
    if not existing:
        new_inv = Invoice(
            invoice_no=data['invoice_no'],
            client_name=data['client_name'],
            amount=data['amount'],
            due_date=data['due_date'],
            contact_email=data['contact_email'],
            follow_up_count=data.get('follow_up_count', 0), # Added this line
            next_followup_due=datetime.now() # Schedule immediately
        )
        db.add(new_inv)
        db.commit()
    db.close()
    
    # Ideally, call the agent for Stage 1 here or let the next cron tick pick it up