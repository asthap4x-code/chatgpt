"""Indicators and confirmed structure helpers; calculations only use supplied closed candles."""
import numpy as np, pandas as pd
REQUIRED=('time','open','high','low','close')
def validate_candles(df,min_rows=55):
 if not isinstance(df,pd.DataFrame) or not set(REQUIRED).issubset(df.columns):return False,'missing OHLC columns'
 if len(df)<min_rows:return False,'insufficient candles'
 x=df.copy()
 for c in ('open','high','low','close'):x[c]=pd.to_numeric(x[c],errors='coerce')
 if x[list(('open','high','low','close'))].isna().any().any():return False,'missing/non-numeric OHLC'
 if not np.isfinite(x[['open','high','low','close']].to_numpy()).all():return False,'non-finite OHLC'
 if (x.high<x[['open','close','low']].max(axis=1)).any() or (x.low>x[['open','close','high']].min(axis=1)).any():return False,'invalid OHLC range'
 t=pd.to_datetime(x.time,utc=True,errors='coerce')
 if t.isna().any() or t.duplicated().any() or not t.is_monotonic_increasing:return False,'timestamps invalid or unordered'
 return True,''
def add_indicators(df):
 x=df.copy()
 for n in (10,20,50):x[f'ema{n}']=x.close.ewm(span=n,adjust=False).mean(); x[f'sma{n}']=x.close.rolling(n).mean()
 lo=x.low.rolling(14).min(); hi=x.high.rolling(14).max(); x['stoch_k']=100*(x.close-lo)/(hi-lo).replace(0,np.nan); x['stoch_d']=x.stoch_k.rolling(3).mean()
 delta=x.close.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); x['rsi']=100-100/(1+gain/loss.replace(0,np.nan))
 e12=x.close.ewm(span=12,adjust=False).mean();e26=x.close.ewm(span=26,adjust=False).mean();x['macd']=e12-e26;x['macd_signal']=x.macd.ewm(span=9,adjust=False).mean()
 tr=pd.concat([x.high-x.low,(x.high-x.close.shift()).abs(),(x.low-x.close.shift()).abs()],axis=1).max(axis=1);x['atr']=tr.rolling(14).mean()
 x['body']=x.close-x.open;x['range']=x.high-x.low;x['body_pct']=x.body.abs()/x.range.replace(0,np.nan)*100
 return x
def confirmed_swings(df,left=2,right=2):
 """Return swing indexes only after right-hand candles have closed; no look-ahead at decision index."""
 highs=[];lows=[]
 for i in range(left,len(df)-right):
  if df.high.iloc[i] > df.high.iloc[i-left:i].max() and df.high.iloc[i] >= df.high.iloc[i+1:i+right+1].max():highs.append(i)
  if df.low.iloc[i] < df.low.iloc[i-left:i].min() and df.low.iloc[i] <= df.low.iloc[i+1:i+right+1].min():lows.append(i)
 return highs,lows
def trend_from_swings(df):
 h,l=confirmed_swings(df)
 if len(h)>=2 and len(l)>=2:
  hh=df.high.iloc[h[-1]]>df.high.iloc[h[-2]]; hl=df.low.iloc[l[-1]]>df.low.iloc[l[-2]]
  lh=df.high.iloc[h[-1]]<df.high.iloc[h[-2]]; ll=df.low.iloc[l[-1]]<df.low.iloc[l[-2]]
  if hh and hl:return 'UP'
  if lh and ll:return 'DOWN'
 return 'RANGE'
