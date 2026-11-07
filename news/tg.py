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
    if not data.get('callback_query_id'): return
    try: api('answerCallbackQuery', data)  # köhnə düymələrdə Telegram xəta verir — vacib deyil
    except Exception: pass


def caption(d, status=''):
    E = html.escape
    lab = {'hype': '🔥 Hype xəbər', 'event': '🎉 Tədbir xəbəri', 'article': '📝 Faydalı məqalə', 'promo': '⭐ Showband promo (yalnız Reels)'}.get(d.get('mode'), '🆕 Yeni xəbər')
    s = (f'<b>{lab}</b> — təsdiq gözləyir\n\n<b>{E(d["title"])}</b>\n{E(d["lead"])}\n\n'
         f'🔥 Viral: {d.get("viral", "?")}/10 · 🏷 {E(d["category"])}\n'
         f'📰 Mənbə: <a href="{E(d["source"]["url"])}">{E(d["source"]["name"])}</a>\n\n'
         f'<b>Instagram mətni:</b>\n{E(d.get("ig_caption", ""))}')
    if status: s += f'\n\n{status}'
    return s[:1024]


def kb(slug):
    h = sid(slug)  # Telegram callback_data maksimum 64 bayt — qısa id istifadə olunur
    return json.dumps({'inline_keyboard': [
        [{'text': '✅ Paylaş', 'callback_data': f'ok:{h}'}, {'text': '❌ Ləğv et', 'callback_data': f'no:{h}'}],
        [{'text': '✍️ Yenidən yaz', 'callback_data': f'rw:{h}'}, {'text': '✏️ Başlığı dəyiş', 'callback_data': f'tt:{h}'}],
        [{'text': '🖼 Şəkilsiz', 'callback_data': f'ph:{h}'}, {'text': '🔄 Başqa xəbər', 'callback_data': f'nx:{h}'}]]})


def sid(slug):
    import hashlib; return hashlib.sha1(slug.encode()).hexdigest()[:12]


def find_draft(key):
    dd = os.path.join(HERE, 'drafts')
    for f in os.listdir(dd) if os.path.isdir(dd) else []:
        if f.endswith('.json') and (f[:-5] == key or sid(f[:-5]) == key): return os.path.join(dd, f)
    return None


def send(path):
    d = json.load(open(path, encoding='utf-8'))
    video = os.path.join(HERE, 'out', d['slug'] + '.mp4')
    mk = kb(d['slug']) if not d.get('reels_only') else json.dumps({'inline_keyboard': [
        [{'text': '✅ Paylaş', 'callback_data': f'ok:{sid(d["slug"])}'}, {'text': '❌ Ləğv et', 'callback_data': f'no:{sid(d["slug"])}'}],
        [{'text': '🔄 Başqa variant', 'callback_data': f'nx:{sid(d["slug"])}'}]]})
    data = {'chat_id': env('TELEGRAM_CHAT_ID'), 'caption': caption(d), 'parse_mode': 'HTML', 'reply_markup': mk,
            'supports_streaming': 'true'}
    m = api('sendVideo', data, {'video': video}) if os.path.exists(video) else api('sendMessage', {
        'chat_id': data['chat_id'], 'text': data['caption'], 'parse_mode': 'HTML', 'reply_markup': json.loads(data['reply_markup'])})
    d['tg_message'] = m['message_id']; d['status'] = 'pending'
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('göndərildi:', d['slug'])


def save(path, d): json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


TT_CTA = {'hype': '📲 Ətraflı — showbandgroup.az',
          'event': '🎉 Tədbirinizi biz təşkil edək — showbandgroup.az'}


def tiktok_caption(d):
    """Instagram mətnindən TikTok üçün qısa mətn: mətn + çağırış + heşteqlər."""
    import re, write
    cap = d.get('ig_caption', '').split('\n\n🎵')[0]
    for c in write.CTA.values(): cap = cap.replace('\n\n' + c, '').replace(c, '')
    m = re.search(r'(\s*#\S+)+\s*$', cap)
    txt, tags = (cap[:m.start()], cap[m.start():].split()) if m else (cap, [])
    for t in ('#baku', '#azerbaijan', '#fyp'):
        if t.lower() not in [x.lower() for x in tags]: tags.append(t)
    cta = TT_CTA['hype' if d.get('mode', 'hype') == 'hype' else 'event']
    return (txt.strip() + '\n\n' + cta + '\n\n' + ' '.join(tags[:8])).strip()


