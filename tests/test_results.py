from database import Database

def test_pending_not_counted(tmp_path):
 db=Database(str(tmp_path/'x.db'));assert db.get_stats()['resolved']==0
