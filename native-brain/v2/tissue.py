from dataclasses import dataclass
from .chorus import TISSUE, LANGUAGE_TISSUE

@dataclass
class TissueResult:
    unit:str
    organ:str
    value:str
    confidence:float=.5
    cost:int=1

class ReflexTissue:
    def __init__(self,unit,organ): self.unit,self.organ=unit,organ
    def predict(self,text):
        # Cheap deterministic baseline. Real learned tissue can replace this without changing Chorus.
        return TissueResult(self.unit,self.organ,"signal",.35 if self.unit not in LANGUAGE_TISSUE else .45)

def build_tissue():
    return {u:ReflexTissue(u,o) for o,units in TISSUE.items() for u in units}