def send_tiktok(d):
    """Paylaşdıqdan sonra TikTok üçün video + hazır mətn göndərir (əl ilə paylaşmaq üçün)."""
    video = os.path.join(HERE, 'out', d['slug'] + '.mp4')
    if not os.path.exists(video): return
    txt = tiktok_caption(d)
    cap = '📱 <b>TikTok üçün</b> — videonu yadda saxlayın, mətnə toxunub kopyalayın:\n\n<code>' + html.escape(txt) + '</code>'
    if len(cap) > 1000: cap = '📱 <b>TikTok üçün</b> — videonu yadda saxlayın, mətn aşağıda 👇'
    try:
        api('sendVideo', {'chat_id': env('TELEGRAM_CHAT_ID'), 'caption': cap, 'parse_mode': 'HTML', 'supports_streaming': 'true'},
            {'video': video})
        if not cap.endswith('</code>'):
            api('sendMessage', {'chat_id': env('TELEGRAM_CHAT_ID'), 'text': '<code>' + html.escape(txt) + '</code>', 'parse_mode': 'HTML'})
    except Exception as e: print('  ! tiktok:', e)


def say(text):
    try: return api('sendMessage', {'chat_id': env('TELEGRAM_CHAT_ID'), 'text': text, 'parse_mode': 'HTML'})
    except Exception as e: print('  ! say:', e)


def drop(chat, mid):
    try: api('deleteMessage', {'chat_id': chat, 'message_id': mid})
    except Exception as e: print('  ! delete:', e)


def resend(path, old):
    """Reels-i yenidən hazırlayır, köhnə mesajı silir və yenisini göndərir."""
    prepare(path)
    if old: drop(env('TELEGRAM_CHAT_ID'), old)
    send(path)


def on_reply(e):
    """✏️ Başlığı dəyiş → istifadəçi bota cavab olaraq yeni başlıq yazır."""
    dd = os.path.join(HERE, 'drafts')
    for f in os.listdir(dd) if os.path.isdir(dd) else []:
        p = os.path.join(dd, f)
        if not f.endswith('.json'): continue
        d = json.load(open(p, encoding='utf-8'))
        if d.get('title_prompt') == e['reply_to'] and d.get('status') == 'pending':
            new = ' '.join(e['text'].split())[:110]
            if len(new) < 10: say('⚠️ Başlıq çox qısadır — yenidən yazın.'); return
            d['title'] = new; prompt = d.pop('title_prompt'); save(p, d)
            drop(env('TELEGRAM_CHAT_ID'), prompt)
            resend(p, d.get('tg_message'))
            return


def del_kb(slug):
    return {'inline_keyboard': [[{'text': '🗑 Saytdan sil', 'callback_data': f'dl:{sid(slug)}'}]]}


def find_post(key):
    for p in json.load(open(os.path.join(HERE, 'posts.json'), encoding='utf-8')):
        if p['slug'] == key or sid(p['slug']) == key: return p
    return None


def unpublish(slug):
    """Xəbəri saytdan silir: posts.json, səhifə, şəkil, video; sonra saytı yenidən qurur."""
    import shutil, subprocess
    ROOT = os.path.dirname(HERE)
    pp = os.path.join(HERE, 'posts.json'); posts = json.load(open(pp, encoding='utf-8'))
    posts = [p for p in posts if p['slug'] != slug]
    json.dump(posts, open(pp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for f in (os.path.join(ROOT, 'img', 'news', slug + '.jpg'), os.path.join(ROOT, 'reels', slug + '.mp4')):
        if os.path.exists(f): os.remove(f)
    shutil.rmtree(os.path.join(ROOT, 'xeberler', slug), ignore_errors=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'build_news.py')], check=True)
    dp = os.path.join(HERE, 'drafts', slug + '.json')
    if os.path.exists(dp):
        d = json.load(open(dp, encoding='utf-8')); d['status'] = 'deleted'; save(dp, d)


