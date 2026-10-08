#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,platform,socket,subprocess,os
from datetime import datetime,timezone

def run(*args):
    try: return True,subprocess.check_output(args,text=True,stderr=subprocess.STDOUT).strip()
    except Exception as exc: return False,f'{type(exc).__name__}: {exc}'

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

contract={
  'name':'P347_DIFFERENTIAL_REALIZATION_V1',
  'version':1,
  'operation':'observe_runtime_identity_and_canonical_contract',
  'required_identity':['system','machine','python','git_checked_out_sha'],
}
identity={
 'system':platform.system(),'release':platform.release(),'machine':platform.machine(),
 'python':platform.python_version(),'hostname':socket.gethostname(),
 'runner_name':os.environ.get('RUNNER_NAME',''),'runner_os':os.environ.get('RUNNER_OS',''),
 'runner_arch':os.environ.get('RUNNER_ARCH',''),'git_checked_out_sha':run('git','rev-parse','HEAD')[1],
}
result={
 'probe':'P347_DIFFERENTIAL_REALIZATION_V1','observed_at':datetime.now(timezone.utc).isoformat(),
 'contract':contract,'contract_sha256':digest(contract),'identity':identity,
 'observation':{'python_ok':True,'git_sha_matches_trigger':identity['git_checked_out_sha']==os.environ.get('GITHUB_SHA','')},
}
print(json.dumps(result,indent=2,sort_keys=True))
print('P347_DIFFERENTIAL_CONTRACT_SHA256='+result['contract_sha256'])
if not result['observation']['git_sha_matches_trigger']: raise SystemExit('P347_DIFFERENTIAL=FAIL_CHECKOUT')
print('P347_DIFFERENTIAL_REALIZATION=PASS
')
