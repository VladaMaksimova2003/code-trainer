import json
import subprocess

script = r"""
import json
from infrastructure.execution.execution_guard import mark_worker_context
mark_worker_context()
from infrastructure.db.models.task.registry import load_models
load_models()
import psycopg2
conn = psycopg2.connect(host='postgres', port=5432, dbname='code_trainer', user='code_trainer', password='change_me')
cur = conn.cursor()
cur.execute('select code_examples from task where id=5')
raw = cur.fetchone()[0]
ce = raw if isinstance(raw, dict) else json.loads(raw)
code = ce['csharp']
from application.execution.pipeline_runner import WorkerPipelineRunner
r = WorkerPipelineRunner().run_submission(5, code, 'csharp')
print(json.dumps({'success': r.get('success'), 'tests': r.get('test_results')[:2], 'msg': (r.get('test_results') or [{}])[0].get('message','')}, ensure_ascii=False))
"""
cmd = ["docker", "exec", "code_trainer_dev-worker-1", "python", "-c", script]
proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
print(proc.stdout)
print(proc.stderr[-800:] if proc.stderr else "")
