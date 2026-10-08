#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
ap=argparse.ArgumentParser(); ap.add_argument("directory"); a=ap.parse_args()
root=Path(a.directory).resolve(); files=[]
for p in sorted(root.rglob("*")):
    if p.is_file() and p.name!="manifest.json":
        files.append({"path":str(p.relative_to(root)),"sha256":digest(p),"size":p.stat().st_size})
(root/"manifest.json").write_text(json.dumps({"schema":"p347-n100-witness-manifest-v1","files":files},indent=2,sort_keys=True)+"\n")
print(root/"manifest.json")
