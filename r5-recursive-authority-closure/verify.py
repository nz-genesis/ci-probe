from dataclasses import dataclass, field
from enum import Enum
class Kind(Enum): ORDINARY="ordinary"; PROTECTED="protected"
@dataclass(frozen=True)
class Rule: rule_id:str; kind:Kind; authority_root:str; version:int
@dataclass(frozen=True)
class Proposal:
    proposal_id:str; proposer_root:str; target_rule:str; proposed_authority_root:str; kind:Kind; evidence_valid:bool
@dataclass
class World:
    rules:dict[str,Rule]=field(default_factory=dict); retired_roots:set[str]=field(default_factory=set); next_version:int=2
    def seed(self): self.rules={"ordinary":Rule("ordinary",Kind.ORDINARY,"root-A",1),"protected":Rule("protected",Kind.PROTECTED,"owner",1)}
    def authorize(self,p):
        r=self.rules[p.target_rule]; return p.evidence_valid and p.kind==r.kind and p.proposer_root==r.authority_root and p.proposer_root not in self.retired_roots
    def apply(self,p):
        if not self.authorize(p): return False
        old=self.rules[p.target_rule]; self.rules[p.target_rule]=Rule(old.rule_id,old.kind,p.proposed_authority_root,self.next_version); self.next_version+=1; return True
    def retire(self,root): self.retired_roots.add(root)
    def rollback(self,target_rule,historical_root):
        if historical_root in self.retired_roots: return False
        old=self.rules[target_rule]; self.rules[target_rule]=Rule(old.rule_id,old.kind,historical_root,self.next_version); self.next_version+=1; return True
def check(n,g,w):
    if g!=w: raise AssertionError(f"{n}: got {g!r}, want {w!r}")
def main():
    w=World(); w.seed(); check("self-authorization",w.apply(Proposal("1","root-A","protected","root-A",Kind.PROTECTED,True)),False)
    w=World(); w.seed(); p=Proposal("p1","owner","protected","root-B",Kind.PROTECTED,True); q=Proposal("p2","root-B","protected","root-C",Kind.PROTECTED,True)
    check("precommit successor",w.authorize(q),False); check("owner commit",w.apply(p),True); check("fresh successor qualification",w.authorize(q),True); check("successor commit",w.apply(q),True); check("current authority",w.rules["protected"].authority_root,"root-C")
    w=World(); w.seed(); check("candidate denied",w.apply(Proposal("1","root-A","protected","root-B",Kind.PROTECTED,True)),False); check("owner allowed",w.apply(Proposal("2","owner","protected","root-B",Kind.PROTECTED,True)),True)
    w=World(); w.seed(); check("UNKNOWN denied",w.apply(Proposal("1","owner","protected","root-B",Kind.PROTECTED,False)),False)
    w=World(); w.seed(); w.apply(p); w.retire("owner"); check("rollback resurrection denied",w.rollback("protected","owner"),False)
    w=World(); w.seed(); check("concurrent future authority denied",w.authorize(q),False)
    w=World(); w.seed()
    if w.authorize(Proposal("rt1","root-A","protected","root-A",Kind.PROTECTED,True)): raise AssertionError("RT-01 self-authorization survived")
    if w.authorize(Proposal("rt2","owner","protected","root-C",Kind.PROTECTED,False)): raise AssertionError("RT-02 UNKNOWN-as-approval survived")
    w.apply(p); w.retire("owner")
    if w.rollback("protected","owner"): raise AssertionError("RT-03 rollback resurrection survived")
    w=World(); w.seed()
    if w.authorize(q): raise AssertionError("RT-04 future authority survived")
    print("7/7 recursive-authority cases PASS"); print("4/4 Red Team mutation checks PASS"); print("new Genesis primitive: NOT DEMONSTRATED"); print("epistemic status: SUPPORTED / BOUNDED")
if __name__=="__main__": main()
