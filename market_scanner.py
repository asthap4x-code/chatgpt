import asyncio,logging
log=logging.getLogger(__name__)
class MarketScanner:
 def __init__(self,provider,engine,config):self.provider=provider;self.engine=engine;self.config=config;self.stop_event=asyncio.Event();self.pairs=[]
 async def refresh(self):
  self.pairs=await self.provider.pairs();return self.pairs
 async def scan_once(self):
  if not self.pairs:await self.refresh()
  tasks=[]
  for p in self.pairs:
   for s in self.config.enabled_strategies:tasks.append(self.engine.candidate(p['pair'],p.get('category','FOREX'),s))
  return [r for r in await asyncio.gather(*tasks,return_exceptions=False) if r]
 async def run(self,on_signal):
  while not self.stop_event.is_set():
   try:
    for s in await self.scan_once():await on_signal(s)
   except Exception:log.exception('Scan loop failed')
   try:await asyncio.wait_for(self.stop_event.wait(),timeout=self.config.scan_interval)
   except asyncio.TimeoutError:pass
 def stop(self):self.stop_event.set()
