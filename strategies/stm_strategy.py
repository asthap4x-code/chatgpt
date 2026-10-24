from .base import Strategy,Candidate
from .indicators import add_indicators,validate_candles,trend_from_swings
class STMStrategy(Strategy):
 name='STM'
 def __init__(self,preceding=3,body_threshold=55,body_cap=85):
  if not 3<=preceding<=10:raise ValueError('preceding must be 3..10')
  self.preceding=preceding;self.body_threshold=body_threshold;self.body_cap=body_cap
 def evaluate(self,candles,context):
  ok,_=validate_candles(candles)
  if not ok:return None
  x=add_indicators(candles);r=x.iloc[-1];prev=x.iloc[-2];trend=trend_from_swings(candles)
  # PVIP: >=N consecutive trend candles, then one pullback candle; trend is confirmed swing structure.
  n=self.preceding
  seq=x.iloc[-(n+1):-1]
  if trend=='UP' and (seq.close>seq.open).all() and r.close<r.open and r.close>r.ema20:
   return Candidate('CALL',72,f'STM PVIP: {n} bullish candles, bearish pullback, confirmed uptrend','STM PVIP')
  if trend=='DOWN' and (seq.close<seq.open).all() and r.close>r.open and r.close<r.ema20:
   return Candidate('PUT',72,f'STM PVIP: {n} bearish candles, bullish pullback, confirmed downtrend','STM PVIP')
  # PVIP 2: adjacent candles share boundary when prior close == current open within floating tolerance;
  # body_pct = abs(close-open)/(high-low)*100; require EMA-side and a closed breakout.
  if r.range>0 and self.body_threshold<=r.body_pct<=self.body_cap:
   shared=abs(float(r.open)-float(prev.close))<=max(float(r.atr or 0)*.05,1e-8)
   if shared and r.close>r.open and r.open>r.ema10 and r.close>prev.high:
    return Candidate('CALL',70,'STM PVIP 2: shared boundary, EMA10 bullish side, confirmed body breakout','STM PVIP 2')
   if shared and r.close<r.open and r.open<r.ema10 and r.close<prev.low:
    return Candidate('PUT',70,'STM PVIP 2: shared boundary, EMA10 bearish side, confirmed body breakout','STM PVIP 2')
  return None
