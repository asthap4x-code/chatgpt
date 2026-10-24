"""Scheduler coordinates scanning, result retries, session controls, and persistent loss streaks."""
import asyncio,logging
from datetime import datetime,timezone,timedelta
log=logging.getLogger(__name__)
class Scheduler:
 def __init__(self,scanner,result_engine,db,config,on_signal):self.scanner=scanner;self.results=result_engine;self.db=db;self.config=config;self.on_signal=on_signal;self.running=False;self.task=None;self.limit=None;self.attempts=0
 async def start(self):
  self.running=True;self.db.set_setting('session_running',True);self.task=asyncio.create_task(self._loop(),name='stm-scheduler')
 async def stop(self):
  self.running=False;self.db.set_setting('session_running',False)
  if self.task:self.task.cancel();
  self.scanner.stop()
 async def run_n(self,n):
  # One eligible attempt means a candidate that passes every filter and is persisted; skipped candidates do not count.
  self.limit=n;self.attempts=0;self.running=True;self.db.set_setting('session_running',True)
  if not self.task or self.task.done():self.task=asyncio.create_task(self._loop(),name='stm-scheduler-limited')
 async def _loop(self):
  while self.running:
   try:
    stats=self.db.get_stats();loss_streak=self.db.get_setting('loss_streak',0);until=self.db.get_setting('cooldown_until')
    if loss_streak>=2 and until:
     if datetime.fromisoformat(until)>datetime.now(timezone.utc):await asyncio.sleep(5);continue
     self.db.set_setting('loss_streak',0);self.db.set_setting('cooldown_until',None)
    await self.results.resolve_due()
    results=await self.scanner.scan_once()
    for s in results:
     await self.on_signal(s);self.attempts+=1
     if self.limit and self.attempts>=self.limit:self.limit=None;self.running=False;self.db.set_setting('session_running',False);break
   except asyncio.CancelledError:raise
   except Exception:log.exception('Scheduler loop error')
   await asyncio.sleep(max(1,self.config.scan_interval))
