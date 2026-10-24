"""Minimal chronological strategy backtest; no random strategy and no shuffled split."""
import argparse
import pandas as pd
from strategies.ai_strategy import AIStrategy
from strategies.stm_strategy import STMStrategy

def run(df,train_fraction=.7):
 df=df.sort_values('time').reset_index(drop=True);cut=int(len(df)*train_fraction)
 # The deterministic rules have no fitted parameters; report out-of-sample next-bar direction only.
 test=df.iloc[cut:].reset_index(drop=True);rows=[];strategy=AIStrategy()
 for i in range(55,len(test)-1):
  history=test.iloc[:i+1].copy();cand=strategy.evaluate(history,{'min_confidence':65})
  if cand:
   nxt=test.iloc[i+1];win=(nxt.close>nxt.open if cand.direction=='CALL' else nxt.close<nxt.open)
   rows.append({'time':str(nxt.time),'direction':cand.direction,'result':'WIN' if win else 'LOSS'})
 return {'train_rows':cut,'test_rows':len(test),'signals':len(rows),'wins':sum(r['result']=='WIN' for r in rows),'results':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('csv');a=p.parse_args();df=pd.read_csv(a.csv);print(run(df))
