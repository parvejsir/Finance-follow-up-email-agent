from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    # Invoice Data
    invoice_no: str
    client_name: str
    amount: float
    due_date: str
    contact_email: str
    contact_phone: Optional[str] # <-- Added to capture telephone strings
    
    # Metadata
    follow_up_count: int
    current_stage: int
    
    # AI Outputs
    generated_content: str  # The body paragraph
    final_email_body: str   # The template + paragraph
    
    # HITL Control Flow
    approval_status: str    # "pending", "approved", "rejected"
    retry_count: int        # Tracks if it's the 1st or 2nd regeneration
    next_node: str          # Controls the path
    
    # Validation & Mode
    is_valid: bool
    processing_mode: str    # "Auto-Process" or "Human Review"
    
    # Audit tracking
    audit_log_id: Optional[int]