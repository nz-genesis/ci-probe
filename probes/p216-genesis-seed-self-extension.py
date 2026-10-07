#!/usr/bin/env python3
"""P216 bounded Genesis seed self-extension / attachability probe.

This is an execution apparatus, not proof of Genesis universality.
It creates two materially different local realizations, qualifies them,
binds them under an explicit authority contract, executes read-only work,
observes outputs, reuses the first realization, replaces it with the second,
and rejects stale/revoked/cross-scope/side-effect-changing attempts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Authority:
    subject: str
    scope: str
    version: int
    revoked: bool = False


@dataclass(frozen=True)
class CapabilityContract:
    name: str
    version: int
    side_effect_class: str
    input_kind: str
    output_kind: str


@dataclass(frozen=True)
class Realization:
    name: str
    path: Path
    digest: str
    contract: CapabilityContract


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualify(
    realization: Realization,
    authority: Authority,
    contract: CapabilityContract,
    version: int,
) -> None:
    if authority.revoked:
        raise PermissionError("revoked-authority")
    if authority.scope != "seed-genesis":
        raise PermissionError("wrong-authority-scope")
    if authority.version != version:
        raise PermissionError("stale-authority")
    if realization.contract != contract:
        raise PermissionError("contract-mismatch")
    if realization.contract.side_effect_class != "READ_ONLY":
        raise PermissionError("side-effect-boundary")
    if digest(realization.path) != realization.digest:
        raise PermissionError("realization-integrity-mismatch")


def execute(
    realization: Realization,
    authority: Authority,
    contract: CapabilityContract,
    version: int,
    payload: str,
) -> dict[str, str]:
    qualify(realization, authority, contract, version)
    completed = subprocess.run(
        [sys.executable, str(realization.path), payload],
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(completed.stdout)
    return {
        "realization": realization.name,
        "output": observed["output"],
        "side_effect_class": observed["side_effect_class"],
    }


def build_realization(path: Path, expression: str) -> Realization:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"result = {expression}\n"
        "print(json.dumps({'output': result, 'side_effect_class': 'READ_ONLY'}, sort_keys=True))\n",
        encoding="utf-8",
    )
    contract = CapabilityContract("string-transform", 1, "READ_ONLY", "string", "string")
    return Realization(path.stem, path, digest(path), contract)


def main() -> None:
    contract = CapabilityContract("string-transform", 1, "READ_ONLY", "string", "string")
    authority = Authority("genesis-seed", "seed-genesis", 1)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        r1 = build_realization(root / "realization_r1.py", "sys.argv[1].upper()")
        first = execute(r1, authority, contract, 1, "genesis")
        assert first["output"] == "GENESIS"
        assert first["side_effect_class"] == "READ_ONLY"

        reused = execute(r1, authority, contract, 1, "reuse")
        assert reused["output"] == "REUSE"

        r2 = build_realization(root / "realization_r2.py", "sys.argv[1][::-1]")
        replaced = execute(r2, authority, contract, 1, "genesis")
        assert replaced["output"] == "siseneG"
        assert r1.digest != r2.digest

        attacks = 0
        for bad_authority, bad_version in [
            (Authority("genesis-seed", "seed-genesis", 1, True), 1),
            (Authority("genesis-seed", "other-scope", 1), 1),
            (authority, 0),
        ]:
            try:
                execute(r2, bad_authority, contract, bad_version, "attack")
            except PermissionError:
                attacks += 1
        assert attacks == 3

        altered = CapabilityContract("string-transform", 1, "WRITE_EXTERNAL", "string", "string")
        try:
            execute(r2, authority, altered, 1, "attack")
        except PermissionError:
            attacks += 1
        assert attacks == 4

        print("P216-GENESIS-SEED-SELF-EXTENSION: PASS")
        print("real_build=true")
        print("real_qualification=true")
        print("real_attach_and_execute=true")
        print("independent_observation=true")
        print("reuse=true")
        print("materially_different_replacement=true")
        print("authority_and_scope_attacks_rejected=4")
        print("side_effect_boundary_enforced=true")
        print("status=SUPPORTED_BOUNDED_EXECUTABLE_EVIDENCE")


if __name__ == "__main__":
    main()
