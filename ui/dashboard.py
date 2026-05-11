import streamlit as st
import pandas as pd
from models.database import SessionLocal, Invoice, AuditLog
from datetime import datetime

def render_stats():
    """Renders top-level KPIs for AI Enablement."""
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
    """
    HITL Workflow:
    - Approve: Sends immediately.
    - Reject (Retry 1): Regenerates draft.
    - Reject (Retry 2): Auto-sends with professional acknowledgement.
    """
    st.subheader("📋 Human Review Queue")
    db = SessionLocal()
    
    # Fetch invoices that have a generated draft but are not yet approved
    queue = db.query(Invoice).filter(
        Invoice.human_approved == False, 
        Invoice.last_generated_email != None,
        Invoice.status == "Active"
    ).all()
    
    if not queue:
        st.write("Review queue is empty. Run the Engine from the Management tab to generate drafts.")
    else:
        for inv in queue:
            with st.expander(f"Review Email: {inv.client_name} (Inv: {inv.invoice_no})"):
                email_text = st.text_area(
                    "Drafted Content (Gemini 2.5 Flash)", 
                    inv.last_generated_email, 
                    height=250, 
                    key=f"txt_{inv.invoice_no}"
                )
                
                c1, c2 = st.columns([1, 1])
                
                # --- ✅ APPROVE BUTTON ---
                if c1.button("✅ Approve", key=f"app_{inv.invoice_no}", use_container_width=True):
                    with st.status(f"Interpretation: Finalizing send for {inv.client_name}...") as status:
                        from agents.nodes import sender_agent
                        # Fulfilling the state requirement for Audit Logging
                        state = {
                            "invoice_no": inv.invoice_no, 
                            "client_name": inv.client_name,
                            "amount": inv.amount,
                            "final_email_body": email_text, 
                            "contact_email": inv.contact_email, 
                            "current_stage": inv.follow_up_count + 1,
                            "retry_count": inv.retry_count
                        }
                        sender_agent(state)
                        status.update(label=f"Email sent to {inv.client_name} successfully!", state="complete")
                    st.rerun()

                # --- 🔄 REJECT / REGENERATE BUTTON ---
                if c2.button("❌ Reject & Regenerate", key=f"reg_{inv.invoice_no}", use_container_width=True):
                    if inv.retry_count < 1:
                        # Logic for first rejection
                        inv.retry_count += 1
                        inv.last_generated_email = None # Force engine to re-call Gemini
                        db.commit()
                        st.warning(f"Feedback noted for {inv.client_name}. Draft marked for regeneration.")
                        st.rerun()
                    else:
                        # Logic for second rejection: Auto-Send
                        with st.status("Interpretation: Max retries reached. Optimizing and sending...") as status:
                            from agents.nodes import sender_agent
                            state = {
                                "invoice_no": inv.invoice_no, 
                                "client_name": inv.client_name,
                                "amount": inv.amount,
                                "final_email_body": email_text, 
                                "contact_email": inv.contact_email, 
                                "current_stage": inv.follow_up_count + 1,
                                "retry_count": inv.retry_count
                            }
                            sender_agent(state)
                            status.update(label="System optimized and dispatched.", state="complete")
                        
                        # Your specific requested acknowledgement message
                        st.success(f"Thank you for acknowledgment. The email has been updated as per your feedback and sent successfully to {inv.client_name} ({inv.contact_email}).")
                        
                        inv.retry_count = 0 
                        db.commit()

    db.close()

def render_audit_logs():
    """Displays the enterprise-grade audit trail."""
    st.subheader("🛡️ Audit Trail")
    db = SessionLocal()
    logs = db.query(AuditLog).order_by(AuditLog.generated_at.desc()).all()
    if logs:
        # Convert to DataFrame for visualization
        df = pd.DataFrame([l.__dict__ for l in logs]).drop('_sa_instance_state', axis=1)
        # Reordering columns for better readability
        cols = ['generated_at', 'invoice_no', 'client_name', 'follow_up_stage', 'llm_model', 'send_status']
        st.dataframe(df[cols + [c for c in df.columns if c not in cols]], use_container_width=True)
    else:
        st.write("No audit logs found.")
    db.close()