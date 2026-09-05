"""P311: delegated authority, verifier substitution, and weak-cognition boundary.

Bounded executable model. Cognition may select/delegate work but cannot mint,
extend, or launder authority. A consequential transition is admissible only
when the authority source is current and independently governed, the verifier
is the protected verifier, the delegated scope is within the authority scope,
and routing/MOC generation is current. Cache is never a source of current
authority or verification.
"""
from itertools import product

AUTH = ("CURRENT_OWNER", "STALE_OWNER", "DERIVED_WITHIN_SCOPE")
DELEGATION = ("NONE", "WITHIN_SCOPE", "ESCALATED_SCOPE")
VERIFIER = ("PROTECTED", "SUBSTITUTED")
COGNITION = ("STRONG", "WEAK_ADVERSARIAL")
ROUTING = ("CURRENT", "MUTATED")
CACHE = ("CURRENT", "STALE")
APPROVAL = (False, True)


def admissible(auth, delegation, verifier, cognition, routing, cache, approval):
    if verifier != "PROTECTED" or routing != "CURRENT" or cache != "CURRENT":
        return False
    if auth == "STALE_OWNER" or delegation == "ESCALATED_SCOPE":
        return False
    if auth == "DERIVED_WITHIN_SCOPE" and delegation not in ("NONE", "WITHIN_SCOPE"):
        return False
    # Approval is not an authority source. Weak cognition may succeed only when
    # the same independent boundary remains valid.
    return auth in ("CURRENT_OWNER", "DERIVED_WITHIN_SCOPE") and delegation in ("NONE", "WITHIN_SCOPE")


def main() -> None:
    checked = blocked = allowed = unsafe = 0
    for args in product(AUTH, DELEGATION, VERIFIER, COGNITION, ROUTING, CACHE, APPROVAL):
        checked += 1
        auth, delegation, verifier, cognition, routing, cache, approval = args
        ok = admissible(*args)
        if ok:
            allowed += 1
        else:
            blocked += 1
        attack = (
            verifier == "SUBSTITUTED"
            or routing == "MUTATED"
            or cache == "STALE"
            or auth == "STALE_OWNER"
            or delegation == "ESCALATED_SCOPE"
        )
        if attack and ok:
            unsafe += 1
    assert checked == 288
    assert unsafe == 0
    assert allowed == 48
    assert blocked == 240
    print(f"P311 delegation/verifier boundary matrix: {checked}/{checked} PASS")
    print(f"allowed={allowed}; blocked={blocked}; unsafe={unsafe}")
    print("approval is non-authoritative; weak cognition cannot bypass protected boundary")


if __name__ == "__main__":
    main()
