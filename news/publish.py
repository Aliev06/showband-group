#!/usr/bin/env python3
"""Təsdiqlənmiş qaralamanı paylaşır:
  1) news/posts.json-a əlavə edir və saytı yenidən qurur (build_news.py)
  2) Reels-i reels/<slug>.mp4 kimi sayta qoyur (Instagram videonu buradan götürür)
  3) IG_TOKEN və IG_USER_ID varsa — Instagram-a Reels kimi (yalnız Reels bölməsinə) göndərir
  python3 news/publish.py drafts/<slug>.json
Qeyd: GitHub Actions-da bu addımdan sonra dəyişikliklər commit olunur, Netlify saytı yeniləyir.
"""
import json, os, sys, time, shutil, subprocess, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from tg import env

KEEP = ['slug', 'title', 'description', 'category', 'date', 'tags', 'lead', 'body', 'reel', 'source', 'image']


def site_url(): return json.load(open(os.path.join(HERE, 'config.json'), encoding='utf-8'))['site_url'].rstrip('/')


def publish(path):
    d = json.load(open(path, encoding='utf-8'))
    if d.get('reels_only'):  # promo: saytda post yoxdur, yalnız Instagram Reels
        vid = os.path.join(HERE, 'out', d['slug'] + '.mp4')
        os.makedirs(os.path.join(ROOT, 'reels'), exist_ok=True)
        if os.path.exists(vid): shutil.copy(vid, os.path.join(ROOT, 'reels', d['slug'] + '.mp4'))
        d['status'] = 'published'; d['ig_status'] = 'queued' if env('IG_TOKEN') else 'no-token'
        json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        return {'site': '', 'ig': 'növbədə' if env('IG_TOKEN') else ''}
    posts = json.load(open(os.path.join(HERE, 'posts.json'), encoding='utf-8'))
    posts = [p for p in posts if not p.get('demo') and p['slug'] != d['slug']]  # demo məqalələr ilk real xəbərlə silinir
    post = {k: d[k] for k in KEEP if k in d}
    img = os.path.join(HERE, 'out', 'img', d['slug'] + '.jpg')
    if os.path.exists(img):  # saytda da şəkil (og:image üçün)
        os.makedirs(os.path.join(ROOT, 'img', 'news'), exist_ok=True)
        dst = os.path.join(ROOT, 'img', 'news', d['slug'] + '.jpg')
        try:  # saytda yüngül şəkil: max 1200px, JPEG q80
            from PIL import Image
            im = Image.open(img).convert('RGB')
            if im.width > 1200: im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
            im.save(dst, quality=80, optimize=True, progressive=True)
        except Exception:
            shutil.copy(img, dst)
        post['image'] = f'img/news/{d["slug"]}.jpg'
    posts.insert(0, post)
    json.dump(posts, open(os.path.join(HERE, 'posts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, 'build_news.py')], check=True)
    vid = os.path.join(HERE, 'out', d['slug'] + '.mp4')
    if os.path.exists(vid):
        os.makedirs(os.path.join(ROOT, 'reels'), exist_ok=True)
        shutil.copy(vid, os.path.join(ROOT, 'reels', d['slug'] + '.mp4'))
    # istifadə olunmuş mənbəni yadda saxla
    sp = os.path.join(HERE, 'seen.json')
    seen = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {'urls': [], 'titles': []}
    seen['urls'] = (seen['urls'] + [d['source']['url']])[-500:]
    import collect; seen['titles'] = (seen['titles'] + [collect.norm(d['title'])])[-500:]
    json.dump(seen, open(sp, 'w', encoding='utf-8'), ensure_ascii=False)
    d['status'] = 'published'; d['ig_status'] = 'queued' if env('IG_TOKEN') else 'no-token'
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return {'site': f'{site_url()}/xeberler/{d["slug"]}/', 'ig': 'növbədə (sayt yenilənəndən sonra)' if env('IG_TOKEN') else ''}


# ---------- Instagram ----------
GRAPH = 'https://graph.facebook.com/v21.0'  # Facebook Login for Business tokeni


def graph(path, params, method='POST'):
    params = dict(params, access_token=env('IG_TOKEN'))
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f'{GRAPH}/{path}' + ('' if method == 'POST' else '?' + data.decode()),
                                 data=data if method == 'POST' else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        if '"code":190' in body.replace(' ', ''):
            raise RuntimeError('Instagram tokeninin vaxtı bitib — yeni token yaradıb IG_TOKEN-i yeniləyin')
        raise RuntimeError(f'HTTP {e.code}: {body[:300]}')


def ig_publish(d, again=True):
    """Sayt yeniləndikdən sonra çağırılır (video URL artıq açıq olmalıdır)."""
    url = f'{site_url()}/reels/{d["slug"]}.mp4'
    for _ in range(20):  # GitHub Pages yeniləyənə qədər gözlə
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=20) as r:
                if r.status == 200: break
        except Exception: pass
        time.sleep(15)
    else:
        raise TimeoutError('video saytda hələ yoxdur')
    # video faylını birbaşa Meta-ya yükləyirik (resumable upload) — URL-dən yükləmə xətalarından qaçmaq üçün
    c = graph(f'{env("IG_USER_ID")}/media', {'media_type': 'REELS', 'upload_type': 'resumable', 'caption': d.get('ig_caption', ''),
                                             'share_to_feed': 'false',  # yalnız Reels bölməsi
                                             'thumb_offset': '3000'})  # örtük: 3-cü saniyə (kart tam görünür)
    fn = os.path.join(ROOT, 'reels', d['slug'] + '.mp4'); data = open(fn, 'rb').read()
    req = urllib.request.Request(c.get('uri') or f'https://rupload.facebook.com/ig-api-upload/v21.0/{c["id"]}', data=data, method='POST',
                                 headers={'Authorization': 'OAuth ' + env('IG_TOKEN'), 'offset': '0', 'file_size': str(len(data))})
    try:
        with urllib.request.urlopen(req, timeout=180) as r: print('  yükləndi:', r.read().decode()[:120])
    except urllib.error.HTTPError as e: raise RuntimeError('upload ' + e.read().decode()[:300])
    for _ in range(40):
        s = graph(c['id'], {'fields': 'status_code,status'}, 'GET')
        if s.get('status_code') == 'FINISHED': break
        if s.get('status_code') == 'ERROR':
            if again: time.sleep(60); return ig_publish(d, False)
            raise RuntimeError(s)
        time.sleep(10)
    r = graph(f'{env("IG_USER_ID")}/media_publish', {'creation_id': c['id']})
    return r['id']


def ig_queue():
    """Saytda paylaşılıb, Instagram-a hələ getməyən qaralamaları göndərir."""
    from tg import api
    dd = os.path.join(HERE, 'drafts')
    for f in sorted(os.listdir(dd)) if os.path.isdir(dd) else []:
        p = os.path.join(dd, f); d = json.load(open(p, encoding='utf-8'))
        if d.get('ig_status') != 'queued': continue
        try:
            d['ig_id'] = ig_publish(d); d['ig_status'] = 'done'; msg = f'📲 Instagram-da paylaşıldı: {d["title"]}'
        except TimeoutError:
            print('  sayt hələ yenilənməyib, növbəti saat yenidən:', d['slug']); continue
        except Exception as e:
            d['ig_tries'] = d.get('ig_tries', 0) + 1
            if d['ig_tries'] < 4 and '2207' in str(e):  # Meta tərəfdə müvəqqəti xəta — növbəti saat yenidən
                print('  Meta xətası, yenidən cəhd olunacaq:', e)
                json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); continue
            d['ig_status'] = 'error'; d['ig_error'] = str(e)[:300]; msg = f'⚠️ Instagram xətası: {d["title"]}\n{str(e)[:200]}'
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        try: api('sendMessage', {'chat_id': env('TELEGRAM_CHAT_ID'), 'text': msg})
        except Exception: pass


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--ig-check':  # tokenin növünü yoxlayır (tokeni çap etmir)
        for host, path, f in (('graph.facebook.com', env('IG_USER_ID'), 'username,media_count'), ('graph.facebook.com', 'me/accounts', 'name,instagram_business_account')):
            try:
                q = urllib.parse.urlencode({'fields': f, 'access_token': env('IG_TOKEN')})
                with urllib.request.urlopen(f'https://{host}/v21.0/{path}?{q}', timeout=30) as r: print('OK', host, r.read().decode()[:200])
            except urllib.error.HTTPError as e: print('XETA', host, e.read().decode()[:300])
    elif len(sys.argv) > 1 and sys.argv[1] == '--ig-queue': ig_queue()
    elif len(sys.argv) > 1: print(publish(sys.argv[1]))
    else: print(__doc__)
