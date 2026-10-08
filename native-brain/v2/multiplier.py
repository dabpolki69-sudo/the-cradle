from dataclasses import dataclass

ARMS=["A0","A0c","A0e","A1","A2","A3","A4","A5","A6","A7"]
@dataclass
class Score:
    task_id:str
    arm:str
    success:float
    recovery:float=0.0
    cascade:float=0.0
    calibration:float=0.0
    drift:float=0.0

class MultiplierHarness:
    def __init__(self): self.scores=[]
    def add(self,score): self.scores.append(score)
    def mean(self,arm,field="success"):
        xs=[getattr(s,field) for s in self.scores if s.arm==arm]
        return sum(xs)/len(xs) if xs else None
    def integration(self):
        a4,a1,a2,a0=[self.mean(x) for x in ("A4","A1","A2","A0")]
        if None in (a4,a1,a2,a0): return None
        return (a4-a1)-(a2-a0)
