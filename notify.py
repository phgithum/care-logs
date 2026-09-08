import json, sys, os, subprocess

now = sys.argv[1] if len(sys.argv) > 1 else ''
hook = os.environ.get('HOOK', '')
cfg = json.load(open('config.json', encoding='utf-8'))
for t in cfg.get('tasks', []):
    if t.get('t') != now:
        continue
    text = {'content': t.get('msg', '')}
    at = str(t.get('at', 'all')).strip()
    if at == 'all':
        text['mentioned_list'] = ['@all']
    elif at:
        text['mentioned_mobile_list'] = [p.strip() for p in at.split(',') if p.strip()]
    body = json.dumps({'msgtype': 'text', 'text': text})
    subprocess.run(['curl', '-s', '-X', 'POST', hook,
                    '-H', 'Content-Type: application/json', '-d', body])
