import logging, asyncio
from datetime import datetime,timezone
log=logging.getLogger(__name__)
class ResultEngine:
 def __init__(self,db,provider,config):self.db=db;self.provider=provider;self.config=config
 async def resolve_due(self):
  now=datetime.now(timezone.utc)
  for s in self.db.open_signals():
   if datetime.fromisoformat(s['expiry_at'])>now:continue
   try:data=await self.provider.settlement(s['pair'],s['entry_at'],s['expiry_at'])
   except Exception:log.exception('Settlement lookup failed for signal %s',s['id']);continue
   if not data or data.get('open') is None or data.get('close') is None:
    # preserve unresolved signal; retry next cycle, never fabricate prices
    continue
   op=float(data['open']);cp=float(data['close'])
   if data.get('source')!='MOCK' and not data.get('official_result'):
    # Do not infer real-provider settlement without authoritative entry/exit values.
    continue
   if cp==op:status='TIE'
   else:status='WIN' if ((s['direction']=='CALL' and cp>op) or (s['direction']=='PUT' and cp<op)) else 'LOSS'
   self.db.resolve(s['id'],status,op,cp,0)