def get_news(mode='hype'):
    """📰 Yeni xəbər al — dərhal yeni xəbər hazırlayır və göndərir."""
    import write, collect
    try: collect.main()
    except Exception as x: print('  ! collect:', x)
    try: write.main(1, mode)
    except SystemExit as x: say(f'⚠️ Hazırda uyğun yeni xəbər tapılmadı ({x}). Bir az sonra yenidən yoxlayın.'); return
    except RuntimeError as x: say('⚠️ AI modelləri (Gemini, Groq, OpenRouter) hazırda cavab vermir. 10-15 dəqiqə sonra «📰» düyməsini basın.'); print(x); return
    send_new()


def get_promo():
    """⭐ Showband promo Reels hazırlayır və təsdiqə göndərir."""
    import promo
    try: promo.make_draft()
    except Exception as x: say(f'⚠️ Promo Reels hazırlanmadı: {x}'); print(x); return
    send_new()


def list_news():
    posts = json.load(open(os.path.join(HERE, 'posts.json'), encoding='utf-8'))[:10]
    if not posts: say('Saytda hələ xəbər yoxdur.'); return
    rows = [[{'text': '🗑 ' + (p['title'][:55] + ('…' if len(p['title']) > 55 else '')), 'callback_data': f'dl:{sid(p["slug"])}'}] for p in posts]
    api('sendMessage', {'chat_id': env('TELEGRAM_CHAT_ID'), 'text': '📰 <b>Saytdakı son xəbərlər</b>\nSilmək üçün xəbərə basın:',
                        'parse_mode': 'HTML', 'reply_markup': {'inline_keyboard': rows}})


def delete_flow(act, key, chat):
    p = find_post(key)
    if act == 'dl':
        if not p: say('Bu xəbər saytda artıq yoxdur.'); return
        api('sendMessage', {'chat_id': chat, 'parse_mode': 'HTML',
                            'text': f'🗑 <b>{html.escape(p["title"])}</b>\n\nSaytdan silinsin?',
                            'reply_markup': {'inline_keyboard': [[{'text': '✅ Bəli, sil', 'callback_data': f'dy:{key}'},
                                                                  {'text': '✖️ Xeyr', 'callback_data': f'dn:{key}'}]]}})
    elif act == 'dy':
        if not p: say('Bu xəbər saytda artıq yoxdur.'); return
        unpublish(p['slug'])
        say(f'🗑 <b>Saytdan silindi:</b> {html.escape(p["title"])}\n\n⚠️ Instagram-dakı Reels varsa, onu tətbiqdə əl ilə silin.')


