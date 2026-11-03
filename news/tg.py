#!/usr/bin/env python3
"""Telegram təsdiqi.
  python3 news/tg.py send <drafts/slug.json>   # qaralamanı video + düymələrlə göndərir
  python3 news/tg.py poll                      # düymə basışlarını oxuyur: ✅ → publish.py, ❌ → ləğv
Açarlar (mühit və ya news/.env): TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
"""
import json, os, sys, uuid, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'tg_state.json')


def env(k):
    v = os.environ.get(k)
    if not v and os.path.exists(os.path.join(HERE, '.env')):
        for l in open(os.path.join(HERE, '.env')):
            if l.startswith(k + '='): v = l.split('=', 1)[1].strip()
    return v.strip() if v else v


def api(method, data=None, files=None):
    url = f'https://api.telegram.org/bot{env("TELEGRAM_TOKEN")}/{method}'
    if files:
        b = uuid.uuid4().hex; body = b''
        for k, v in (data or {}).items():
            body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, path in files.items():
            body += (f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(path)}"\r\n'
                     f'Content-Type: application/octet-stream\r\n\r\n').encode() + open(path, 'rb').read() + b'\r\n'
        body += f'--{b}--\r\n'.encode()
        req = urllib.request.Request(url, data=body, headers={'Content-Type': f'multipart/form-data; boundary={b}'})
    else:
        req = urllib.request.Request(url, data=json.dumps(data or {}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.load(r)
    if not j.get('ok'): raise RuntimeError(j)
    return j['result']


def ans(data):
    try: api('answerCallbackQuery', data)  # köhnə düymələrdə Telegram xəta verir — vacib deyil
    except Exception: pass


def caption(d, status=''):
    E = html.escape
    s = (f'🆕 <b>Yeni xəbər — təsdiq gözləyir</b>\n\n<b>{E(d["title"])}</b>\n{E(d["lead"])}\n\n'
         f'🔥 Viral: {d.get("viral", "?")}/10 · 🏷 {E(d["category"])}\n'
         f'📰 Mənbə: <a href="{E(d["source"]["url"])}">{E(d["source"]["name"])}</a>\n\n'
         f'<b>Instagram mətni:</b>\n{E(d.get("ig_caption", ""))}')
    if status: s += f'\n\n{status}'
    return s[:1024]


def kb(slug):
    return json.dumps({'inline_keyboard': [[{'text': '✅ Paylaş', 'callback_data': f'ok:{slug}'[:64]},
                                             {'text': '❌ Ləğv et', 'callback_data': f'no:{slug}'[:64]}]]})


def send(path):
    d = json.load(open(path, encoding='utf-8'))
    video = os.path.join(HERE, 'out', d['slug'] + '.mp4')
    data = {'chat_id': env('TELEGRAM_CHAT_ID'), 'caption': caption(d), 'parse_mode': 'HTML', 'reply_markup': kb(d['slug']),
            'supports_streaming': 'true'}
    m = api('sendVideo', data, {'video': video}) if os.path.exists(video) else api('sendMessage', {
        'chat_id': data['chat_id'], 'text': data['caption'], 'parse_mode': 'HTML', 'reply_markup': json.loads(data['reply_markup'])})
    d['tg_message'] = m['message_id']; d['status'] = 'pending'
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('göndərildi:', d['slug'])


def poll():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {'offset': 0}
    ups = api('getUpdates', {'offset': st['offset'], 'timeout': 0, 'allowed_updates': ['callback_query']})
    for u in ups:
        st['offset'] = u['update_id'] + 1
        q = u.get('callback_query')
        if not q or str(q['message']['chat']['id']) != str(env('TELEGRAM_CHAT_ID')): continue
        act, slug = q['data'].split(':', 1)
        path = os.path.join(HERE, 'drafts', slug + '.json')
        if not os.path.exists(path):
            ans({'callback_query_id': q['id'], 'text': 'Qaralama tapılmadı'}); continue
        d = json.load(open(path, encoding='utf-8'))
        if d.get('status') in ('published', 'rejected'):
            ans({'callback_query_id': q['id'], 'text': 'Artıq edilib'}); continue
        if act == 'ok':
            ans({'callback_query_id': q['id'], 'text': 'Paylaşılır…'})
            import publish
            res = publish.publish(path)
            status = '✅ <b>Saytda paylaşıldı</b>' + (' · Instagram: ' + res['ig'] if res.get('ig') else '')
        else:
            d['status'] = 'rejected'; json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            ans({'callback_query_id': q['id'], 'text': 'Ləğv edildi'})
            status = '❌ <b>Ləğv edildi</b>'
        method = 'editMessageCaption' if q['message'].get('video') else 'editMessageText'
        key = 'caption' if method == 'editMessageCaption' else 'text'
        try: api(method, {'chat_id': q['message']['chat']['id'], 'message_id': q['message']['message_id'],
                          key: caption(d, status), 'parse_mode': 'HTML'})
        except Exception as e: print('  ! edit:', e)
    json.dump(st, open(STATE, 'w'))
    print('yeniləmələr:', len(ups))


def send_new():
    """Hələ göndərilməmiş qaralamalar üçün Reels hazırlayır və Telegram-a göndərir."""
    import subprocess
    dd = os.path.join(HERE, 'drafts')
    for f in sorted(os.listdir(dd)) if os.path.isdir(dd) else []:
        p = os.path.join(dd, f)
        if not f.endswith('.json') or json.load(open(p, encoding='utf-8')).get('status'): continue
        subprocess.run([sys.executable, os.path.join(HERE, 'reels.py'), p], check=True)
        send(p)


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    if len(sys.argv) > 1 and sys.argv[1] == 'send-new': send_new()
    elif len(sys.argv) > 2 and sys.argv[1] == 'send': send(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == 'poll': poll()
    else: print(__doc__)
