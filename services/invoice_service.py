from datetime import datetime
from models.database import SessionLocal, Invoice

def add_new_invoice(data):
    """Inserts a fresh credit profile record including its telephone matrix."""
    db = SessionLocal()
    existing = db.query(Invoice).filter(Invoice.invoice_no == data['invoice_no']).first()
    
    if not existing:
        new_inv = Invoice(
            invoice_no=data['invoice_no'],
            client_name=data['client_name'],
            amount=data['amount'],
            due_date=data['due_date'],
            contact_email=data['contact_email'],
            contact_phone=data.get('contact_phone'), # <-- Capture the phone values
            follow_up_count=data.get('follow_up_count', 0), 
            next_followup_due=datetime.now(),
            status="Active"
        )
        db.add(new_inv)
        db.commit()
    db.close()