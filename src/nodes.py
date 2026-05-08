import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from src.prompts import SYSTEM_PROMPTS, COMPANY_NOTIF_EMAIL
from src.database import SessionLocal, Invoice
from dotenv import load_dotenv  

load_dotenv() 

llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")


def send_real_email(recipient, subject, body):
    """Sends an actual email using SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "sikandarrohit4545@gmail.com"
    msg['To'] = recipient

    # Credentials from .env (Make sure these are set!)
    # You MUST use an App Password here, not your regular password
    sender_email = "sikandarrohit4545@gmail.com"
    sender_password = os.getenv("EMAIL_APP_PASSWORD") 

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def router_node(state):
    count = state.get("follow_up_count", 0)
    if count >= 4:
        return {"next_action": "escalate"}
    return {"next_action": "generate_email"}

def generation_node(state):
    count = state["follow_up_count"] + 1
    prompt_instruction = SYSTEM_PROMPTS.get(count, SYSTEM_PROMPTS[4])
    
    context = f"Client: {state['client_name']}, Invoice: {state['invoice_no']}, Amt: {state['amount']}, Due: {state['due_date']}"
    full_prompt = f"{prompt_instruction}\n\nContext: {context}\n\nWrite only the email body."
    
    response = llm.invoke(full_prompt)
    return {"email_body": response.content, "follow_up_count": count}

def send_email_node(state):
    subject = f"Payment Reminder: Invoice {state['invoice_no']}"
    success = send_real_email(state["contact_email"], subject, state["email_body"])
    
    if success:
        db = SessionLocal()
        invoice = db.query(Invoice).filter(Invoice.invoice_no == state['invoice_no']).first()
        if invoice:
            invoice.follow_up_count = state['follow_up_count']
            invoice.last_email_send_timestamp = datetime.now()
            db.commit()
        db.close()
    return {"status": "Sent" if success else "Failed"}

def escalation_node(state):
    content = f"LEGAL ALERT: {state['client_name']} (Inv: {state['invoice_no']}) has ignored 4+ reminders."
    send_real_email(COMPANY_NOTIF_EMAIL, "URGENT: Legal Escalation Required", content)
    
    db = SessionLocal()
    invoice = db.query(Invoice).filter(Invoice.invoice_no == state['invoice_no']).first()
    if invoice:
        invoice.status = "Flagged"
        db.commit()
    db.close()
    return {"status": "Flagged"}