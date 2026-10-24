from .base import Strategy,Candidate
from .indicators import validate_candles
class Black4X(Strategy):
 name='BLACK4X'
 def evaluate(self,candles,context):
  ok,_=validate_candles(candles,2)
  if not ok:return None
  r=candles.iloc[-1]
  if r.close>r.open:return Candidate('CALL',60,'Previous closed candle bullish; same-direction rule','BLACK4X')
  if r.close<r.open:return Candidate('PUT',60,'Previous closed candle bearish; same-direction rule','BLACK4X')
  return None
