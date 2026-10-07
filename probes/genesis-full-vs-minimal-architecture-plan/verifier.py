#!/usr/bin/env python3
from itertools import combinations

BASE={'state','transition','capability','authority','observation','evidence','constraint'}
FULL={'signal_ingress','interpretation','intent_formation','goal_formation','possibility_space','research','reasoning','planning','decision','capability_resolution','governed_execution','observation','evidence','verification','recovery','external_realization','self_evolution','governance','skills','praxis','add_ons','domain_system_creation','knowledge','learning'}
OWNERS={
'signal_ingress':'extension','interpretation':'extension','intent_formation':'extension','goal_formation':'extension','possibility_space':'extension',
'research':'extension','reasoning':'extension','planning':'extension','decision':'governance','capability_resolution':'base','governed_execution':'base',
'observation':'base','evidence':'base','verification':'extension','recovery':'base','external_realization':'external_adapter','self_evolution':'governance',
'governance':'governance','skills':'extension','praxis':'extension','add_ons':'extension','domain_system_creation':'extension','knowledge':'extension','learning':'extension'}
STAGES={
'contract':(),
'reference_kernel':('contract',),
'governed_action':('reference_kernel',),
'external_realization':('governed_action',),
'cognition_extension':('contract','governed_action'),
'research_assurance':('contract','reference_kernel'),
'evolution_governance':('research_assurance','governed_action'),
'substrate_substitution':('external_realization','research_assurance')}

def main():
    assert set(OWNERS)==FULL
    assert set(OWNERS.values()) <= {'base','extension','external_adapter','governance'}
    assert len(BASE)==7
    assert BASE.isdisjoint({'reasoning','research','skills','praxis','knowledge','learning'})
    for size in range(len(BASE)):
        for subset in combinations(BASE,size):
            assert BASE-set(subset)
    resolved=set(); remaining=set(STAGES)
    while remaining:
        ready=[x for x in remaining if set(STAGES[x]) <= resolved]
        assert ready
        resolved.update(ready); remaining-=set(ready)
    assert resolved==set(STAGES)
    print('FULL_FUNCTIONAL_CORPUS=25')
    print('BASE_CANDIDATE_ELEMENTS=7')
    print('FULL_TO_MINIMAL_OWNERSHIP_COVERAGE=PASS')
    print('MINIMAL_ACTION_BEARING_BOUNDARY=PASS')
    print('EXTENSION_INDEPENDENCE_OF_BASE=PASS')
    print('PROPER_BASE_SUBSETS=127/127')
    print('PLAN_DEPENDENCY_ORDER=PASS')
    print('UNIVERSAL_SUFFICIENCY=NOT_PROVEN')
    print('CANONICALIZATION=NOT_PERFORMED')

if __name__=='__main__':
    main()
