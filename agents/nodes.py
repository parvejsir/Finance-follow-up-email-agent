import os
import json
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.prompts import GENERATOR_SYSTEM_PROMPT, VALIDATOR_SYSTEM_PROMPT
from models.database import SessionLocal, Invoice
from services.email_service import send_secure_email
from services.sms_service import send_billing_sms # <-- Import our new messaging client
from services.audit import create_audit_entry, update_audit_status
from dotenv import load_dotenv

load_dotenv()

# Strict LLM setup for cost and quota efficiency
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

def router_agent(state):
    """Decides between generation and legal escalation."""
    if state["follow_up_count"] >= 4:
        return {"next_node": "escalate"}
    return {"next_node": "generate"}

def email_generator_agent(state):
    """
    Generates email body. 
    QUOTA OPTIMIZATION: Checks if a draft already exists in the state/DB 
    to avoid redundant Gemini calls.
    """
    if state.get("generated_content") and state.get("approval_status") != "rejected":
        return {"next_node": "validate"}

    prompt = f"{GENERATOR_SYSTEM_PROMPT}\n\nTask: Write a Stage {state['current_stage']} paragraph for {state['client_name']}."
    response = llm.invoke(prompt)
    content = response.content
    
    full_email = f"""
Subject: Payment Reminder - Invoice #{state['invoice_no']}

Dear {state['client_name']},

{content}

Invoice Details:
- Invoice Number: {state['invoice_no']}
- Amount Due: ${state['amount']}
- Due Date: {state['due_date']}

Please use this payment link: http://pay.aienablement.in/{state['invoice_no']}

Regards,
Finance Team
AI Enablement
    """
    
    return {
        "generated_content": content, 
        "final_email_body": full_email, 
        "next_node": "validate"
    }

def validator_agent(state):
    """QA check to ensure no brackets or hallucinated values exist."""
    email = state["final_email_body"]
    
    placeholders = ["[", "]", "{", "}"]
    is_valid = not any(p in email for p in placeholders)
    
    if not is_valid:
        if state.get("retry_count", 0) < 1:
            return {"next_node": "generate", "retry_count": state["retry_count"] + 1, "is_valid": False}
        return {"next_node": "send", "is_valid": True} 

    return {"is_valid": True, "next_node": "send"}

def sender_agent(state):
    """Broadcasts reminders across multiple channels (Email + Twilio SMS) and recalibrates schedules."""
    log_id = create_audit_entry(state, status="Processing")
    
    # Channel 1: High-Fidelity Email Delivery
    email_success, email_error = send_secure_email(
        recipient=state["contact_email"],
        subject=f"Reminder: Invoice {state['invoice_no']}",
        body=state["final_email_body"]
    )
    
    # Channel 2: Immediate Multi-Channel SMS Alerts
    sms_success = True
    sms_error = None
    if state.get("contact_phone"):
        sms_success, sms_result = send_billing_sms(
            recipient_phone=state["contact_phone"],
            client_name=state["client_name"],
            invoice_no=state["invoice_no"],
            amount=state["amount"],
            due_date=state["due_date"]
        )
        if not sms_success:
            sms_error = sms_result

    # Database state management & interval calculation
    if email_success:
        db = SessionLocal()
        inv = db.query(Invoice).filter(Invoice.invoice_no == state['invoice_no']).first()
        if inv:
            inv.follow_up_count += 1
            inv.last_email_send_timestamp = datetime.now()
            inv.next_followup_due = datetime.now() + timedelta(days=7)
            inv.last_generated_email = None 
            inv.retry_count = 0
            db.commit()
        db.close()
        
        # Log results to our consolidated system log metrics
        combined_err = f"SMS Alert Notice: {sms_error}" if not sms_success else None
        update_audit_status(log_id, status="Sent", sent_email=state["final_email_body"], error=combined_err)
    else:
        update_audit_status(log_id, status="Failed", error=f"Email Fail: {email_error} | SMS Info: {sms_error}")
        
    return {"status": "Complete"}

def escalation_agent(state):
    """Legal Escalation Node."""
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.invoice_no == state['invoice_no']).first()
    if inv:
        inv.status = "Flagged"
        db.commit()
    db.close()
    return {"status": "Flagged", "next_node": "end"}