# 💰 Finance Credit Follow-Up Email Agent

An AI-powered agentic workflow designed to automate the accounts receivable process. This system monitors overdue invoices, determines the appropriate communication tone based on a 4-stage escalation matrix, and sends personalized follow-up emails via Gmail.

---

## 🚀 Features

- 🤖 **LangGraph Workflow:** Deterministic state machine for reliable agent behavior.
- 📧 **Automated Emailing:** Sends actual emails using `smtplib` and Gmail App Passwords.
- 🧠 **Tone Escalation:** Automatically switches from 'Warm' to 'Stern' based on overdue days.
- 📅 **7-Day Smart Delay:** Logic to ensure clients aren't harassed (minimum 7-day gap between emails).
- ⚖️ **Legal Escalation:** Automatically flags accounts and alerts the admin after 4 failed attempts.
- 📊 **Streamlit Dashboard:** Professional UI to upload Excel data and monitor database status.

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
├── data/               # SQLite database storage
├── src/
│   ├── database.py     # SQLAlchemy models & DB CRUD
│   ├── graph.py        # LangGraph workflow definition
│   ├── nodes.py        # Logic for Router, Generator, and Emailer
│   ├── prompts.py      # System prompts & Escalation matrix
│   └── utils.py        # Date math & Excel parsing
├── app.py              # Main Streamlit application
├── .env                # API Keys (Google & Email)
├── requirements.txt    # Python dependencies
└── README.md           # You are here
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
pip install streamlit langgraph langchain-google-genai pandas openpyxl sqlalchemy python-dotenv

# 4. Set up environment variables (.env file)
# GOOGLE_API_KEY=your_key
# EMAIL_APP_PASSWORD=your_16_digit_app_password
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

4. **Run Follow-up Engine**  
   Click **"Run Follow-up Engine"** to start the automated workflow.

   - The agent checks whether **7 days** have passed since the `last_email_send_timestamp`.
   - If eligible, Gemini generates a **tone-appropriate follow-up email** based on the escalation stage.
   - The email is automatically sent to the client.
   - The database is updated with the latest follow-up activity.

5. **Monitor Status**  
   Review the **"Database Status"** table at the bottom of the Streamlit app to track invoice states, email history, and escalation progress.

---
## 📜 License
This project is for educational and prototype purposes only.  

© 2026 Parvej Alam.
