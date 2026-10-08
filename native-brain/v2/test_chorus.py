from .chorus import ORGANS,TISSUE,LANGUAGE_TISSUE,Chorus,Signal,Position
from .economy import Budget
from .voice import Voice

def test_structure():
    assert len(ORGANS)==9
    assert sum(map(len,TISSUE.values()))==78
    assert len(LANGUAGE_TISSUE)==2
    assert all(len(v)==9 for k,v in TISSUE.items() if k!='auditor')
    assert len(TISSUE['auditor'])==6

def test_route():
    r=Chorus().route(Signal('x',salience=.8,stakes=.9,surprise=.7))
    assert abs(sum(r.values())-1)<1e-9
    assert all(v>0 for v in r.values())

def test_weight():
    c=Chorus(); p=Position('auditor','check',.8,relevance=.5)
    assert c.weight(p)==.5*.8*.5

def test_budget():
    b=Budget(tokens=10,calls=2)
    assert b.spend(tokens=5,calls=1)
    assert not b.spend(tokens=6,calls=1)

def test_voice():
    v=Voice(); out=v.receive('hello')
    assert 'speech' in out and 'routing' in out
