from datetime import datetime,timezone,timedelta
import logging, hashlib
from strategies.ai_strategy import AIStrategy
from strategies.stm_strategy import STMStrategy
from strategies.random_strategy import RandomStrategy
from strategies.black4x import Black4X
from strategies.opx4o import OPX4O
from strategies.indicators import validate_candles
log=logging.getLogger(__name__)
class SignalEngine:
 def __init__(self,config,db,provider):
  self.config=config;self.db=db;self.provider=provider;self.strategies={'AI':AIStrategy(),'STM':STMStrategy(),'RANDOM':RandomStrategy(),'BLACK4X':Black4X(),'OPX4O':OPX4O()};self.semaphore=__import__('asyncio').Semaphore(config.max_concurrency)
 async def candidate(self,pair,category,strategy_name):
  if strategy_name not in self.config.enabled_strategies and strategy_name!='RANDOM':return None
  async with self.semaphore:
   try:
    df=await self.provider.candles(pair,120)
    if df is None:return None
    # Drop candle still in progress; provider timestamps are candle start times.
    now=datetime.now(timezone.utc);times=__import__('pandas').to_datetime(df.time,utc=True)
    df=df.loc[times+__import__('pandas').Timedelta(seconds=60)<=now].reset_index(drop=True)
    ok,reason=validate_candles(df)
    if not ok:log.debug('Skipping %s: %s',pair,reason);return None
    age=(now-times.iloc[-1].to_pydatetime()-timedelta(seconds=60)).total_seconds()
    if age>self.config.max_data_age_seconds:return None
    payout=await self.provider.payout(pair)
    if payout is None or payout<self.config.payout_threshold:return None
    ctx={'min_confidence':self.config.min_confidence,'mock_mode':self.config.mock_mode}
    s=self.strategies[strategy_name];cand=s.evaluate(df,ctx)
    if not cand:return None
    if cand.confidence<self.config.min_confidence:return None
    now=datetime.now(timezone.utc)
    # Target the next minute only in the final 10 seconds; earlier scans are not eligible.
    if now.second < 50:return None
    entry=(now+timedelta(minutes=1)).replace(second=0,microsecond=0);expiry=entry+timedelta(minutes=1)
    key=hashlib.sha256(f'{pair}|{entry.isoformat()}|{cand.strategy}'.encode()).hexdigest()
    row={'pair':pair,'category':category,'strategy':cand.strategy,'direction':cand.direction,'signal_at':now.isoformat(),'entry_at':entry.isoformat(),'expiry_at':expiry.isoformat(),'payout':float(payout),'confidence':int(cand.confidence),'reference_price':float(df.close.iloc[-1]),'dedupe_key':key,'reason':cand.reason}
    sid=self.db.create_signal(row)
    if not sid:return None
    row['id']=sid;return row
   except Exception:log.exception('Candidate evaluation failed for %s/%s',pair,strategy_name);return None
