"""TikTok-a avtomatik paylaşım — Upload-Post API (https://docs.upload-post.com).

Secret-lər: UPLOADPOST_API_KEY (vacib), UPLOADPOST_USER (istəyə görə — yoxdursa,
TikTok qoşulu olan profil API-dən avtomatik tapılır).
post(video, caption, key) -> {'ok': True, 'id': ..., 'user': ...} və ya {'ok': False, 'error': ...}
"""
import json, os, uuid, urllib.request, urllib.error

BASE = 'https://api.upload-post.com/api'


def _env(k):
    try:
        from tg import env
        return env(k)
    except Exception:
        return os.environ.get(k, '')


def _req(path, data=None, headers=None, timeout=60):
    h = {'Authorization': 'Apikey ' + _env('UPLOADPOST_API_KEY'), **(headers or {})}
    req = urllib.request.Request(BASE + path, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read() or b'{}')
        except Exception: body = {}
        return e.code, body


def find_user():
    """TikTok hesabı qoşulu olan profili tapır."""
    u = _env('UPLOADPOST_USER')
    if u: return u
    code, j = _req('/uploadposts/users')
    if code != 200: raise RuntimeError(f'profil siyahısı alınmadı ({code}): {j.get("message") or j}')
    profs = [p for p in j.get('profiles', []) if isinstance((p.get('social_accounts') or {}).get('tiktok'), dict)]
    if not profs: raise RuntimeError('TikTok qoşulu profil tapılmadı')
    if len(profs) > 1:
        sb = [p for p in profs if 'showband' in json.dumps(p, ensure_ascii=False).lower()]
        if len(sb) == 1: profs = sb
        else: raise RuntimeError('bir neçə TikTok profili var — UPLOADPOST_USER secret-ini yazın: ' +
                                 ', '.join(p['username'] for p in profs))
    return profs[0]['username']


def post(video, caption, key=None):
    if not _env('UPLOADPOST_API_KEY'): return {'ok': False, 'error': 'UPLOADPOST_API_KEY yoxdur'}
    try:
        user = find_user()
        fields = {'user': user, 'platform[]': 'tiktok', 'title': caption[:2200],
                  'tiktok_title': caption[:2200], 'privacy_level': 'PUBLIC_TO_EVERYONE'}
        b = uuid.uuid4().hex; body = b''
        for k, v in fields.items():
            body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        body += (f'--{b}\r\nContent-Disposition: form-data; name="video"; filename="{os.path.basename(video)}"\r\n'
                 'Content-Type: video/mp4\r\n\r\n').encode() + open(video, 'rb').read() + b'\r\n'
        body += f'--{b}--\r\n'.encode()
        hdr = {'Content-Type': f'multipart/form-data; boundary={b}'}
        if key: hdr['Idempotency-Key'] = 'showband-' + key   # təkrar göndərilsə dublikat olmasın
        code, j = _req('/upload', body, hdr, timeout=180)
        if code in (200, 201, 202) and j.get('success', True) is not False:
            tt = (j.get('results') or {}).get('tiktok') or {}
            if isinstance(tt, dict) and tt.get('success') is False:
                return {'ok': False, 'error': tt.get('error') or tt.get('message') or 'TikTok rədd etdi'}
            return {'ok': True, 'user': user, 'id': j.get('post_id') or tt.get('post_id') or j.get('request_id'),
                    'url': tt.get('url') if isinstance(tt, dict) else None, 'warnings': j.get('warnings') or []}
        return {'ok': False, 'error': f'{code}: ' + str(j.get('message') or j.get('error') or j)[:300]}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}


def check():
    """Heç nə paylaşmadan: hansı profillərə hansı TikTok qoşulub — Telegram-a yazır."""
    import html
    from tg import say
    code, j = _req('/uploadposts/users')
    if code != 200:
        return say(f'⚠️ <b>Upload-Post</b>: profil siyahısı alınmadı ({code}) — açar səhv ola bilər')
    lines = []
    for p in j.get('profiles', []):
        tt = (p.get('social_accounts') or {}).get('tiktok')
        acc = ('@' + str(tt.get('handle') or tt.get('display_name') or '?')) if isinstance(tt, dict) else '— TikTok qoşulmayıb'
        lines.append(f'• <code>{html.escape(p.get("username", ""))}</code> → {html.escape(acc)}')
    cur = _env('UPLOADPOST_USER')
    say('🔎 <b>Upload-Post profilləri</b>\n' + ('\n'.join(lines) or 'profil yoxdur') +
        (f'\n\nİndi seçilib: <code>{html.escape(cur)}</code> — avtomatik TikTok aktivdir ✅' if cur else
         '\n\nAvtomatik TikTok hələ <b>söndürülüb</b>. Düzgün profilin adını GitHub secret <code>UPLOADPOST_USER</code> kimi yazın.'))


if __name__ == '__main__':   # python3 news/tiktok.py check
    check()
