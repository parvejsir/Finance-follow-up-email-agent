# 💰 Finance Credit Follow-Up Email Agent — Version 2

An enterprise-grade AI-powered finance collection automation platform built using multi-agent orchestration.  
The system automates overdue payment follow-ups, escalates communication tone intelligently, supports human-in-the-loop approvals, maintains complete audit trails, and performs scheduled collection workflows using LangGraph agents.

## 🧠 Multi-Agent Workflow Graph

![Workflow Graph](https://github.com/parvejsir/Finance-follow-up-email-agent/blob/f223bc5b3815f76a777d7f105116f94027597913/graph.png)

---

# 🚀 Version 2 Features

- 🤖 **Multi-Agent LangGraph Workflow**
  - Router Agent
  - Email Generator Agent
  - Validator Agent
  - Human Approval Agent
  - Sender Agent
  - Audit Agent
  - Escalation Agent

---

- 📧 **AI-Powered Personalized Emails**
  - Dynamic client-specific emails
  - Includes:
    - Client Name
    - Invoice Number
    - Amount Due
    - Due Date
    - Days Overdue
    - Payment Link
  - Backend-controlled invoice values to prevent hallucinations

---

- 🧠 **4-Stage Tone Escalation Engine**
  - Stage 1 → Friendly Reminder
  - Stage 2 → Professional Follow-Up
  - Stage 3 → Formal Warning
  - Stage 4 → Final Notice
  - Stage 5+ → Manual Finance/Legal Escalation

---

- 👨‍💻 **Human-in-the-Loop (HITL) Approval System**
  - Auto Send Mode
  - Human Review Mode
  - Email Preview Before Sending
  - Regenerate Email Support
  - Retry Approval Workflow
  - Auto-send after final retry

---

- 🛡️ **Enterprise Security & Validation**
  - Prompt Injection Mitigation
  - PII Protection
  - Structured Output Validation
  - Placeholder Detection
  - API Key Security using `.env`
  - Input Sanitization
  - Hallucination Prevention
  - Email Validation Layer

---

- 📅 **Automated Cron Scheduling**
  - Immediate Stage-1 email on invoice insertion
  - Daily scheduled follow-up processing at 10:00 AM
  - Smart 7-day reminder interval
  - Duplicate send prevention

---

- 📊 **Enterprise Audit Trail System**
  - Tracks every generated email
  - Human approval/rejection history
  - Retry attempts
  - Send failures
  - Escalation logs
  - Timestamped activity tracking
  - Model usage logging

---

- ⚖️ **Automatic Legal / Finance Escalation**
  - Stops automated reminders after Stage 4
  - Flags invoice for manual review
  - Sends internal escalation notification
  - Creates escalation audit logs

---

- 📈 **Advanced Streamlit Dashboard**
  - Pending Invoice Analytics
  - Human Review Queue
  - Audit Logs Viewer
  - Escalated Cases
  - Failed Email Monitoring
  - Stage-wise Filters
  - Status Tracking

---

## 🛠️ Tech Stack

- **LLM:** Gemini 2.5 Flash (Google AI)
- **Agent Framework:** LangGraph (LangChain)
- **Frontend:** Streamlit
- **Database:** SQLite with SQLAlchemy (ORM)
- **Data Handling:** Pandas & Openpyxl
- **Environment:** Python 3.11+

---

## 📁 Folder Structure

```text
finance-email-agent/
│
├── agents/                         # Multi-agent LangGraph workflow
│   ├── __init__.py
│   ├── graph.py                    # LangGraph workflow builder
│   ├── nodes.py                    # Router, Generator, Validator, Sender, Escalation agents
│   ├── prompts.py                  # System prompts & escalation prompts
│   └── state.py                    # Shared LangGraph state schema
│
├── data/                           # SQLite database storage
│   └── database.db
│
├── models/                         # Database models & ORM setup
│   ├── __init__.py
│   └── database.py                 # Invoice + Audit models
│
├── services/                       # Business logic/services layer
│   ├── __init__.py
│   ├── audit.py                    # Audit trail logging service
│   ├── email_service.py            # SMTP / SendGrid email handling
│   ├── invoice_service.py          # Invoice processing logic
│   └── scheduler.py                # APScheduler cron jobs
│
├── ui/                             # Streamlit dashboard UI
│   ├── __init__.py
│   └── dashboard.py                # Dashboard components & HITL workflow
│
├── utils/                          # Utility/helper functions
│   ├── __init__.py
│   └── visualizer.py               # LangGraph visualization & graph export
│
├── venv/                           # Virtual environment
│
├── .env                            # Environment variables & secrets
├── .gitignore                      # Git ignored files
├── app.py                          # Main Streamlit application entry point
├── graph.png                       # Auto-generated LangGraph workflow image
├── LICENSE                         # Project license
├── README.md                       # Project documentation
└── requirements.txt               # Python dependencies
```
---
## 📦 Installation & Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/finance-email-agent.git
cd finance-email-agent

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install streamlit langgraph langchain-google-genai pandas openpyxl sqlalchemy python-dotenv pygraphviz grandalf mermaid

# 4. Set up environment variables (.env file)
# GOOGLE_API_KEY=your_key
# EMAIL_APP_PASSWORD=your_16_digit_app_password
# TWILIO_ACCOUNT_SID=your_twilio_sid
# TWILIO_AUTH_TOKEN=your_twilio_auth
# TWILIO_PHONE_NUMBER=your_twilio_phone_number

```

---
## 📈 Escalation Matrix

| Stage   | Trigger               | Tone               | Key Message                                      |
|----------|-----------------------|--------------------|--------------------------------------------------|
| Stage 1  | 1–7 Days Overdue      | Warm & Friendly    | Gentle reminder; assume oversight.              |
| Stage 2  | 8–14 Days Overdue     | Polite but Firm    | Payment pending; request confirmation.          |
| Stage 3  | 15–21 Days Overdue    | Formal & Serious   | Escalating concern; mention credit impact.      |
| Stage 4  | 22–30 Days Overdue    | Stern & Urgent     | Final reminder before legal escalation.         |
| Flagged  | 30+ Days Overdue      | Legal Alert        | Human review required; Admin notified.          |

---
## 🚀 Usage Guide

1. **Initialize**  
   Create a `data/` folder in the root directory.

2. **Upload Invoice File**  
   Use the Streamlit dashboard to upload your **"Overdue Invoices"** Excel file.

3. **Sync Database**  
   Click on **"Sync to Database"** to populate the local SQLite database with invoice records.

4. **Choose The Method For Running Of Follow-up**
   Click **Auto-Process** or **Human-Review**.

5. **Run Follow-up Engine**  
   Click **"Run Follow-up Engine"** to start the automated workflow.

   - For **Human-Review** go to the human-review tab and select either **Approve** or **Reject**.
     
6. **Auditing**
   For Auditing ,use the audit log tab.

8. **Monitor Status**  
   Review the **"Database Status"** table at the bottom of the Streamlit app to track invoice states, email history, and escalation progress.

---
## 📜 License
This project is for educational and prototype purposes only.  

© 2026 Parvej Alam.
