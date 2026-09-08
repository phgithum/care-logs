import json, sys, os, subprocess

now = sys.argv[1] if len(sys.argv) > 1 else ''
hook = os.environ.get('HOOK', '')
cfg = json.load(open('config.json', encoding='utf-8'))
for t in cfg.get('tasks', []):
    if t.get('t') == now:
        body = json.dumps({'msgtype': 'text',
                           'text': {'content': t.get('msg', ''),
                                    'mentioned_list': ['@all']}})
        subprocess.run(['curl', '-s', '-X', 'POST', hook,
                        '-H', 'Content-Type: application/json', '-d', body])
