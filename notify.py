import json, sys, os, subprocess, urllib.request
from datetime import datetime, timezone, timedelta

now = sys.argv[1] if len(sys.argv) > 1 else ''
hook = os.environ.get('HOOK', '')
wxp_token = os.environ.get('WXP_TOKEN', '')
wxp_uids = [u.strip() for u in os.environ.get('WXP_UIDS', '').split(',') if u.strip()]
wxp_topic = os.environ.get('WXP_TOPIC', '').strip()
cfg = json.load(open('config.json', encoding='utf-8'))
CST = timezone(timedelta(hours=8))
today = datetime.now(CST).strftime('%Y-%m-%d')

def wxp_send(text):
    """推送到个人微信（WxPusher）：uids 按人推，topic 按订阅组推，二者可同时配"""
    if not wxp_token or (not wxp_uids and not wxp_topic):
        return
    body = {'appToken': wxp_token, 'content': text, 'contentType': 1}
    if wxp_uids:
        body['uids'] = wxp_uids
    if wxp_topic:
        body['topicIds'] = [int(wxp_topic)]
    try:
        req = urllib.request.Request('https://wxpusher.zjiecode.com/api/send/message',
                                     data=json.dumps(body).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        r = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if not r.get('success'):
            print('wxpusher warn:', r.get('msg'))
    except Exception as e:
        print('wxpusher error:', e)

def send(text, at='all'):
    if hook:
        t = {'content': text}
        at = str(at if at is not None else 'all').strip()
        if at == 'all':
            t['mentioned_list'] = ['@all']
        elif at:
            t['mentioned_mobile_list'] = [p.strip() for p in at.split(',') if p.strip()]
        subprocess.run(['curl', '-s', '-X', 'POST', hook,
                        '-H', 'Content-Type: application/json', '-d', json.dumps({'msgtype': 'text', 'text': t})])
    wxp_send(text)

for t in cfg.get('tasks', []):
    if t.get('t') == now:
        send(t.get('msg', ''), t.get('at', 'all'))

b1, b2 = cfg.get('b1', '12:00'), cfg.get('b2', '18:00')
if now in (b1, b2):
    sk = 'a' if now == b1 else 'e'
    sn = '中' if now == b1 else '晚'
    who = ''
    try:
        data = json.load(open('data.json', encoding='utf-8'))
        who = (data.get('shifts', {}).get(today, {}) or {}).get(sk, '')
    except Exception:
        pass
    msg = '⏰ 交接班提醒\n现在进入【' + sn + '班】\n'
    msg += ('本班值班：' + who + '\n') if who else '本班还没人排班\n'
    msg += '上一班请到【看护记录】完成交接；本班记得记录护理情况'
    send(msg, 'all')
