from dataclasses import dataclass, field
from itertools import product
@dataclass(frozen=True)
class P:
    id:str; proposer:str; version:int; authority:tuple[str,int]; epoch:int; evidence_authority:tuple[str,int]; new_root:str
@dataclass
class S:
    version:int=1; epoch:int=1; root:str="A"; generation:int=1; retired:set[str]=field(default_factory=set)
    def auth(self): return (self.root,self.generation)
def ok(s,p):
    return p.proposer==s.root and p.version==s.version and p.authority==s.auth() and p.epoch==s.epoch and p.evidence_authority==s.auth() and p.proposer not in s.retired
def commit(s,p):
    if not ok(s,p): return False
    s.version+=1; s.root=p.new_root; s.generation+=1; s.epoch+=1; return True
def rollback(s,root="A"):
    if root in s.retired: return False
    s.version+=1; s.root=root; s.generation+=1; s.epoch+=1; return True
def expect(n,g,w):
    if g!=w: raise AssertionError(f"{n}: got {g!r}, want {w!r}")
def props(s):
    a=s.auth(); return {"B":P("B","A",s.version,a,s.epoch,a,"B"),"C":P("C","A",s.version,a,s.epoch,a,"C")}
def targeted():
    s=S(); p=props(s); expect("race",int(commit(s,p["B"]))+int(commit(s,p["C"])),1)
    s=S(); p=props(s)["B"]; expect("commit",commit(s,p),True); expect("rollback",rollback(s),True); expect("stale",commit(s,p),False)
    fresh=P("B2","A",s.version,s.auth(),s.epoch,s.auth(),"B"); expect("fresh",commit(s,fresh),True); expect("ABA",s.auth(),("B",4))
    s=S(); p=props(s)["B"]; expect("admission then rollback",commit(s,p) and rollback(s),True)
    s=S(); p=props(s)["B"]; expect("rollback then stale",rollback(s) and not commit(s,p),True)
    s=S(); p=props(s)["B"]; commit(s,p); b1=s.auth(); rollback(s); fresh=P("B2","A",s.version,s.auth(),s.epoch,s.auth(),"B"); commit(s,fresh); expect("instance differs",b1!=s.auth(),True)
    s=S(); commit(s,props(s)["B"]); s.retired.add("A"); expect("retired",rollback(s),False)
def exhaustive():
    failures=[]
    for n in range(1,7):
        for seq in product(("B","C","R"),repeat=n):
            s=S(); p=props(s); wins=0
            for a in seq:
                before=(s.version,s.epoch,s.auth())
                if a in ("B","C"):
                    if commit(s,p[a]):
                        wins+=1
                        if before!=(1,1,("A",1)): failures.append(("stale",seq,a))
                else: rollback(s)
            if wins>1: failures.append(("multi",seq))
            if any(s.version<1 for _ in [0]): failures.append(("version",seq))
    expect("1092 interleavings",failures,[])
def redteam():
    s=S(); p=props(s)["B"]; commit(s,p); rollback(s)
    if p.version==s.version and p.epoch==s.epoch and p.authority==s.auth(): raise AssertionError("RT-01 stale binding survived")
    s=S(); commit(s,props(s)["B"]); b1=s.auth(); rollback(s); f=P("B2","A",s.version,s.auth(),s.epoch,s.auth(),"B"); commit(s,f)
    if b1==s.auth(): raise AssertionError("RT-02 ABA alias survived")
def main():
    targeted(); exhaustive(); redteam()
    print("7/7 targeted R5 Pass 2 cases PASS")
    print("1092/1092 exhaustive interleaving sequences PASS")
    print("2/2 Red Team mutation checks PASS")
    print("new Genesis primitive: NOT DEMONSTRATED")
    print("epistemic status: SUPPORTED / BOUNDED")
if __name__=="__main__": main()
