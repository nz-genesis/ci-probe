#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, platform, subprocess, socket
from datetime import datetime, timezone
from pathlib import Path
def run(*args: str):
    try: return True, subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc: return False, f'{type(exc).__name__}: {exc}'
def digest(payload):
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); return hashlib.sha256(raw).hexdigest()
identity={'hostname':socket.gethostname(),'platform':platform.platform(),'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'python':platform.python_version(),'runner_name':os.environ.get('RUNNER_NAME',''),'runner_os':os.environ.get('RUNNER_OS',''),'runner_arch':os.environ.get('RUNNER_ARCH',''),'github_run_id':os.environ.get('GITHUB_RUN_ID',''),'github_sha':os.environ.get('GITHUB_SHA',''),'github_ref':os.environ.get('GITHUB_REF',''),'git_checked_out_sha':run('git','rev-parse','HEAD')[1]}
commands={'python3':('python3','--version'),'curl':('curl','--version'),'tcpdump':('tcpdump','--version'),'pfctl':('pfctl','-s','info'),'networksetup':('networksetup','-listallhardwareports'),'route':('route','-n','get','default')}
capabilities={}
for name,command in commands.items():
    ok,output=run(*command); capabilities[name]={'available':ok,'sample':output.splitlines()[0][:240] if output else ''}
contract={'probe':'P347_MAC_EXECUTION_MATRIX_V1','contract_version':1,'action':'canonical_identity_and_capability_observation','required_fields':['hostname','system','machine','git_checked_out_sha']}
record={'probe':'P347_MAC_EXECUTION_MATRIX_V1','observed_at':datetime.now(timezone.utc).isoformat(),'identity':identity,'contract':contract,'contract_sha256':digest(contract),'capabilities':capabilities,'security_boundary':{'trusted_push_only':True,'pull_request_triggers':False,'jit_ephemeral_expected':True},'evidence_class':{'execution_environment':'eligible','semantic_independence':'not_claimed','external_authority_independence':'not_claimed','network_witness':'not_claimed','physical_effect':'not_claimed'}}
Path('p347-mac-execution-matrix.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2,sort_keys=True))
if identity['system']!='Darwin': raise SystemExit('P347_MAC_EXECUTION_MATRIX=FAIL_NOT_MAC')
required=['python3','curl','tcpdump','pfctl','networksetup','route']
missing=[name for name in required if not capabilities[name]['available']]
if missing:
    print('P347_MAC_EXECUTION_MATRIX=BLOCKED'); print('Missing capabilities:',', '.join(missing)); raise SystemExit(2)
print('P347_MAC_EXECUTION_MATRIX=PASS')
