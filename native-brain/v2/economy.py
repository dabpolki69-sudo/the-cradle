from dataclasses import dataclass

@dataclass
class Budget:
    tokens:int=80_000
    calls:int=40
    reflex_units:int=78
    spent_tokens:int=0
    spent_calls:int=0
    spent_reflex:int=0

    def spend(self,tokens=0,calls=0,reflex=0):
        if self.spent_tokens+tokens>self.tokens or self.spent_calls+calls>self.calls:
            return False
        self.spent_tokens+=tokens; self.spent_calls+=calls; self.spent_reflex+=reflex
        return True

    @property
    def remaining(self):
        return {"tokens":self.tokens-self.spent_tokens,"calls":self.calls-self.spent_calls,
                "reflex_units":self.reflex_units-self.spent_reflex}

@dataclass
class Currencies:
    surprise:float=.0
    energy:float=.0
    stakes:float=.0

    def as_dict(self):
        return {"surprise":self.surprise,"energy":self.energy,"stakes":self.stakes}
