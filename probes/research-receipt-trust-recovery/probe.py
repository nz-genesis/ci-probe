#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from securesystemslib.signer import CryptoSigner
from tuf.api.exceptions import BadVersionNumberError, DownloadHTTPError, UnsignedMetadataError
from tuf.api.metadata import Metadata, MetaFile, Root, Role, Snapshot, TargetFile, Targets, Timestamp
from tuf.api.serialization.json import JSONSerializer
from tuf.ngclient import Updater
from tuf.ngclient.fetcher import FetcherInterface

V1 = b'{"claim":"mature-tool-receipt","source":"system-A","version":"1","scope":"bounded"}\n'
V2 = V1.replace(b'"version":"1"', b'"version":"2"')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def signed_metadata(metadata: Metadata, signers: list[CryptoSigner]) -> bytes:
    metadata.signatures.clear()
    for signer in signers:
        metadata.sign(signer, append=True)
    return metadata.to_bytes(JSONSerializer())


def make_root(
    *,
    version: int,
    root_signing_keys: list[CryptoSigner],
    root_role_keys: list[CryptoSigner],
    targets_key: CryptoSigner,
    timestamp_key: CryptoSigner,
    snapshot_key: CryptoSigner,
) -> bytes:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    root = Root(version=version, spec_version="1.0", expires=now + dt.timedelta(days=365))
    root.consistent_snapshot = False
    for role_name, key in (
        ("targets", targets_key),
        ("timestamp", timestamp_key),
        ("snapshot", snapshot_key),
    ):
        root.add_key(key.public_key, role_name)
        root.roles[role_name] = Role([key.public_key.keyid], 1)
    for key in root_role_keys:
        root.add_key(key.public_key, "root")
    root.roles["root"] = Role([key.public_key.keyid for key in root_role_keys], 1)
    return signed_metadata(Metadata(root), root_signing_keys)


def make_repository_state(
    data: bytes,
    version: int,
    *,
    targets_key: CryptoSigner,
    timestamp_key: CryptoSigner,
    snapshot_key: CryptoSigner,
) -> dict[str, bytes]:
    expires = dt.datetime.now(dt.timezone.utc).replace(microsecond=0) + dt.timedelta(days=7)
    targets = Targets(version=version, spec_version="1.0", expires=expires)
    targets.targets["receipt"] = TargetFile.from_data("receipt", data, ["sha256"])
    targets_bytes = signed_metadata(Metadata(targets), [targets_key])

    snapshot = Snapshot(version=version, spec_version="1.0", expires=expires)
    snapshot.meta["targets.json"] = MetaFile(
        version, len(targets_bytes), {"sha256": digest(targets_bytes)}
    )
    snapshot_bytes = signed_metadata(Metadata(snapshot), [snapshot_key])

    timestamp = Timestamp(version=version, spec_version="1.0", expires=expires)
    timestamp.snapshot_meta = MetaFile(
        version, len(snapshot_bytes), {"sha256": digest(snapshot_bytes)}
    )
    timestamp_bytes = signed_metadata(Metadata(timestamp), [timestamp_key])
    return {
        "targets": targets_bytes,
        "snapshot": snapshot_bytes,
        "timestamp": timestamp_bytes,
    }


class FixtureFetcher(FetcherInterface):
    def __init__(
        self,
        roots: dict[int, bytes],
        state: dict[str, bytes],
        target: bytes,
    ) -> None:
        self.roots = roots
        self.state = state
        self.target = target

    def _fetch(self, url: str):
        path = urlparse(url).path
        if path.startswith("/metadata/"):
            name = path[len("/metadata/") : -5]
            if name.endswith(".root"):
                version = int(name.split(".", 1)[0])
                if version not in self.roots:
                    raise DownloadHTTPError(f"GET {url}: not found", 404)
                yield self.roots[version]
                return
            yield self.state[name.split(".", 1)[-1]]
            return
        if path.startswith("/targets/"):
            yield self.target
            return
        raise RuntimeError(path)


def verify_historical_metadata(metadata_bytes: bytes, root_bytes: bytes) -> None:
    root = Metadata.from_bytes(root_bytes)
    historical = Metadata.from_bytes(metadata_bytes)
    root.signed.verify_delegate(
        "targets",
        historical.signed.to_bytes(JSONSerializer()),
        historical.signatures,
    )


