💰 Finance Credit Follow-Up Email Agent (MVP)
An AI-powered agentic workflow designed to automate the accounts receivable process. The system monitors overdue invoices, determines the appropriate communication tone based on an escalation matrix, and sends personalized follow-up emails via Gmail.

📋 Project Overview
Finance teams spend significant time manually chasing overdue payments. This prototype solves the problem of inconsistent follow-ups and high Days Sales Outstanding (DSO) by using LangGraph to manage a deterministic state machine and Gemini 1.5 Flash to generate empathetic yet firm communications.

Core Functionality
Database-Driven Logic: Tracks last_email_send_timestamp to ensure clients aren't harassed (minimum 7-day interval).

Tone Escalation Engine: Automatically moves from "Warm & Friendly" to "Stern & Urgent" as follow-up counts increase.

Automated Emailing: Uses smtplib to send actual emails to clients and admin alerts for legal escalations.

Human-in-the-Loop UI: A Streamlit dashboard to ingest data, trigger batch runs, and monitor database status.

Layer,Choice,Rationale
LLM,gemini-1.5-flash-latest,High speed and low cost for repetitive text generation; excellent at following structured system prompts.
Agent Framework,LangGraph,Allows for a directed acyclic graph (DAG) structure which is perfect for deterministic state transitions (Routing -> Generating -> Sending).
Data Source,SQLite via SQLAlchemy,"Provides a local, ACID-compliant database to track state across multiple application restarts."
UI,Streamlit,Rapid prototyping of an internal dashboard for finance teams to view and trigger the agent.

🏗 Agent Architecture & Flow
The agent follows a Stateful Workflow:

Ingestion: Excel data is parsed and synced to SQLite.

Eligibility Check: The system filters for records where (Current Time - Last Sent) >= 7 Days.

Router Node: Decides between generate_email (if count < 5) or escalate (if count >= 5).

Generation Node: Injects invoice details into a specific prompt template based on the current stage.

Action Node: Sends the email and updates the database with the new timestamp and incremented count.

🔐 Security & Risk Mitigation
Prompt Injection: Uses structured input templates. The LLM only receives specific fields (client_name, amount), preventing it from being manipulated by the source data.

API Key Exposure: Implemented .env with python-dotenv. Credentials like GOOGLE_API_KEY and EMAIL_APP_PASSWORD are never hardcoded.

Data Privacy (PII): All processing is done via targeted fields. Sensitive financial history is stored in a local SQLite file, not in the cloud prompts.

Email Spoofing: Configured using Google's App Password system to ensure emails are sent through an authenticated SMTP channel.


🚀 Setup & Installation
1. Clone & Environment
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install streamlit langgraph langchain-google-genai pandas openpyxl sqlalchemy python-dotenv

2. Configuration
Create a .env file in the root directory:
GOOGLE_API_KEY=your_gemini_api_key
EMAIL_APP_PASSWORD=your_16_char_google_app_password

4. Database Initialization
Create a folder named data in the project root:
mkdir data

4. Running the Application
streamlit run app.py

📈 Escalation Matrix (Mandatory Design)
Stage,Trigger,Tone,Key Message
1st Follow-Up,1–7 days,Warm & Friendly,"Gentle reminder, assume oversight."
2nd Follow-Up,8–14 days,Polite but Firm,Payment still pending; request confirmation.
3rd Follow-Up,15–21 days,Formal & Serious,Escalating concern; mention credit impact.
4th Follow-Up,22–30 days,Stern & Urgent,Final reminder before legal escalation.
Escalation,30+ days,Flag for Legal,Human review required; email sent to admin.

🧑‍💻 Author
Parve Alam

Project Type: AI Agent / Fintech Automation

Date: May 2026
