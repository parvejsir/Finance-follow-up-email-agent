from datetime import datetime, timedelta
import pandas as pd

def calculate_days_overdue(due_date):
    """Calculates days since the invoice was due."""
    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
    delta = datetime.now() - due_date
    return delta.days

def is_eligible_for_followup(last_sent_timestamp):
    """Checks if the last email was more than 7 days ago."""
    if last_sent_timestamp is None:
        return True # It has never been sent, so it's eligible
    
    elapsed_time = datetime.now() - last_sent_timestamp
    return elapsed_time.days >= 7

def parse_excel(file):
    """Reads excel and returns a list of dictionaries."""
    df = pd.read_excel(file)
    # Ensure column names match our expected format
    df.columns = [c.lower().replace(" ", "_").replace(".", "") for c in df.columns]
    return df.to_dict(orient='records')