def run_tuf_compromise_recovery() -> None:
    old_root = CryptoSigner.generate_ed25519()
    new_root = CryptoSigner.generate_ed25519()
    attacker_root = CryptoSigner.generate_ed25519()
    old_targets = CryptoSigner.generate_ed25519()
    new_targets = CryptoSigner.generate_ed25519()
    timestamp = CryptoSigner.generate_ed25519()
    snapshot = CryptoSigner.generate_ed25519()

    root1 = make_root(
        version=1,
        root_signing_keys=[old_root],
        root_role_keys=[old_root],
        targets_key=old_targets,
        timestamp_key=timestamp,
        snapshot_key=snapshot,
    )

    # A malicious replacement signed only by the compromised old root.
    malicious_root2 = make_root(
        version=2,
        root_signing_keys=[old_root],
        root_role_keys=[attacker_root],
        targets_key=attacker_root,
        timestamp_key=timestamp,
        snapshot_key=snapshot,
    )

    # Legitimate rotation: the transition root is signed by the old and new
    # root keys and introduces the new targets key.
    root2 = make_root(
        version=2,
        root_signing_keys=[old_root, new_root],
        root_role_keys=[old_root, new_root],
        targets_key=new_targets,
        timestamp_key=timestamp,
        snapshot_key=snapshot,
    )

    # Recovery is complete: the old root key is removed from the root role.
    root3 = make_root(
        version=3,
        root_signing_keys=[new_root],
        root_role_keys=[new_root],
        targets_key=new_targets,
        timestamp_key=timestamp,
        snapshot_key=snapshot,
    )

    # Any later root signed only by the compromised old key must remain
    # unacceptable after the rotation.
    malicious_root4 = make_root(
        version=4,
        root_signing_keys=[old_root],
        root_role_keys=[attacker_root],
        targets_key=attacker_root,
        timestamp_key=timestamp,
        snapshot_key=snapshot,
    )

    old_state = make_repository_state(
        V1, 1, targets_key=old_targets, timestamp_key=timestamp, snapshot_key=snapshot
    )
    new_state = make_repository_state(
        V2, 2, targets_key=new_targets, timestamp_key=timestamp, snapshot_key=snapshot
    )

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        # 1. A compromised signer cannot unilaterally substitute a new root.
        try:
            Updater(
                str(base / "bootstrap"),
                "https://probe.invalid/metadata/",
                str(base / "targets"),
                "https://probe.invalid/targets/",
                FixtureFetcher({2: malicious_root2}, old_state, V1),
                bootstrap=root1,
            ).refresh()
        except (UnsignedMetadataError, BadVersionNumberError):
            print("tuf_compromised_root_rejected=PASS")
        else:
            raise AssertionError("compromised root substitution accepted")

        # 2. Authorized transition is accepted and recovery continues to root3.
        updater = Updater(
            str(base / "rotation"),
            "https://probe.invalid/metadata/",
            str(base / "targets-rotation"),
            "https://probe.invalid/targets/",
            FixtureFetcher({2: root2, 3: root3}, new_state, V2),
            bootstrap=root1,
        )
        updater.refresh()
        info = updater.get_targetinfo("receipt")
        assert info is not None
        assert Path(updater.download_target(info)).read_bytes() == V2
        print("tuf_root_rotation_recovery=PASS")

        # 3. After root3, the old root cannot re-enter the trust chain.
        try:
            Updater(
                str(base / "post-rotation"),
                "https://probe.invalid/metadata/",
                str(base / "targets-post-rotation"),
                "https://probe.invalid/targets/",
                FixtureFetcher({2: root2, 3: root3, 4: malicious_root4}, new_state, V2),
                bootstrap=root1,
            ).refresh()
        except UnsignedMetadataError:
            print("tuf_old_root_rejected_after_rotation=PASS")
        else:
            raise AssertionError("old root regained trust after rotation")

        # 4. Historical evidence remains cryptographically verifiable under
        # the historical root, even though the current root no longer accepts
        # the historical target signer.
        verify_historical_metadata(old_state["targets"], root1)
        print("tuf_historical_receipt_verification=PASS")

        current_root = Metadata.from_bytes(root3)
        historical_targets = Metadata.from_bytes(old_state["targets"])
        try:
            current_root.signed.verify_delegate(
                "targets",
                historical_targets.signed.to_bytes(JSONSerializer()),
                historical_targets.signatures,
            )
        except UnsignedMetadataError:
            print("tuf_historical_receipt_not_currently_admissible=PASS")
        else:
            raise AssertionError("historical target signer remained current-admissible")


if __name__ == "__main__":
    run_tuf_compromise_recovery()
    print("TRUST_RECOVERY_TUF=PASS")
