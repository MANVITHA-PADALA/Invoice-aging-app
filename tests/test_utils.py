import datetime as dt
from utils import compute_aging_bucket

def test_current():
    assert compute_aging_bucket(dt.date(2025,12,31), dt.date(2025,8,22)) == "Current"

def test_0_30():
    assert compute_aging_bucket(dt.date(2025,7,25), dt.date(2025,8,22)) == "0-30"

def test_31_60():
    assert compute_aging_bucket(dt.date(2025,6,25), dt.date(2025,8,22)) == "31-60"

def test_61_90():
    assert compute_aging_bucket(dt.date(2025,5,25), dt.date(2025,8,22)) == "61-90"

def test_90_plus():
    assert compute_aging_bucket(dt.date(2025,4,1), dt.date(2025,8,22)) == "90+"
