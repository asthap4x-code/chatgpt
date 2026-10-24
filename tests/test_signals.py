from database import Database
from pathlib import Path

def test_duplicate_prevention(tmp_path):
 db=Database(str(tmp_path/'x.db'));s={'pair':'EURUSD','category':'FOREX','strategy':'AI','direction':'CALL','signal_at':'a','entry_at':'b','expiry_at':'c','payout':85,'confidence':70,'dedupe_key':'same'}
 assert db.create_signal(s);assert db.create_signal(s) is None
