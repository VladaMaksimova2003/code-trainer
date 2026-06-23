import json
from pathlib import Path
data=json.loads(Path('algo_syntax_course.json').read_text(encoding='utf-8'))
for n in [86, 34, 38, 214]:
    pass
for t in data:
    if t['task_num']==86:
        print('=== task 86 ===')
        print('title:', t['title'])
        print('short:', t['short_goal'])
        print('desc:', t['detailed_description'])
        print('format:', t['format_ru'])
        for lang in ['pascal','java']:
            impl=t['implementations'][lang]
            print(lang, 'ph:', (impl.get('placeholder_code') or '')[:120])
            print(lang, 'gaps:', len(impl.get('gaps') or []))
