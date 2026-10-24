from database import Database

def test_setting_persists(tmp_path):
 p=str(tmp_path/'x.db');a=Database(p);a.set_setting('loss_streak',2);b=Database(p);assert b.get_setting('loss_streak')==2
