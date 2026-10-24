"""SQLite persistence. UTC ISO timestamps; transactions are short and serialized by SQLite."""
import sqlite3, json, threading
from pathlib import Path
from datetime import datetime, timezone

class Database:
 def __init__(self,path):
  self.path=path; Path(path).parent.mkdir(parents=True,exist_ok=True); self.lock=threading.RLock(); self._init()
 def connect(self):
  c=sqlite3.connect(self.path,timeout=15); c.row_factory=sqlite3.Row; c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA foreign_keys=ON'); return c
 def _init(self):
  with self.connect() as c:
   c.executescript("""CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY, pair TEXT NOT NULL, category TEXT NOT NULL, strategy TEXT NOT NULL, direction TEXT NOT NULL, signal_at TEXT NOT NULL, entry_at TEXT NOT NULL, expiry_at TEXT NOT NULL, payout REAL NOT NULL, confidence INTEGER NOT NULL, reference_price REAL, status TEXT NOT NULL DEFAULT 'OPEN', open_price REAL, close_price REAL, result TEXT, recovery_used INTEGER NOT NULL DEFAULT 0, resolved_at TEXT, dedupe_key TEXT UNIQUE); CREATE INDEX IF NOT EXISTS idx_signals_entry ON signals(entry_at); CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL); CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, verified INTEGER NOT NULL DEFAULT 0, categories TEXT NOT NULL DEFAULT '[]', pairs TEXT NOT NULL DEFAULT '[]', strategies TEXT NOT NULL DEFAULT '[]'); CREATE TABLE IF NOT EXISTS admin_log(id INTEGER PRIMARY KEY, user_id INTEGER, action TEXT, at TEXT);""")
 def create_signal(self,s):
  with self.lock,self.connect() as c:
   cur=c.execute('INSERT OR IGNORE INTO signals(pair,category,strategy,direction,signal_at,entry_at,expiry_at,payout,confidence,reference_price,dedupe_key) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(s['pair'],s['category'],s['strategy'],s['direction'],s['signal_at'],s['entry_at'],s['expiry_at'],s['payout'],s['confidence'],s.get('reference_price'),s['dedupe_key']))
   return cur.lastrowid if cur.rowcount else None
 def open_signals(self):
  with self.connect() as c:return [dict(r) for r in c.execute("SELECT * FROM signals WHERE status IN ('OPEN','PENDING') ORDER BY entry_at")]
 def resolve(self,sid,status,op=None,cp=None,recovery=0):
  with self.lock,self.connect() as c:c.execute('UPDATE signals SET status=?,result=?,open_price=?,close_price=?,recovery_used=?,resolved_at=? WHERE id=?',(status,status,op,cp,recovery,datetime.now(timezone.utc).isoformat(),sid))
 def get_stats(self,pair=None):
  with self.connect() as c:
   where="WHERE status IN ('WIN','LOSS','MTG WIN','TIE')"; args=[]
   if pair: where+=' AND pair=?';args.append(pair)
   rows=c.execute(f'SELECT status,recovery_used FROM signals {where}',args).fetchall()
  wins=sum(r['status'] in ('WIN','MTG WIN') for r in rows); losses=sum(r['status']=='LOSS' for r in rows); n=wins+losses
  return {'wins':wins,'losses':losses,'resolved':n,'accuracy':round(100*wins/n,2) if n else 0,'first_attempt_wins':sum(r['status']=='WIN' and not r['recovery_used'] for r in rows),'recovery_wins':sum(r['status']=='MTG WIN' for r in rows)}
 def recent(self,limit=100):
  with self.connect() as c:return [dict(r) for r in c.execute('SELECT * FROM signals ORDER BY entry_at DESC LIMIT ?', (limit,))]
 def set_setting(self,k,v):
  with self.connect() as c:c.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(k,json.dumps(v)))
 def get_setting(self,k,default=None):
  with self.connect() as c:r=c.execute('SELECT value FROM settings WHERE key=?',(k,)).fetchone()
  return json.loads(r['value']) if r else default
 def log_admin(self,uid,action):
  with self.connect() as c:c.execute('INSERT INTO admin_log(user_id,action,at) VALUES(?,?,?)',(uid,action,datetime.now(timezone.utc).isoformat()))
 def save_user(self,uid,**kw):
  with self.connect() as c:
   c.execute('INSERT OR IGNORE INTO users(user_id) VALUES(?)',(uid,))
   for k,v in kw.items():
    if k in {'verified','categories','pairs','strategies'}: c.execute(f'UPDATE users SET {k}=? WHERE user_id=?',(json.dumps(v) if k!='verified' else int(v),uid))
 def user(self,uid):
  with self.connect() as c:r=c.execute('SELECT * FROM users WHERE user_id=?',(uid,)).fetchone()
  if not r:return {'user_id':uid,'verified':0,'categories':[],'pairs':[],'strategies':[]}
  d=dict(r)
  for k in ('categories','pairs','strategies'):d[k]=json.loads(d[k])
  return d
