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
    - Approve: Sends email and text message, marks human_approved=True.
    - Reject (Retry 1): Logs feedback, increments retry, regenerates.
    - Reject (Retry 2): Auto-sends with final log updates.
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
            with st.expander(f"Review Communications: {inv.client_name} (Inv: {inv.invoice_no})"):
                email_text = st.text_area(
                    "Drafted Content (Gemini 2.5 Flash)", 
                    inv.last_generated_email, 
                    height=200, 
                    key=f"txt_{inv.invoice_no}"
                )
                
                # Dynamic Feedback capture field to eliminate empty logs
                feedback_input = st.text_input(
                    "📝 Add Adjustment Feedback / Audit Comments (Optional)", 
                    key=f"feed_{inv.invoice_no}",
                    placeholder="e.g., Content looks perfect, or please make it more formal"
                )
                
                c1, c2 = st.columns([1, 1])
                
                # --- ✅ APPROVE BUTTON ---
                if c1.button("✅ Approve & Dispatch", key=f"app_{inv.invoice_no}", use_container_width=True):
                    with st.status(f"Dispatched multi-channel pathways for {inv.client_name}...") as status:
                        # 1. Update Core Data Model BEFORE invoking agent to ensure data consistency
                        inv.human_approved = True
                        inv.approval_status = "approved"
                        db.commit()
                        
                        from agents.nodes import sender_agent
                        state = {
                            "invoice_no": inv.invoice_no, 
                            "client_name": inv.client_name,
                            "amount": inv.amount,
                            "due_date": inv.due_date.strftime("%Y-%m-%d") if isinstance(inv.due_date, datetime) else str(inv.due_date),
                            "final_email_body": email_text, 
                            "contact_email": inv.contact_email, 
                            "contact_phone": inv.contact_phone,
                            "current_stage": inv.follow_up_count + 1,
                            "retry_count": inv.retry_count,
                            "human_feedback": feedback_input if feedback_input else "Approved without custom modifications"
                        }
                        sender_agent(state)
                        status.update(label=f"Dispatched successfully!", state="complete")
                    st.rerun()

                # --- 🔄 REJECT / REGENERATE BUTTON ---
                if c2.button("❌ Reject & Correct", key=f"reg_{inv.invoice_no}", use_container_width=True):
                    chosen_feedback = feedback_input if feedback_input else "Rejected for automated textual alignment"
                    
                    if inv.retry_count < 1:
                        # Strike 1: Flag for textual refinement
                        inv.retry_count += 1
                        inv.approval_status = "rejected"
                        inv.last_generated_email = None # Wipe cache to force Gemini call
                        db.commit()
                        
                        # Immediately store the rejection audit comment log
                        from services.audit import create_audit_entry, update_audit_status
                        state_dummy = {
                            "invoice_no": inv.invoice_no, "client_name": inv.client_name, "amount": inv.amount,
                            "current_stage": inv.follow_up_count + 1, "retry_count": inv.retry_count,
                            "final_email_body": f"[Draft Rejected by User] - Feedback: {chosen_feedback}"
                        }
                        l_id = create_audit_entry(state_dummy, status="Rejected")
                        # Pass feedback into audit framework
                        db_audit = SessionLocal()
                        log_rec = db_audit.query(AuditLog).filter(AuditLog.id == l_id).first()
                        if log_rec:
                            log_rec.human_feedback = chosen_feedback
                            db_audit.commit()
                        db_audit.close()
                        
                        st.warning("Feedback saved. Run Engine again to view updated text alignment.")
                        st.rerun()
                    else:
                        # Strike 2: Final processing fallback override
                        with st.status("Max feedback loops hit. Forcing optimization broadcast...") as status:
                            inv.human_approved = True
                            inv.approval_status = "approved"
                            db.commit()
                            
                            from agents.nodes import sender_agent
                            state = {
                                "invoice_no": inv.invoice_no, 
                                "client_name": inv.client_name,
                                "amount": inv.amount,
                                "due_date": inv.due_date.strftime("%Y-%m-%d") if isinstance(inv.due_date, datetime) else str(inv.due_date),
                                "final_email_body": email_text, 
                                "contact_email": inv.contact_email, 
                                "contact_phone": inv.contact_phone,
                                "current_stage": inv.follow_up_count + 1,
                                "retry_count": inv.retry_count,
                                "human_feedback": f"Auto-sent after 2 rejections. Final notes: {chosen_feedback}"
                            }
                            sender_agent(state)
                            status.update(label="Dispatched across channels.", state="complete")
                        st.success(f"Dispatched successfully to {inv.client_name}.")
                        inv.retry_count = 0 
                        db.commit()
                        st.rerun()
    db.close()

def render_audit_logs():
    """Displays the enterprise-grade audit trail with interactive updates."""
    st.subheader("🛡️ Audit Trail")
    db = SessionLocal()
    logs = db.query(AuditLog).order_by(AuditLog.generated_at.desc()).all()
    if logs:
        df = pd.DataFrame([l.__dict__ for l in logs]).drop('_sa_instance_state', axis=1)
        # Included 'human_feedback' explicitly in high-visibility columns
        cols = ['generated_at', 'invoice_no', 'client_name', 'follow_up_stage', 'human_feedback', 'llm_model', 'send_status']
        st.dataframe(df[cols + [c for c in df.columns if c not in cols]], use_container_width=True)
    else:
        st.write("No audit logs found.")
    db.close()