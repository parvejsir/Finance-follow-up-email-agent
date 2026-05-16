from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String, unique=True)
    client_name = Column(String)
    amount = Column(Float)
    due_date = Column(DateTime)
    contact_email = Column(String)
    contact_phone = Column(String, nullable=True) # <-- New column for SMS routing
    
    # Logic Tracking
    follow_up_count = Column(Integer, default=0)
    last_email_send_timestamp = Column(DateTime, nullable=True)
    next_followup_due = Column(DateTime, nullable=True)
    status = Column(String, default="Active") 
    
    # HITL / Quota Protection Cache
    last_generated_email = Column(Text, nullable=True)
    approval_status = Column(String, default="pending") 
    retry_count = Column(Integer, default=0)
    human_approved = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = 'email_audit_logs'
    
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String)
    client_name = Column(String)
    follow_up_stage = Column(Integer)
    tone_used = Column(String)      
    retry_count = Column(Integer)   
    generated_email = Column(Text)
    final_sent_email = Column(Text, nullable=True)
    human_feedback = Column(Text, nullable=True)
    send_status = Column(String) 
    generated_at = Column(DateTime, default=datetime.now)
    sent_at = Column(DateTime, nullable=True)
    llm_model = Column(String, default="gemini-2.5-flash")
    error_message = Column(Text, nullable=True)

# Connection - AI Enablement Local Data Store
engine = create_engine('sqlite:///data/database.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(engine)