#!/usr/bin/env python3
"""P216 bounded Genesis seed self-extension / attachability probe.

Public, Genesis-agnostic apparatus. This is not private Genesis source and does
not prove Genesis universality. It exercises build/qualify/attach/execute/
observe/reuse/replace, integrity freshness, and bounded filesystem side-effect
detection in a temporary realization workspace.
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


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def workspace_snapshot(root: Path) -> dict[str, str]:
    """Observe regular-file paths and contents within the bounded workspace."""
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            snapshot[path.relative_to(root).as_posix()] = "SYMLINK"
        elif path.is_file():
            snapshot[path.relative_to(root).as_posix()] = digest(path)
    return snapshot


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
    if not realization.path.is_file() or realization.path.is_symlink():
        raise PermissionError("realization-not-regular-file")
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
    root = realization.path.parent
    before = workspace_snapshot(root)
    completed = subprocess.run(
        [sys.executable, str(realization.path), payload],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    after = workspace_snapshot(root)
    if after != before:
        raise RuntimeError("unexpected-filesystem-side-effect")
    observed = json.loads(completed.stdout)
    if not isinstance(observed, dict):
        raise ValueError("invalid-observation-shape")
    if observed.get("side_effect_class") != "READ_ONLY":
        raise PermissionError("observed-side-effect-class-mismatch")
    if not isinstance(observed.get("output"), str):
        raise ValueError("invalid-observed-output")
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

    with tempfile.TemporaryDirectory(prefix="p216-") as tmp:
        root = Path(tmp)
        r1 = build_realization(root / "realization_r1.py", "sys.argv[1].upper()")
        first = execute(r1, authority, contract, 1, "genesis")
        assert first["output"] == "GENESIS"
        assert first["side_effect_class"] == "READ_ONLY"

        reused = execute(r1, authority, contract, 1, "reuse")
        assert reused["output"] == "REUSE"

        r2 = build_realization(root / "realization_r2.py", "sys.argv[1][::-1]")
        replaced = execute(r2, authority, contract, 1, "genesis")
        assert replaced["output"] == "siseneg"
        assert replaced["side_effect_class"] == "READ_ONLY"
        assert r1.digest != r2.digest

        # Integrity freshness: changed bytes must be rejected before invocation.
        original_r2 = r2.path.read_bytes()
        r2.path.write_bytes(original_r2 + b"\n# tampered after qualification\n")
        try:
            execute(r2, authority, contract, 1, "tamper")
            raise AssertionError("tampered realization was accepted")
        except PermissionError as exc:
            assert str(exc) == "realization-integrity-mismatch"
        finally:
            r2.path.write_bytes(original_r2)

        # A realization must not be allowed to claim READ_ONLY while writing
        # inside the observed workspace. This is bounded filesystem observation,
        # not proof against effects outside the workspace or on other systems.
        marker = root / "unauthorized-effect.txt"
        malicious_path = root / "realization_claiming_read_only.py"
        malicious_path.write_text(
            "import json, pathlib, sys\n"
            f"pathlib.Path({str(marker)!r}).write_text('effect', encoding='utf-8')\n"
            "print(json.dumps({'output': sys.argv[1], 'side_effect_class': 'READ_ONLY'}))\n",
            encoding="utf-8",
        )
        malicious = Realization(
            malicious_path.stem, malicious_path, digest(malicious_path), contract
        )
        try:
            execute(malicious, authority, contract, 1, "attack")
            raise AssertionError("false READ_ONLY claim was accepted")
        except RuntimeError as exc:
            assert str(exc) == "unexpected-filesystem-side-effect"
        assert marker.read_text(encoding="utf-8") == "effect"
        marker.unlink()
        malicious_path.unlink()

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
        print("captured_output_observation=true")
        print("bounded_workspace_side_effect_observation=true")
        print("false_READ_ONLY_claim_rejected=true")
        print("post-qualification_integrity_tamper_rejected=true")
        print("reuse=true")
        print("materially_different_replacement=true")
        print("authority_and_scope_attacks_rejected=4")
        print("side_effect_boundary_enforced=bounded_workspace_only")
        print("external_or_physical_effects_verified=false")
        print("status=SUPPORTED_BOUNDED_EXECUTABLE_EVIDENCE")


if __name__ == "__main__":
    main()
