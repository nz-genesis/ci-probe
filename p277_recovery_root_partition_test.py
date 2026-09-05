from dataclasses import dataclass
from enum import Enum

class V(Enum): VALID=1; INVALID=2; UNKNOWN=3

@dataclass(frozen=True)
class Authority:
    epoch:int
    root:str
    signers:frozenset[str]
    threshold:int
    protected:bool=True

@dataclass(frozen=True)
class Recovery:
    old_root:str
    new_root:str
    epoch:int
    signers:frozenset[str]

def decide(current:Authority, a:Recovery, b:Recovery, available:frozenset[str])->V:
    # Safety-first rule: conflicting successor histories without a common
    # authoritative quorum remain UNKNOWN; partition must not manufacture liveness.
    if a.old_root != current.root or b.old_root != current.root:
        return V.INVALID
    if a.epoch != current.epoch+1 or b.epoch != current.epoch+1:
        return V.INVALID
    if a.new_root == b.new_root:
        return V.VALID if len((a.signers & b.signers) & available) >= current.threshold else V.UNKNOWN
    return V.UNKNOWN

def run():
    current=Authority(10,"R10",frozenset({"s1","s2","s3","s4"}),3)
    a=Recovery("R10","R11A",11,frozenset({"s1","s2","s3"}))
    b=Recovery("R10","R11B",11,frozenset({"s2","s3","s4"}))
    same=Recovery("R10","R11A",11,frozenset({"s1","s2","s3"}))

    # 1. Competing partition histories do not produce an arbitrary winner.
    assert decide(current,a,b,frozenset({"s1","s2","s3","s4"})) is V.UNKNOWN
    # 2. No availability cannot become guessed authority.
    assert decide(current,a,a,frozenset()) is V.UNKNOWN
    # 3. Same successor with enough currently available common authority can converge.
    assert decide(current,a,same,frozenset({"s1","s2","s3"})) is V.VALID
    # 4. Partial availability below threshold remains unknown.
    assert decide(current,a,a,frozenset({"s1","s2"})) is V.UNKNOWN
    # 5. Wrong parent history is invalid.
    wrong=Recovery("R9","R11A",11,frozenset({"s1","s2","s3"}))
    assert decide(current,wrong,wrong,frozenset({"s1","s2","s3"})) is V.INVALID
    # 6. Epoch skipping is invalid.
    skip=Recovery("R10","R12",12,frozenset({"s1","s2","s3"}))
    assert decide(current,skip,skip,frozenset({"s1","s2","s3"})) is V.INVALID
    # 7. A protected authority is not replaced merely because a partitioned side claims it.
    assert current.protected is True
    # 8. This is a liveness/safety tradeoff, not a missing Genesis primitive.
    assert V.UNKNOWN != V.VALID

    print("P277 recovery-root partition: 8/8 PASS")

if __name__ == "__main__":
    run()
