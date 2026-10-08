from chorus import Chorus,Signal,Position,TISSUE,LANGUAGE_TISSUE,ORGANS

def test_counts():
    assert len(ORGANS)==9
    assert sum(map(len,TISSUE.values()))==78
    assert sum(x in LANGUAGE_TISSUE for xs in TISSUE.values() for x in xs)==2

def test_soft_routing():
    r=Chorus().route(Signal('x')); assert set(r)==set(ORGANS); assert abs(sum(r.values())-1)<1e-9; assert all(v>0 for v in r.values())

def test_weighting_and_dissent():
    c=Chorus(); ps=[Position('weaver','scene A',.8),Position('auditor','scene B',.8)]; assert c.process(Signal('x',surprise=.8),ps)['dissent']

def test_reliability_moves():
    c=Chorus(); old=c.reliability['weaver']; c.update_reliability('weaver',True,1); assert c.reliability['weaver']>old

if __name__=='__main__':
    test_counts(); test_soft_routing(); test_weighting_and_dissent(); test_reliability_moves(); print('CHORUS TESTS PASS')
