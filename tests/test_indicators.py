import pandas as pd
from strategies.indicators import validate_candles,add_indicators

def sample(n=60):
 t=pd.date_range('2025-01-01',periods=n,freq='min',tz='UTC');c=[1+i*.001 for i in range(n)]
 return pd.DataFrame({'time':t,'open':[x-.0002 for x in c],'high':[x+.0003 for x in c],'low':[x-.0004 for x in c],'close':c})
def test_validation_and_indicators():
 d=sample();assert validate_candles(d)[0];x=add_indicators(d);assert 'ema50' in x and 'atr' in x and 'stoch_k' in x
def test_bad_ohlc_rejected():
 d=sample();d.loc[10,'high']=0;assert not validate_candles(d)[0]
