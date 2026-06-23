import json, psycopg2
conn=psycopg2.connect(host='localhost',port=5433,dbname='code_trainer',user='code_trainer',password='change_me')
cur=conn.cursor()
for pid in ('task_068','task_076'):
 cur.execute("select test_cases from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s", (pid,))
 tests=json.loads(cur.fetchone()[0])
 print('===', pid)
 for i,t in enumerate(tests): print(i+1, repr(t.get('inputs')), '->', repr(t.get('output')))
cur.close(); conn.close()