def poll():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {'offset': 0}
    ev = os.environ.get('TG_EVENT')  # Cloudflare Worker-dən gələn hadisə (webhook rejimi)
    if not ev: print('TG_EVENT yoxdur'); return
    e = json.loads(ev)
    if e.get('kind') == 'reply': on_reply(e); return
    if str(e['chat_id']) != str(env('TELEGRAM_CHAT_ID')): return
    if e.get('kind') == 'cmd' and e.get('cmd') in ('yeni', 'tedbir'):
        import datetime as _dt
        now = _dt.datetime.now(_dt.timezone.utc)
        if e['cmd'] == 'yeni' and now.hour == 6 and now.minute < 30: get_promo(); return   # 10:00 Bakı — hər gün Showband promo
        if e['cmd'] == 'tedbir' and now.hour == 13 and now.minute < 30:                       # 17:00 Bakı — növbə ilə hype / tədbir
            get_news('hype' if now.timetuple().tm_yday % 2 else 'event'); return
        get_news('event' if e['cmd'] == 'tedbir' else 'hype'); return
    if (e.get('data') or '').startswith('gt:'):
        get_news('event' if e['data'] == 'gt:e' else 'hype'); return
    if e.get('kind') == 'cmd': list_news(); return
    act, key = e['data'].split(':', 1)
    if act in ('dl', 'dy', 'dn'):
        if act != 'dl': drop(e['chat_id'], e['message_id'])  # təsdiq mesajını sil
        delete_flow(act, key, e['chat_id']); return
    path = find_draft(key)
    if not path: say('⚠️ Qaralama tapılmadı'); return
    d = json.load(open(path, encoding='utf-8'))
    if d.get('status') in ('published', 'rejected'): return
    chat, mid, is_video = e['chat_id'], e['message_id'], e.get('video')

    def mark(status, markup=None):
        method = 'editMessageCaption' if is_video else 'editMessageText'
        body = {'chat_id': chat, 'message_id': mid, ('caption' if is_video else 'text'): caption(d, status), 'parse_mode': 'HTML'}
        if markup: body['reply_markup'] = markup
        try: api(method, body)
        except Exception as x: print('  ! edit:', x)

    if d.get('reels_only') and act in ('rw', 'nx', 'ph'):  # promo: başqa variant
        d['status'] = 'rejected'; save(path, d); mark('🔄 <b>Başqa promo hazırlanır…</b>'); get_promo()
        json.dump(st, open(STATE, 'w')); return
    if act == 'ok':
        import publish
        res = publish.publish(path); d = json.load(open(path, encoding='utf-8'))
        mark('✅ <b>Saytda paylaşıldı</b>' + (' · Instagram: ' + res['ig'] if res.get('ig') else ''), del_kb(d['slug']))
        send_tiktok(d)
    elif act == 'no':
        d['status'] = 'rejected'; save(path, d); mark('❌ <b>Ləğv edildi</b>')
    elif act == 'ph':  # şəkilsiz
        d['no_photo'] = True; save(path, d); resend(path, mid)
    elif act == 'rw':  # mətni yenidən yaz
        import write, collect
        text, _ = collect.article_text(d['source']['url'])
        it = {'source': d['source']['name'], 'url': d['source']['url'], 'title': d.get('source_title', d['title'])}
        j = write.rewrite(it, text or d['lead'])
        for k in ('title', 'description', 'category', 'lead', 'body', 'reel', 'ig_caption'):
            if j.get(k): d[k] = j[k]
        d['ig_caption'] = write.add_cta(d.get('ig_caption', ''), d.get('mode', 'hype'))
        d['tags'] = j.get('tags', d['tags'])[:6]; save(path, d); resend(path, mid)
    elif act == 'tt':  # başlığı özün yaz
        m = api('sendMessage', {'chat_id': chat, 'reply_to_message_id': mid,
                                'text': '✏️ Yeni başlığı <b>bu mesaja cavab (reply)</b> olaraq yazın:', 'parse_mode': 'HTML',
                                'reply_markup': {'force_reply': True, 'input_field_placeholder': 'Yeni başlıq…'}})
        d['title_prompt'] = m['message_id']; save(path, d)
    elif act == 'nx':  # başqa xəbər
        d['status'] = 'rejected'; save(path, d); mark('🔄 <b>Başqa xəbər axtarılır…</b>')
        import write
        try: write.main(1, 'event' if d.get('mode') in ('event', 'article') else 'hype')
        except SystemExit as x: say(f'⚠️ Başqa uyğun xəbər tapılmadı ({x})'); return
        send_new()
    json.dump(st, open(STATE, 'w'))


def prepare(p):
    """Reels-i hazırlayır və Instagram mətninə mahnının adını əlavə edir."""
    import subprocess
    subprocess.run([sys.executable, os.path.join(HERE, 'reels.py'), p], check=True)
    f = os.path.basename(p)
    meta = os.path.join(HERE, 'out', f[:-5] + '.json'); tp = os.path.join(HERE, 'music', 'titles.json')
    if os.path.exists(meta) and os.path.exists(tp):
        tr = json.load(open(meta, encoding='utf-8')).get('track'); title = json.load(open(tp, encoding='utf-8')).get(tr or '')
        if title:
            d = json.load(open(p, encoding='utf-8')); d['ig_caption'] = d.get('ig_caption', '').split('\n\n🎵')[0] + f'\n\n🎵 {title}'; d['track'] = title
            save(p, d)


def send_new():
    """Hələ göndərilməmiş qaralamalar üçün Reels hazırlayır və Telegram-a göndərir."""
    dd = os.path.join(HERE, 'drafts')
    for f in sorted(os.listdir(dd)) if os.path.isdir(dd) else []:
        p = os.path.join(dd, f)
        if not f.endswith('.json'): continue
        d = json.load(open(p, encoding='utf-8'))
        if d.get('status'): continue
        if not d.get('reels_only'): prepare(p)  # promo videosu artıq hazırdır
        send(p)


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    if len(sys.argv) > 1 and sys.argv[1] == 'send-new': send_new()
    elif len(sys.argv) > 2 and sys.argv[1] == 'send': send(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == 'poll': poll()
    else: print(__doc__)
