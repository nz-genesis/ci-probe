"""Cross-domain consumption clean-room probe."""
from dataclasses import dataclass
import hashlib,json
@dataclass(frozen=True)
class Envelope:
 operation_id:str; producer_domain:str; schema:str; version:int; authority:str; capability:str; payload:tuple; lineage:str; digest:str
def make(**x):
 m=json.dumps({**x,'payload':sorted(x['payload'])},sort_keys=True); return Envelope(**x,digest=hashlib.sha256(m.encode()).hexdigest())
def consume(e,**p):
 m=json.dumps({'operation_id':e.operation_id,'producer_domain':e.producer_domain,'schema':e.schema,'version':e.version,'authority':e.authority,'capability':e.capability,'payload':sorted(e.payload),'lineage':e.lineage},sort_keys=True)
 return hashlib.sha256(m.encode()).hexdigest()==e.digest and e.schema==p['schema'] and e.version>=p['version'] and e.authority==p['authority'] and e.capability==p['capability'] and e.lineage==p['lineage']
def main():
 g=make(operation_id='op-1',producer_domain='A',schema='result/v1',version=1,authority='allow',capability='consume',payload=(('status','ready'),),lineage='l1')
 c=[consume(g,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l1'),consume(g,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l1')]
 o=make(operation_id='op-2',producer_domain='A',schema='result/v0',version=0,authority='allow',capability='consume',payload=(('status','ready'),),lineage='l2'); c += [not consume(o,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l2')]
 a=make(operation_id='op-3',producer_domain='A',schema='result/v1',version=1,authority='bad',capability='consume',payload=(('status','ready'),),lineage='l3'); c += [not consume(a,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l3')]
 x=make(operation_id='op-4',producer_domain='A',schema='result/v1',version=1,authority='allow',capability='execute',payload=(('status','ready'),),lineage='l4'); c += [not consume(x,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l4')]
 c += [not consume(g,schema='result/v1',version=1,authority='allow',capability='consume',lineage='other')]
 t=Envelope(g.operation_id,g.producer_domain,g.schema,g.version,g.authority,g.capability,(('status','corrupted'),),g.lineage,g.digest); c += [not consume(t,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l1')]
 b=make(operation_id='op-5',producer_domain='B',schema='result/v1',version=1,authority='allow',capability='consume',payload=(('status','ready'),),lineage='l5'); c += [consume(b,schema='result/v1',version=1,authority='allow',capability='consume',lineage='l5')]
 r=make(operation_id='op-6',producer_domain='A',schema='result/v1',version=1,authority='allow',capability='consume',payload=(('status','ready'),),lineage='l6'); c += [consume(Envelope(**r.__dict__),schema='result/v1',version=1,authority='allow',capability='consume',lineage='l6')]
 assert len(c)==9 and all(c); print('CROSS-DOMAIN CONSUMPTION: 9/9 PASS')
main()
