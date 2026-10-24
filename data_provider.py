"""Provider boundary. PyQuotex is community-maintained/reverse-engineered, not an official Quotex API.
The documented get_candles(asset,end_from_time,offset,period) call is isolated here.
No documented, reliable payout endpoint was found, so the adapter deliberately returns no payout.
"""
import asyncio, logging, time
from datetime import datetime, timezone
import pandas as pd
log=logging.getLogger(__name__)

class ProviderError(RuntimeError): pass
class DataProvider:
 async def connect(self): pass
 async def close(self): pass
 async def pairs(self): raise NotImplementedError
 async def candles(self,pair,limit=120): raise NotImplementedError
 async def payout(self,pair): return None
 async def settlement(self,pair,entry_ts,expiry_ts): return None

class MockProvider(DataProvider):
 def __init__(self):self._seed=0
 async def pairs(self):return [{'pair':'EURUSD','category':'FOREX'},{'pair':'GBPUSD','category':'FOREX'},{'pair':'USDJPY','category':'FOREX'},{'pair':'EURUSD-OTC','category':'CURRENCY'},{'pair':'BTCUSD','category':'CRYPTO'},{'pair':'XAUUSD','category':'COMMODITIES'}]
 async def candles(self,pair,limit=120):
  import numpy as np
  now=int(time.time())//60*60; idx=np.arange(limit); base=1.1 if 'JPY' not in pair else 150.0
  close=base+np.cumsum(np.sin(idx/4)*0.0002+np.cos(idx/9)*0.0001)
  op=np.r_[close[0],close[:-1]]; hi=np.maximum(op,close)+0.00015; lo=np.minimum(op,close)-0.00015
  df=pd.DataFrame({'time':pd.to_datetime(now-(limit-idx)*60,unit='s',utc=True),'open':op,'high':hi,'low':lo,'close':close,'volume':1.0})
  return df
 async def payout(self,pair):return 85.0
 async def settlement(self,pair,entry_ts,expiry_ts):
  # mock settlement is explicitly synthetic; uses nearest generated candles only for test mode
  df=await self.candles(pair,3);return {'open':float(df.close.iloc[-2]),'close':float(df.close.iloc[-1]),'source':'MOCK'}

class PyQuotexAdapter(DataProvider):
 def __init__(self,email,password):self.email=email;self.password=password;self.client=None
 async def connect(self):
  if not self.email or not self.password:raise ProviderError('QUOTEX_EMAIL and QUOTEX_PASSWORD required for pyquotex mode')
  try:
   from pyquotex.stable_api import Quotex
   self.client=Quotex(email=self.email,password=self.password,lang='en')
   result=await self.client.connect()
   if isinstance(result,tuple) and result and not result[0]:raise ProviderError('PyQuotex connection was not successful')
  except Exception as e:
   self.client=None; raise ProviderError(f'PyQuotex connect failed or installed API is incompatible: {type(e).__name__}') from e
 async def close(self):
  if self.client:
   try: await self.client.close()
   except Exception: log.exception('Provider close failed')
 async def pairs(self):
  # Instrument metadata varies by PyQuotex version; do not guess OTC coverage.
  instruments=getattr(getattr(self.client,'api',None),'instruments',None)
  if not isinstance(instruments,list):return []
  out=[]
  for item in instruments:
   if isinstance(item,dict) and item.get('name'):
    name=str(item['name']); out.append({'pair':name,'category':'FOREX' if 'OTC' not in name else 'CURRENCY'})
  return out
 async def candles(self,pair,limit=120):
  if not self.client:raise ProviderError('Provider is not connected')
  try:
   raw=await self.client.get_candles(pair,time.time(),limit*60,60)
   if not raw:raise ProviderError('Provider returned no candles')
   df=pd.DataFrame(raw)
   # PyQuotex documents dict candles with time/open/close/high/low.
   required={'time','open','high','low','close'}
   if not required.issubset(df.columns):raise ProviderError('Unrecognized candle schema; refusing unsafe conversion')
   df['time']=pd.to_datetime(df['time'],unit='s',utc=True)
   for col in ('open','high','low','close'):df[col]=pd.to_numeric(df[col],errors='coerce')
   return df.sort_values('time').drop_duplicates('time').tail(limit).reset_index(drop=True)
  except ProviderError:raise
  except Exception as e:raise ProviderError(f'PyQuotex candle retrieval failed: {type(e).__name__}') from e
 async def payout(self,pair):return None
 async def settlement(self,pair,entry_ts,expiry_ts):return None
