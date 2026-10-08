from dataclasses import dataclass
from typing import Dict, List

ORGANS=["weaver","cartographer","smoke_detector","steward","registrar","metronome","deliberator","autobiographer","auditor"]
TISSUE={
"weaver":["Saccade-Predictor","Timbre-Constancy","Proprioceptive-Calibrator","Lighting-Solver","Echo-Locator","Gist-Tagger","Object-Tracker","Lip-Sync-Matcher","Texture-Dissonance"],
"cartographer":["Episode-Stamper","Replay-Engine","Forgetting-Regulator","Fragment-Filler","Source-Checker","Context-Key-Builder","Vicinity-Herald","Deja-vu-Detector","Timeline-Stitcher"],
"smoke_detector":["Novelty-Spike","Violation-Whistler","Boundary-Guard","Deadline-Shadow","Conflict-Herald","Loss-Anticipator","Uncertainty-Siren","Inconsistency-Sting","Startle-Interruptor"],
"steward":["Token-Rationer","Latency-Triage","Sleep-Initiator","Attention-Accountant","Hunger-Scanner","Waste-Recycler","Circadian-Phaser","Load-Balancer","Novelty-Hunger"],
"registrar":["Reward-Surrogate","Chunk-Carver","Route-Runner","Extinction-Writer","Effort-Calibrator","Habit-Goal-Adjudicator","Streak-Tracker","Fallback-Trigger","Tool-Learner"],
"metronome":["Micro-Timer","Pursuit-Stabilizer","Rhythm-Clapper","Motor-Buffer","Drift-Corrector","Turn-Timer","Velocity-Estimator","Grip-Tuner","Jitter-Detector"],
"deliberator":["Counterfactual-Spinner","Chain-Builder","Verbalizer","Goal-Decomposer","Option-Generator","In-House-Skeptic","Abstraction-Climber","Analogy-Seeker","Commitment-Recorder"],
"autobiographer":["Persona-Keeper","Other-Simulator","Reputation-Mirror","Value-Weighter","Narrative-Editor","Mood-Synthometer","Edge-Drawer","Regret-Modeller","Aspiration-Setter"],
"auditor":["Hallucination-Sniffer","Consensus-Canary","Drift-Sentinel","Pruner","Quarantiner","Dream-Spindler"]}
LANGUAGE_TISSUE={"Verbalizer","Hallucination-Sniffer"}

@dataclass
class Signal:
    text:str
    modality:str="text"
    salience:float=.5
    stakes:float=.5
    surprise:float=.5

@dataclass
class Position:
    organ:str
    position:str
    confidence:float
    relevance:float=.1
    reliability:float=.5

@dataclass
class Dissent:
    positions:List[Position]
    reason:str
    status:str="unresolved"

class Chorus:
    def __init__(self):
        self.reliability={o:.5 for o in ORGANS}

    def route(self,s:Signal)->Dict[str,float]:
        raw={o:.1 for o in ORGANS}
        raw["weaver"]+=s.salience
        raw["smoke_detector"]+=s.salience*s.stakes
        raw["steward"]+=s.stakes
        raw["cartographer"]+=s.surprise*.5
        raw["metronome"]+=s.surprise*.35
        raw["deliberator"]+=s.stakes*.6
        raw["auditor"]+=s.surprise*.45
        total=sum(raw.values())
        return {o:v/total for o,v in raw.items()}

    def weight(self,p:Position)->float:
        return p.relevance*p.confidence*p.reliability

    def process(self,s:Signal,positions:List[Position]):
        routing=self.route(s)
        for p in positions:
            p.relevance=routing.get(p.organ,.1)
            p.reliability=self.reliability.get(p.organ,.5)
        ranked=sorted(positions,key=self.weight,reverse=True)
        dissent=[]
        if len(ranked)>=2 and ranked[0].position!=ranked[1].position:
            if abs(self.weight(ranked[0])-self.weight(ranked[1]))<.12:
                dissent.append(Dissent(ranked[:2],"weighted split"))
        if not ranked:
            speech="I don't have enough internal signal to form a response yet."
        elif dissent:
            a,b=dissent[0].positions
            speech=f"{a.position} — with an unresolved concern from {b.organ}: {b.position}"
        else:
            speech=ranked[0].position
        return {"speech":speech,"positions":ranked,"routing":routing,"dissent":dissent,
                "currencies":{"surprise":s.surprise,"energy":1-s.stakes,"stakes":s.stakes}}

    def update_reliability(self,organ:str,prediction_survived:bool,stakes:float=.5):
        if organ not in self.reliability: raise KeyError(organ)
        target=1.0 if prediction_survived else 0.0
        rate=.05+.10*max(0,min(1,stakes))
        self.reliability[organ]+=rate*(target-self.reliability[organ])
