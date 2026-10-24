from datetime import datetime,timezone

def test_utc_aware():assert datetime.now(timezone.utc).utcoffset().total_seconds()==0
