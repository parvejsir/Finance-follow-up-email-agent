from datetime import datetime
from models.database import SessionLocal, AuditLog

def create_audit_entry(state, status="Draft", error=None):
    """Logs the agent's current state into the AuditLog table."""
    db = SessionLocal()
    try:
        log = AuditLog(
            invoice_no=state["invoice_no"],
            client_name=state["client_name"],
            follow_up_stage=state.get("current_stage", 0),
            tone_used=f"Stage {state.get('current_stage', 0)}",
            generated_email=state.get("final_email_body", ""),
            send_status=status,
            retry_count=state.get("retry_count", 0),
            llm_model="gemini-1.5-flash",
            error_message=str(error) if error else None,
            generated_at=datetime.now()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log.id
    finally:
        db.close()

def update_audit_status(log_id, status, sent_email=None, error=None):
    """Updates a log entry after the email attempt."""
    db = SessionLocal()
    try:
        log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        if log:
            log.send_status = status
            if status == "Sent":
                log.sent_at = datetime.now()
                log.final_sent_email = sent_email
            if error:
                log.error_message = str(error)
            db.commit()
    finally:
        db.close()