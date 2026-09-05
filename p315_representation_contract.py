"""P315 bounded probe: representation-independent semantic contract.

The probe uses independently authored heterogeneous fixtures and an explicit
oracle for five semantic guarantees. It tests three things: every fixture can
be adapted to the same semantic oracle; one mutation per guarantee is visible;
and representation-specific payload changes that do not affect the guarantees
remain semantically irrelevant. It does not benchmark or require a universal
physical envelope.
"""
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Oracle:
    identity: str
    version: int
    provenance: str
    integrity: str
    authority: str

ORACLE = Oracle("artifact-7", 3, "source-A", "sha256:payload-7", "authority-9")
GUARANTEES = ("identity", "version", "provenance", "integrity", "authority")

# Independently authored fixtures; no fixture is generated from ORACLE.
FIXTURES = {
    "research_md": """---
id: artifact-7
version: 3
provenance: source-A
integrity: sha256:payload-7
authority: authority-9
---
Human research record.
""",
    "machine_json": '{"meta":{"id":"artifact-7","version":3},"origin":"source-A","digest":"sha256:payload-7","auth":{"principal":"authority-9"},"value":{"x":1}}',
    "local_sqlite": {"id":"artifact-7","version":3,"provenance":"source-A","integrity":"sha256:payload-7","authority":"authority-9","payload":"x=1"},
    "signed_binary": b"ID=artifact-7|V=3|SRC=source-A|DIG=sha256:payload-7|AUTH=authority-9|PAY=x=1",
    "api_payload": {"headers":{"X-Artifact-ID":"artifact-7","X-Version":"3","X-Provenance":"source-A","X-Integrity":"sha256:payload-7","X-Authority":"authority-9"},"body":{"x":1}},
    "domain_payload": {"artifact_key":("artifact-7",3),"lineage":{"origin":"source-A"},"checksum":"sha256:payload-7","controller":"authority-9","domain_value":"x=1"},
    "graph_projection": {"nodes":[("artifact-7","artifact"),("source-A","source"),("authority-9","authority")],"edges":[("artifact-7","version","3"),("artifact-7","provenance","source-A"),("artifact-7","integrity","sha256:payload-7"),("artifact-7","authority","authority-9")]},
}

def adapt(name, value):
    if name == "research_md":
        head=value.split("---",2)[1]
        return {k.strip():(int(v.strip()) if k.strip()=="version" else v.strip()) for k,v in (line.split(":",1) for line in head.strip().splitlines())}
    if name == "machine_json":
        x=json.loads(value)
        return {"id":x["meta"]["id"],"version":x["meta"]["version"],"provenance":x["origin"],"integrity":x["digest"],"authority":x["auth"]["principal"]}
    if name == "local_sqlite":
        return {k:value[k] for k in ("id","version","provenance","integrity","authority")}
    if name == "signed_binary":
        raw={p.split("=",1)[0]:p.split("=",1)[1] for p in value.decode().split("|")}
        return {"id":raw["ID"],"version":int(raw["V"]),"provenance":raw["SRC"],"integrity":raw["DIG"],"authority":raw["AUTH"]}
    if name == "api_payload":
        h=value["headers"]
        return {"id":h["X-Artifact-ID"],"version":int(h["X-Version"]),"provenance":h["X-Provenance"],"integrity":h["X-Integrity"],"authority":h["X-Authority"]}
    if name == "domain_payload":
        return {"id":value["artifact_key"][0],"version":value["artifact_key"][1],"provenance":value["lineage"]["origin"],"integrity":value["checksum"],"authority":value["controller"]}
    if name == "graph_projection":
        artifact_id=next(n for n,t in value["nodes"] if t=="artifact")
        edges={(a,r):b for a,r,b in value["edges"]}
        return {"id":artifact_id,"version":int(edges[(artifact_id,"version")]),"provenance":edges[(artifact_id,"provenance")],"integrity":edges[(artifact_id,"integrity")],"authority":edges[(artifact_id,"authority")]}
    raise KeyError(name)

def project(fields):
    return Oracle(str(fields["id"]),int(fields["version"]),str(fields["provenance"]),str(fields["integrity"]),str(fields["authority"]))

def assert_all_match():
    for name, fixture in FIXTURES.items():
        assert project(adapt(name, fixture)) == ORACLE, name

