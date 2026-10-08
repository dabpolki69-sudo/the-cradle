from dataclasses import dataclass
from .chorus import Chorus,Signal,Position
from .economy import Budget
from .ledger import DissentLedger

@dataclass
class VoiceResult:
    speech:str
    routing:dict
    positions:list
    dissent:list
    currencies:dict
    budget:dict

class Voice:
    def __init__(self,chorus=None,budget=None):
        self.chorus=chorus or Chorus(); self.budget=budget or Budget(); self.ledger=DissentLedger()
    def receive(self,text,positions=None,modality="text",salience=.5,stakes=.5,surprise=.5):
        signal=Signal(text,modality,salience,stakes,surprise)
        positions=positions or [Position(o,"no position",.0) for o in self.chorus.reliability]
        result=self.chorus.process(signal,positions)
        for d in result["dissent"]: self.ledger.record(d)
        self.budget.spend(calls=1,reflex=78)
        result["budget"]=self.budget.remaining
        return result
