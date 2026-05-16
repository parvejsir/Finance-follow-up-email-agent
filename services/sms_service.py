import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_billing_sms(recipient_phone, client_name, invoice_no, amount, due_date):
    """
    Cleanses phone data and pushes a structured payment SMS via Twilio API.
    Auto-appends +91 for Indian numbering plans if input is raw.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    if not account_sid or not auth_token or not twilio_number:
        return False, "Missing Twilio configuration environment variables."
        
    # Standardize to international E.164 format
    phone_clean = str(recipient_phone).strip().split('.')[0] # Remove potential decimal float artifacts
    if not phone_clean.startswith("+"):
        if len(phone_clean) == 10:
            phone_clean = f"+91{phone_clean}"
        elif phone_clean.startswith("91") and len(phone_clean) == 12:
            phone_clean = f"+{phone_clean}"
        else:
            return False, f"Invalid phone structure format: {phone_clean}"
            
    try:
        client = Client(account_sid, auth_token)
        
        # Build concise message payload to fit SMS limits cleanly
        message_body = (
            f"Dear {client_name},\n\n"
            f"This is a reminder from AI Enablement regarding Invoice #{invoice_no}.\n"
            f"Amount Due: ${amount}\n"
            f"Due Date: {due_date}\n\n"
            f"Payment Link: http://pay.aienablement.in/{invoice_no}"
        )
        
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=phone_clean
        )
        return True, message.sid
    except Exception as e:
        return False, str(e)