def mutate(name, fixture, guarantee):
    bad={"identity":"artifact-X","version":4,"provenance":"source-B","integrity":"sha256:tampered","authority":"authority-X"}[guarantee]
    if name == "research_md":
        key={"identity":"id","version":"version","provenance":"provenance","integrity":"integrity","authority":"authority"}[guarantee]
        old={"identity":"artifact-7","version":"3","provenance":"source-A","integrity":"sha256:payload-7","authority":"authority-9"}[guarantee]
        return fixture.replace(f"{key}: {old}", f"{key}: {bad}")
    if name == "machine_json":
        x=json.loads(fixture)
        if guarantee=="identity": x["meta"]["id"]=bad
        elif guarantee=="version": x["meta"]["version"]=bad
        elif guarantee=="provenance": x["origin"]=bad
        elif guarantee=="integrity": x["digest"]=bad
        else: x["auth"]["principal"]=bad
        return json.dumps(x,separators=(",",":"))
    if name == "local_sqlite":
        return {**fixture,{"identity":"id","version":"version","provenance":"provenance","integrity":"integrity","authority":"authority"}[guarantee]:bad}
    if name == "signed_binary":
        key={"identity":"ID","version":"V","provenance":"SRC","integrity":"DIG","authority":"AUTH"}[guarantee]
        old={"identity":"artifact-7","version":"3","provenance":"source-A","integrity":"sha256:payload-7","authority":"authority-9"}[guarantee]
        return fixture.replace(f"{key}={old}".encode(),f"{key}={str(bad)}".encode())
    if name == "api_payload":
        h={"identity":"X-Artifact-ID","version":"X-Version","provenance":"X-Provenance","integrity":"X-Integrity","authority":"X-Authority"}[guarantee]
        return {**fixture,"headers":{**fixture["headers"],h:str(bad)}}
    if name == "domain_payload":
        if guarantee=="identity": return {**fixture,"artifact_key":(bad,fixture["artifact_key"][1])}
        if guarantee=="version": return {**fixture,"artifact_key":(fixture["artifact_key"][0],bad)}
        if guarantee=="provenance": return {**fixture,"lineage":{"origin":bad}}
        if guarantee=="integrity": return {**fixture,"checksum":bad}
        return {**fixture,"controller":bad}
    if name == "graph_projection":
        key={"version":"version","provenance":"provenance","integrity":"integrity","authority":"authority"}
        if guarantee=="identity":
            return {**fixture,"nodes":[(bad,t) if t=="artifact" else (n,t) for n,t in fixture["nodes"]],"edges":[(bad,r,v) if a=="artifact-7" else (a,r,v) for a,r,v in fixture["edges"]]}
        return {**fixture,"edges":[(a,r,str(bad) if r==key[guarantee] else b) for a,r,b in fixture["edges"]]}
    raise KeyError(name)

def assert_mutation_witnesses():
    count=0
    for name, fixture in FIXTURES.items():
        for guarantee in GUARANTEES:
            altered=mutate(name,fixture,guarantee)
            observed=project(adapt(name,altered))
            assert observed != ORACLE, (name,guarantee)
            assert getattr(observed,guarantee) != getattr(ORACLE,guarantee), (name,guarantee)
            count += 1
    assert count == 35

def assert_representation_specific_changes_do_not_change_guarantees():
    for name, fixture in FIXTURES.items():
        if name=="research_md": altered=fixture+"Editorial text may change.\n"
        elif name=="machine_json": altered=fixture.replace('"x":1','"x":999')
        elif name=="local_sqlite": altered={**fixture,"payload":"x=999"}
        elif name=="signed_binary": altered=fixture.replace(b"PAY=x=1",b"PAY=x=999")
        elif name=="api_payload": altered={**fixture,"body":{"x":999}}
        elif name=="domain_payload": altered={**fixture,"domain_value":"x=999"}
        else: altered={**fixture,"nodes":fixture["nodes"]+[("note-1","note")]}
        assert project(adapt(name,altered)) == ORACLE, name

def main():
    assert_all_match()
    assert_mutation_witnesses()
    assert_representation_specific_changes_do_not_change_guarantees()
    print("35/35 PASS")
    print("representation_specific_adapters=SUFFICIENT_FOR_TESTED_GUARANTEES")
    print("mutation_witnesses=35")
    print("representation_specific_changes_preserve_contract=7/7")
    print("universal_envelope_semantic_requirement=NOT_DEMONSTRATED")
    print("universal_format_requirement=NOT_DEMONSTRATED")
    print("new_data_primitive_required=false")

if __name__ == "__main__":
    main()
