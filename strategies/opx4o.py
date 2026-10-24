from .base import Strategy,Candidate
from .indicators import validate_candles
class OPX4O(Strategy):
 name='OPX4O'
 def __init__(self,doji_tolerance=0.00001):self.tolerance=doji_tolerance
 def evaluate(self,candles,context):
  ok,_=validate_candles(candles,2)
  if not ok:return None
  r=candles.iloc[-1];body=float(r.close-r.open)
  # Candle color convention: close>open bullish, close<open bearish. True/near doji is explicit.
  if abs(body)<=self.tolerance:return None
  return Candidate('PUT' if body>0 else 'CALL',58,'OPX4O: opposite direction to previous non-doji candle','OPX4O')
