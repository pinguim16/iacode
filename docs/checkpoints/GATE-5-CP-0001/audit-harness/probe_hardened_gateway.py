"""Actual owned hardened worker/API/provider diagnosis; no substitution or model change."""

import json
import os
import secrets
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from compose import compose, read_env_file, wait_for_health  # noqa: E402
from desktop_test_support import environment  # noqa: E402
from verify import VERIFICATION_PORT_VARIABLES  # noqa: E402

WORKER = """
import asyncio,json,sys
from iacode_orchestrator.config import WorkerSettings
from iacode_orchestrator.agent_runtime.runtime_context import build_context
from iacode_agent_runtime.gateway_client import MODELS_PATH,INFER_PATH
from iacode_agent_runtime.errors import AgentRuntimeError
async def main():
    ctx=build_context(WorkerSettings())
    report={'kind':'ACTUAL_HARDENED_WORKER_GATEWAY_DIAGNOSIS_NOT_TASK_ACCEPTANCE','steps':[],'result':'FAIL'}
    try:
        for name,path,payload in [('sync',MODELS_PATH+'/sync',{'provider':sys.argv[1].partition(':')[0]}),('catalog',MODELS_PATH,None),('infer',INFER_PATH,
            {'model':sys.argv[1],'messages':[{'role':'user','content':'Reply only with OK.'}],'maxOutputTokens':32})]:
            try:
                data=await(ctx.model_client._get(path) if payload is None else ctx.model_client._post(path,payload))
                present=any(row['provider']+':'+row['model']==sys.argv[1] and row['active'] for row in data.get('models',[]))
                sync_ok=bool(data.get('outcomes')) and all(not row['errors'] for row in data.get('outcomes',[]))
                ok=sync_ok if name=='sync' else present if name=='catalog' else bool(data.get('content'))
                report['steps'].append({'name':name,'result':'PASS' if ok else 'FAIL',
                    'modelCount':len(data.get('models',[])),'authorizedModelPresent':present,
                    'hasContent':bool(data.get('content')),'syncErrorCount':sum(len(row['errors']) for row in data.get('outcomes',[]))})
                if not ok:break
            except AgentRuntimeError as error:
                report['steps'].append({'name':name,'result':'FAIL','errorType':str(error.error_type),
                    'upstreamType':error.upstream_type,'reason':error.details.get('reason'),
                    'status':error.details.get('status'),'causeType':type(error.__cause__).__name__})
                break
            except Exception as error:
                report['steps'].append({'name':name,'result':'FAIL','causeType':type(error).__name__})
                break
        if len(report['steps'])==3 and all(row['result']=='PASS' for row in report['steps']):report['result']='PASS'
    finally:await ctx.close()
    print(json.dumps(report))
asyncio.run(main())
"""


def main():
    values = read_env_file()
    model = os.environ.get("IACODE_GATEWAY_SMOKE_MODEL") or values.get("IACODE_GATEWAY_SMOKE_MODEL")
    if not model:
        raise ValueError("actual authorized smoke model required; never substituted")
    project = "iacode-desktop-" + uuid.uuid4().hex[:12]
    key = secrets.token_hex(32)
    owned = {"COMPOSE_PROJECT_NAME": project, **dict.fromkeys(VERIFICATION_PORT_VARIABLES, "0"),
             "IACODE_DESKTOP_TOKEN": key,
             "IACODE_DESKTOP_TOKEN_EXPIRES_AT": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
             "IACODE_GATEWAY_DEFAULT_MODEL": model}
    report = {"project": project, "authorizedModel": model, "result": "FAIL"}
    with environment(owned):
        try:
            started = compose("up", "-d", "--build", timeout=600)
            if not started.ok:
                raise RuntimeError("owned diagnostic startup failed")
            wait_for_health(timeout=300)
            observed = compose("exec", "-T", "worker", "python", "-c", WORKER, model, timeout=300)
            if not observed.ok:
                raise RuntimeError("owned diagnostic worker invocation failed")
            report["worker"] = json.loads(observed.stdout)
            report["result"] = report["worker"]["result"]
        finally:
            report["cleanupExitCode"] = compose("down", "--volumes", "--remove-orphans", timeout=180).exit_code
    target = ROOT / "var/hardened-gateway-diagnosis.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" and report["cleanupExitCode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
