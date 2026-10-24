import random
from .base import Strategy,Candidate
class RandomStrategy(Strategy):
 name='RANDOM'
 def evaluate(self,candles,context):
  if not context.get('mock_mode',False):return None
  return Candidate(random.choice(['CALL','PUT']),50,'EXPERIMENTAL MOCK-ONLY RANDOM OUTPUT; not a prediction',self.name)
