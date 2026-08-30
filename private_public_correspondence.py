"""Bounded private-to-public semantic correspondence probe."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PrivateState:
    public_status: str
    public_version: int
    private_note: str


def project(s: PrivateState) -> tuple[str, int]:
    return (s.public_status, s.public_version)


def main() -> None:
    a = PrivateState("ready", 1, "secret-A")
    b = PrivateState("ready", 1, "secret-B")
    c = PrivateState("blocked", 1, "secret-A")
    d = PrivateState("ready", 2, "secret-A")
    assert project(a) == project(b), "private-only mutation leaked into public projection"
    assert project(a) != project(c), "public semantic mutation was erased"
    assert project(a) != project(d), "public version mutation was erased"
    assert "secret-A" not in project(a)
    print("PRIVATE-PUBLIC CORRESPONDENCE: 4/4 PASS")
    print("Invariant: private-only changes may remain private; public-semantic changes remain observable")

if __name__ == "__main__":
    main()
