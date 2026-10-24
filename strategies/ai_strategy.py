from .base import Strategy,Candidate
from .indicators import add_indicators,validate_candles,trend_from_swings
class AIStrategy(Strategy):
 name='AI'
 def evaluate(self,candles,context):
  ok,_=validate_candles(candles)
  if not ok:return None
  x=add_indicators(candles);r=x.iloc[-1];p=x.iloc[-2];score={'CALL':0,'PUT':0};why=[]
  if r.ema10>r.ema20>r.ema50:score['CALL']+=2;why.append('EMA trend bullish')
  if r.ema10<r.ema20<r.ema50:score['PUT']+=2;why.append('EMA trend bearish')
  if r.macd>r.macd_signal:score['CALL']+=1
  if r.macd<r.macd_signal:score['PUT']+=1
  if 20<r.stoch_k<80 and r.stoch_k>r.stoch_d:score['CALL']+=1
  if 20<r.stoch_k<80 and r.stoch_k<r.stoch_d:score['PUT']+=1
  if r.close>p.high:score['CALL']+=1;why.append('close broke prior high')
  if r.close<p.low:score['PUT']+=1;why.append('close broke prior low')
  trend=trend_from_swings(candles)
  if trend=='UP':score['CALL']+=1
  if trend=='DOWN':score['PUT']+=1
  if not r.atr or r.atr<=0 or r.range<r.atr*.15 or r.range>r.atr*2.5:return None
  direction=max(score,key=score.get);best=score[direction]
  if best<4 or score['CALL']==score['PUT']:return None
  # Score is a rule-confluence index normalized to 60-90, NOT a win probability.
  confidence=min(90,60+best*5)
  if confidence<int(context.get('min_confidence',65)):return None
  return Candidate(direction,confidence,'; '.join(why) or f'{trend} structure confluence',self.name)
