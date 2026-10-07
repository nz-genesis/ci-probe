#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt
import hashlib
import inspect
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from in_toto.models.layout import Layout, Step
from in_toto.models.metadata import Metablock
from in_toto.runlib import in_toto_run
from in_toto.verifylib import in_toto_verify
from securesystemslib.signer import CryptoSigner
from tuf.api.exceptions import BadVersionNumberError, DownloadHTTPError, ExpiredMetadataError, LengthOrHashMismatchError
from tuf.api.metadata import Metadata, MetaFile, Root, Role, Snapshot, TargetFile, Targets, Timestamp
from tuf.api.serialization.json import JSONSerializer
from tuf.ngclient import Updater
from tuf.ngclient.fetcher import FetcherInterface

V1=b'{"claim":"mature-tool-receipt","source":"system-A","version":"1","scope":"bounded"}\n'
V2=V1.replace(b'"version":"1"',b'"version":"2"')

def h(x): return hashlib.sha256(x).hexdigest()
def sign(md,s): md.signatures.clear(); md.sign(s,append=True); return md.to_bytes(JSONSerializer())

class F(FetcherInterface):
    def __init__(self,roots,state,target): self.roots=roots; self.state=state; self.target=target
    def _fetch(self,url):
        p=urlparse(url).path
        if p.startswith("/metadata/"):
            n=p[len("/metadata/"):-5]
            if n.endswith(".root"):
                version=int(n.split(".",1)[0])
                if version not in self.roots:
                    raise DownloadHTTPError(f"GET {url}: not found", 404)
                yield self.roots[version]
                return
            yield self.state[n.split(".",1)[-1]]
            return
        if p.startswith("/targets/"): yield self.target; return
        raise RuntimeError(p)

def root(signers):
    now=dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    r=Root(version=1,spec_version="1.0",expires=now+dt.timedelta(days=365)); r.consistent_snapshot=False
    for role in ("root","timestamp","snapshot","targets"):
        r.add_key(signers[role].public_key,role); r.roles[role]=Role([signers[role].public_key.keyid],1)
    return sign(Metadata(r),signers["root"])

def state(data,version,signers):
    exp=dt.datetime.now(dt.timezone.utc).replace(microsecond=0)+dt.timedelta(days=7)
    t=Targets(version=version,spec_version="1.0",expires=exp); t.targets["receipt"]=TargetFile.from_data("receipt",data,["sha256"]); tb=sign(Metadata(t),signers["targets"])
    s=Snapshot(version=version,spec_version="1.0",expires=exp); s.meta["targets.json"]=MetaFile(version,len(tb),{"sha256":h(tb)}); sb=sign(Metadata(s),signers["snapshot"])
    ts=Timestamp(version=version,spec_version="1.0",expires=exp); ts.snapshot_meta=MetaFile(version,len(sb),{"sha256":h(sb)}); tsb=sign(Metadata(ts),signers["timestamp"])
    return {"targets":tb,"snapshot":sb,"timestamp":tsb}

def run_intoto():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td); (p/"receipt").write_bytes(V1)
        owner=CryptoSigner.generate_ed25519(); fn=CryptoSigner.generate_ed25519()
        functionary_public = fn.public_key.to_dict()
        functionary_public["keyid"] = fn.public_key.keyid
        l=Layout(); l.set_relative_expiration(days=1); l.add_functionary_key(functionary_public)
        step=Step(name="receipt"); step.pubkeys=[fn.public_key.keyid]; step.expected_command=["python3","-c","pass"]; step.add_product_rule_from_string("CREATE receipt"); step.add_product_rule_from_string("DISALLOW *"); l.steps=[step]
        m=Metablock(signed=l); m.create_signature(owner); m.dump(str(p/"root.layout"))
        old=Path.cwd(); os.chdir(p)
        try:
            link=in_toto_run("receipt",[],["receipt"],["python3","-c","pass"],record_streams=True,signer=fn)
            assert link.signed.products["receipt"]["sha256"]==h(V1)
            params=inspect.signature(in_toto_verify).parameters; assert "metadata" in params and "layout_key_dict" in params
            owner_public = owner.public_key.to_dict()
            owner_public["keyid"] = owner.public_key.keyid
            in_toto_verify(metadata=m,layout_key_dict={owner.public_key.keyid:owner_public})
            # in-toto verifies the signed Link/authorized process evidence.
            # Live target mutation is a TUF distribution-layer test below.
            # Here we tamper with the signed Link while keeping its old signature.
            link_files = list(p.glob("receipt.*.link"))
            assert len(link_files) == 1
            link_md = Metablock.load(str(link_files[0]))
            link_md.signed.products["receipt"]["sha256"] = "0" * 64
            link_md.dump(str(link_files[0]))
            try: in_toto_verify(metadata=m,layout_key_dict={owner.public_key.keyid:owner_public})
            except Exception: print("intoto_link_tamper_detection=PASS")
            else: raise AssertionError("in-toto accepted tampered Link")
        finally: os.chdir(old)
    print("intoto_valid=PASS")

