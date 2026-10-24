from dataclasses import dataclass
from typing import Optional
import pandas as pd
@dataclass
class Candidate:
 direction:str
 confidence:int
 reason:str
 strategy:str
class Strategy:
 name='BASE'
 def evaluate(self,candles:pd.DataFrame,context:dict)->Optional[Candidate]:raise NotImplementedError
