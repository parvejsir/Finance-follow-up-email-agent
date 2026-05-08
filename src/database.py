from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
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
    follow_up_count = Column(Integer, default=0)
    last_email_send_timestamp = Column(DateTime, nullable=True)
    status = Column(String, default="Active") # Active, Flagged

# Create the data folder if it doesn't exist before running this
engine = create_engine('sqlite:///data/database.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(engine)