def run_tuf():
    ss={r:CryptoSigner.generate_ed25519() for r in ("root","timestamp","snapshot","targets")}
    bootstrap_root_md=Metadata.from_bytes(root(ss))
    bootstrap_root_md.signed.version=5
    bootstrap_root=sign(bootstrap_root_md,ss["root"])
    root6_md=Metadata.from_bytes(bootstrap_root); root6_md.signed.version=6
    root6=sign(root6_md,ss["root"])
    root7_md=Metadata.from_bytes(root6); root7_md.signed.version=7
    root7=sign(root7_md,ss["root"])
    a=state(V1,1,ss); b=state(V2,2,ss)
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); md=d/"md"; tg=d/"tg"
        u=Updater(str(md),"https://probe.invalid/metadata/",str(tg),"https://probe.invalid/targets/",F({6:root6,7:root7},a,V1),bootstrap=bootstrap_root); u.refresh(); info=u.get_targetinfo("receipt"); assert info is not None; assert Path(u.download_target(info)).read_bytes()==V1; print("tuf_valid=PASS")
        u2=Updater(str(md),"https://probe.invalid/metadata/",str(tg),"https://probe.invalid/targets/",F({6:root6,7:root7},b,V2),bootstrap=bootstrap_root); u2.refresh(); print("tuf_forward=PASS")
        u3=Updater(str(md),"https://probe.invalid/metadata/",str(tg),"https://probe.invalid/targets/",F({6:root6,7:root7},a,V1),bootstrap=bootstrap_root)
        try: u3.refresh()
        except BadVersionNumberError: print("tuf_rollback=PASS")
        else: raise AssertionError("rollback accepted")
        u4=Updater(str(md/"mix"),"https://probe.invalid/metadata/",str(tg/"mix"),"https://probe.invalid/targets/",F({6:root6,7:root7},b,V1),bootstrap=bootstrap_root)
        try:
            u4.refresh()
            mix_info=u4.get_targetinfo("receipt")
            assert mix_info is not None
            u4.download_target(mix_info)
        except LengthOrHashMismatchError: print("tuf_mixmatch=PASS")
        else: raise AssertionError("mixmatch accepted")
        e=dict(b); tm=Metadata.from_bytes(e["timestamp"]); tm.signed.expires=dt.datetime.now(dt.timezone.utc)-dt.timedelta(minutes=1); e["timestamp"]=sign(tm,ss["timestamp"])
        u5=Updater(str(md/"expired"),"https://probe.invalid/metadata/",str(tg/"expired"),"https://probe.invalid/targets/",F({6:root6,7:root7},e,V2),bootstrap=bootstrap_root)
        try: u5.refresh()
        except ExpiredMetadataError: print("tuf_expiry=PASS")
        else: raise AssertionError("expired metadata accepted")

def run_compromise_recovery():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        old_key, old_pub = d/"old.key", d/"old.pub"
        new_key, new_pub = d/"new.key", d/"new.pub"
        receipts = [
            ("pre", d/"pre.json", 100, old_key, d/"pre.sig"),
            ("post", d/"post.json", 300, old_key, d/"post.sig"),
            ("recovered", d/"recovered.json", 400, new_key, d/"recovered.sig"),
        ]
        for key, pub in ((old_key, old_pub), (new_key, new_pub)):
            subprocess.run(["openssl","genpkey","-algorithm","ED25519","-out",str(key)], check=True)
            subprocess.run(["openssl","pkey","-in",str(key),"-pubout","-out",str(pub)], check=True)

        for name, receipt, signed_at, key, sig in receipts:
            receipt.write_text(
                '{"claim":"genesis-receipt","event":"effect","version":"1","signed_at":%d}\n' % signed_at,
                encoding="utf-8",
            )
            subprocess.run(
                ["openssl","pkeyutl","-sign","-inkey",str(key),"-rawin","-in",str(receipt),"-out",str(sig)],
                check=True,
            )

        for name, receipt, signed_at, key, sig in receipts:
            pub = old_pub if key == old_key else new_pub
            subprocess.run(
                ["openssl","pkeyutl","-verify","-pubin","-inkey",str(pub),"-rawin",
                 "-in",str(receipt),"-sigfile",str(sig)],
                check=True,
            )

        compromise_epoch = 200
        evidence = [
            {"id":"pre","signer":"old","signed_at":100,"receipt":receipts[0][1]},
            {"id":"post","signer":"old","signed_at":300,"receipt":receipts[1][1]},
            {"id":"recovered","signer":"new","signed_at":400,"receipt":receipts[2][1]},
        ]

        def admit(e):
            if e["signer"] == "old" and e["signed_at"] >= compromise_epoch:
                return False
            return e["signer"] == "new" or (e["signer"] == "old" and e["signed_at"] < compromise_epoch)

        assert admit(evidence[0]) is True
        assert admit(evidence[1]) is False
        assert admit(evidence[2]) is True

        # Red Team: changing the signed compromise boundary after signing must fail verification.
        tampered = d/"tampered.json"
        tampered.write_text(
            receipts[1][1].read_text(encoding="utf-8").replace('"signed_at":300','"signed_at":100'),
            encoding="utf-8",
        )
        result = subprocess.run(
            ["openssl","pkeyutl","-verify","-pubin","-inkey",str(old_pub),"-rawin",
             "-in",str(tampered),"-sigfile",str(receipts[1][4])],
            capture_output=True,
        )
        assert result.returncode != 0

        assert all(r.exists() and s.exists() for _, r, _, _, s in receipts)
        print("compromise_pre_historical_valid=PASS")
        print("compromise_post_cryptographically_valid_currently_inadmissible=PASS")
        print("compromise_new_trusted_signer_admissible=PASS")
        print("compromise_historical_lineage_preserved=PASS")
        print("compromise_signed_boundary_tamper_rejected=PASS")

if __name__=="__main__":
    run_intoto()
    run_tuf()
    run_compromise_recovery()
    print("MATURE_RECEIPT_TOOLS=PASS")
