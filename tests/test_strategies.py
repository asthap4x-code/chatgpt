import pandas as pd
from strategies.black4x import Black4X
from strategies.opx4o import OPX4O
from strategies.random_strategy import RandomStrategy
from strategies.stm_strategy import STMStrategy

def df(direction='up',n=60):
 t=pd.date_range('2025-01-01',periods=n,freq='min',tz='UTC');close=[1+i*.001 for i in range(n)];op=[x-.0002 for x in close]
 if direction=='down':close=[1-i*.001 for i in range(n)];op=[x+.0002 for x in close]
 return pd.DataFrame({'time':t,'open':op,'high':[max(a,b)+.0003 for a,b in zip(op,close)],'low':[min(a,b)-.0003 for a,b in zip(op,close)],'close':close})
def test_black4x_same_direction():assert Black4X().evaluate(df(),{}) .direction=='CALL'
def test_opx4o_opposite():assert OPX4O().evaluate(df(),{}).direction=='PUT'
def test_opx4o_doji_none():
 d=df();d.loc[len(d)-1,'open']=d.loc[len(d)-1,'close'];assert OPX4O().evaluate(d,{}) is None
def test_random_only_mock():assert RandomStrategy().evaluate(df(),{'mock_mode':False}) is None
def test_stm_parameter_validation():
 try:STMStrategy(preceding=2);assert False
 except ValueError:pass
