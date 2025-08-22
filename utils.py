import datetime as dt
from typing import Literal, Optional

AgingBucket = Literal["Current","0-30","31-60","61-90","90+"]

def compute_aging_bucket(due_date: dt.date, today: Optional[dt.date] = None) -> AgingBucket:
    if today is None:
        today = dt.date.today()
    if due_date >= today:
        return "Current"
    days = (today - due_date).days
    if 1 <= days <= 30: return "0-30"
    if 31 <= days <= 60: return "31-60"
    if 61 <= days <= 90: return "61-90"
    return "90+"
