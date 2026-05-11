import streamlit as st
import pandas as pd
from models.database import SessionLocal, Invoice, AuditLog
from datetime import datetime

def render_stats():
    db = SessionLocal()
    total_pending = db.query(Invoice).filter(Invoice.status == "Active").count()
    total_flagged = db.query(Invoice).filter(Invoice.status == "Flagged").count()
    sent_today = db.query(AuditLog).filter(
        AuditLog.send_status == "Sent",
        AuditLog.sent_at >= datetime.now().date()
    ).count()
    db.close()
    
    st.info("🏢 Organization: AI Enablement")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Invoices", total_pending)
    col2.metric("Escalated (Legal)", total_flagged)
    col3.metric("Emails Sent Today", sent_today)

def render_human_review_queue(agent):
    st.subheader("📋 Human Review Queue")
    db = SessionLocal()
    # Only show invoices that have a draft and haven't been approved yet
    queue = db.query(Invoice).filter(Invoice.human_approved == False, Invoice.last_generated_email != None).all()
    
    if not queue:
        st.write("Review queue is empty. Run the engine to generate drafts.")
    else:
        for inv in queue:
            with st.expander(f"Review Email: {inv.client_name} (Inv: {inv.invoice_no})"):
                email_text = st.text_area("Email Content", inv.last_generated_email, height=250, key=f"txt_{inv.invoice_no}")
                
                c1, c2, c3 = st.columns([1, 1, 2])
                
                # APPROVE BUTTON
                if c1.button("✅ Approve", key=f"app_{inv.invoice_no}"):
                    with st.status(f"Sending to {inv.client_name}...") as status:
                        # Direct call to sender logic
                        from agents.nodes import sender_agent
                        state = {"invoice_no": inv.invoice_no, "final_email_body": email_text, "contact_email": inv.contact_email, "current_stage": inv.follow_up_count + 1}
                        sender_agent(state)
                        status.update(label="Email Sent Successfully!", state="complete")
                    st.rerun()

                # REGENERATE / REJECT BUTTON
                if c2.button("🔄 Reject", key=f"reg_{inv.invoice_no}"):
                    if inv.retry_count < 1:
                        st.warning("Regenerating with feedback...")
                        inv.retry_count += 1
                        inv.last_generated_email = None # Force new LLM call
                        db.commit()
                        st.rerun()
                    else:
                        # Final retry logic: Auto-send
                        st.info("Final improvement attempt...")
                        from agents.nodes import sender_agent
                        state = {"invoice_no": inv.invoice_no, "final_email_body": email_text, "contact_email": inv.contact_email, "current_stage": inv.follow_up_count + 1}
                        sender_agent(state)
                        st.success(f"Thank you for acknowledgment. The email has been updated as per your feedback and sent successfully to {inv.client_name} ({inv.contact_email}).")
                        db.commit()

def render_audit_logs():
    st.subheader("🛡️ Audit Trail")
    db = SessionLocal()
    logs = db.query(AuditLog).order_by(AuditLog.generated_at.desc()).all()
    if logs:
        df = pd.DataFrame([l.__dict__ for l in logs]).drop('_sa_instance_state', axis=1)
        st.dataframe(df, use_container_width=True)
    db.close()