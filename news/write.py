#!/usr/bin/env python3
"""Showband Group — hovuzdan (pool.json) ən yaxşı musiqi xəbərini seçir və Gemini ilə yenidən yazır.
  python3 news/write.py            # 1 qaralama: news/drafts/<slug>.json + Reels
  python3 news/write.py --n 2      # 2 qaralama
Açar: GEMINI_API_KEY (mühit dəyişəni və ya news/.env)
Qaralama Telegram təsdiqindən sonra publish.py ilə sayta və Instagram-a gedir.
"""
import json, os, re, sys, time, urllib.request, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import collect

MODELS = ['gemini-flash-lite-latest', 'gemini-3.5-flash-lite', 'gemini-flash-latest']
CATS = ['Şou-biznes', 'Yeni mahnı', 'Klip', 'Konsert', 'Albom', 'Festival', 'Avroviziya']


def key():
    k = (os.environ.get('GEMINI_API_KEY') or '').strip()
    if not k and os.path.exists(os.path.join(HERE, '.env')):
        for l in open(os.path.join(HERE, '.env')):
            if l.startswith('GEMINI_API_KEY='): k = l.split('=', 1)[1].strip()
    if not k: sys.exit('GEMINI_API_KEY yoxdur')
    return k


def gemini(prompt, temp=0.4):
    body = json.dumps({'contents': [{'parts': [{'text': prompt}]}],
                       'generationConfig': {'responseMimeType': 'application/json', 'temperature': temp}}).encode()
    last = ''
    for attempt in range(2):
        for m in MODELS:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', data=body,
                                         headers={'x-goog-api-key': key(), 'content-type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    j = json.load(r)
                return json.loads(j['candidates'][0]['content']['parts'][0]['text'])
            except Exception as e:
                last = f'{m}: {e}'; print('  ! Gemini', last)
        time.sleep(20)
    raise RuntimeError('Gemini cavab vermədi: ' + last)


RULES = """Uyğun: MÜĞƏNNİLƏR, MUSİQİÇİLƏR, REPERLƏR, DJ-lər, musiqi qrupları, bəstəkarlar və musiqi hadisələri
(mahnı, klip, konsert, albom, festival, Avroviziya, mükafat). Qalmaqal, ayrılıq, mübahisə, açıqlama — olar, baxış gətirir.
Aktyor, film, serial, model, idmançı — UYĞUN DEYİL.
QADAĞAN: zorakılıq və cinayət təfərrüatı, cinsi zorakılıq, uşaqlarla bağlı xəbər, ölüm/xəstəlik spekulyasiyası, siyasət."""


def pick(pool, n):
    pool = sorted(pool, key=lambda x: x.get('score', 0), reverse=True)[:40]
    res = gemini('Sən "Showband Group" musiqi xəbərləri saytının redaktorusan. Başlıqları qiymətləndir.\n' + RULES +
                 '\nHər biri üçün: {"i":indeks,"music":bool,"allowed":bool,"viral":1-10}. Yalnız JSON massiv.\nBaşlıqlar:\n' +
                 '\n'.join(f'{i}. {x["title"]}' for i, x in enumerate(pool)), temp=0.2)
    ok = [r for r in res if r.get('music') and r.get('allowed') and 0 <= r.get('i', -1) < len(pool)]
    ok.sort(key=lambda r: r.get('viral', 0), reverse=True)
    return [pool[r['i']] | {'viral': r['viral']} for r in ok[:n]]


def slugify(s):
    s = s.lower()
    for a, b in zip('əıöüçşğ', 'eioucsg'): s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    s = '-'.join(s.split('-')[:9])
    return s[:60].rstrip('-')


def _rewrite(it, text, fix=''):
    j = gemini(f'''Sən "Showband Group" saytının musiqi xəbərləri redaktorusan. Mənbə mətnindən Azərbaycan dilində TAM YENİ, unikal xəbər yaz
(kopyalama, öz sözlərinlə). Faktları dəyişmə, heç nə uydurma. İddiaları "bildirilir", "iddia olunur" kimi ver; ittiham etmə, təhqir etmə.
Ton: canlı, maraqlı, peşəkar. Yalnız Azərbaycan dilində yaz — heç bir ingilis və ya rus sözü işlətmə (məs. "surprising" yox, "təəccüblü"). 180-320 söz, 2-3 ara başlıq.
SEO: title 50-70 simvol, artistin adı əvvəldə, tam cümlə — sonunda üç nöqtə (...) OLMASIN; description 140-160 simvol.
Kateqoriya bunlardan biri: {", ".join(CATS)}.
Yalnız JSON:
{{"title":"","description":"","category":"","tags":["4-6 açar söz"],"lead":"1-2 cümlə",
"body":[{{"h":"ara başlıq"}},{{"p":"abzas"}},{{"p":"abzas"}},{{"h":"ara başlıq"}},{{"p":"abzas"}}],
"reel":{{"caption":"kartın altında qısa, maraqlı 1-2 cümlə, max 110 simvol"}},
"ig_caption":"Instagram üçün 2-3 cümlə + 5 heşteq (#ShowbandGroup daxil)"}}
MƏNBƏ ({it["source"]}): {it["title"]}\n{text}''' + fix, temp=0.5)
    # body-ni normallaşdır: {"h","p"} birlikdə gələrsə ayır
    body = []
    for b in j.get('body', []):
        if b.get('h'): body.append({'h': b['h'].strip()})
        if b.get('p'): body.append({'p': b['p'].strip()})
    j['body'] = body
    if j.get('category') not in CATS: j['category'] = 'Şou-biznes'
    return j


# ---------- avtomatik yoxlama ----------
EN = set('''the and of to in is for with on at by new song songs music video official surprising amazing shocking fans fan singer
star best love life news from about after his her their this that it was are be has have will more about breaking exclusive
finally wow just really very first last people world big great famous viral trend trending update announced reveals revealed
shares shared says said'''.split())


def check(j, src):
    import re
    out = []
    parts = [j.get('title', ''), j.get('description', ''), j.get('lead', ''), (j.get('reel') or {}).get('caption', ''),
             j.get('ig_caption', '')] + [b.get('h', '') or b.get('p', '') for b in j.get('body', [])]
    allt = ' '.join(parts)
    if re.search('[а-яА-ЯёЁ]', allt): out.append('mətndə kiril (rus) hərfləri var')
    bad = sorted({w for w in re.findall(r"(?<![#@\w])[a-zəğıöüçş]+", allt) if w in EN or ('w' in w and len(w) > 2)})
    if bad: out.append('ingilis sözləri var: ' + ', '.join(bad[:8]) + ' — Azərbaycan dilində yaz')
    t = j.get('title', '')
    if not 35 <= len(t) <= 80: out.append(f'title {len(t)} simvoldur, 50-70 olmalıdır')
    if t.rstrip().endswith(('...', '…')): out.append('title üç nöqtə ilə bitməməlidir')
    if len((j.get('reel') or {}).get('caption', '')) > 120: out.append('reel.caption 110 simvoldan uzundur')
    if not 90 <= len(j.get('description', '')) <= 200: out.append('description 140-160 simvol olmalıdır')
    words = len(' '.join(b.get('p', '') for b in j.get('body', [])).split())
    if words < 100: out.append(f'mətn {words} sözdür, ən azı 150 olmalıdır (mənbədəki faktlar əsasında, uydurmadan)')
    names = [w for w in re.findall(r'[A-ZƏĞIİÖÜÇŞ][\wəğıöüçş]{3,}', t)]
    low = src.lower().replace('i̇', 'i')
    if names and not any(n.lower().replace('i̇', 'i')[:5] in low for n in names):
        out.append('başlıqdakı adlar mənbədə yoxdur — faktları mənbədən götür')
    return out


def rewrite(it, text):
    """Yazır, yoxlayır, problem varsa 2 dəfəyə qədər yenidən yazdırır."""
    best, fix = None, ''
    for attempt in range(3):
        j = _rewrite(it, text, fix)
        probs = check(j, it.get('title', '') + ' ' + text)
        print(f'  yoxlama #{attempt + 1}:', 'OK' if not probs else '; '.join(probs))
        if best is None or len(probs) < best[1]: best = (j, len(probs))
        if not probs: break
        fix = '\n\nƏVVƏLKİ CAVABDA PROBLEMLƏR VAR İDİ, DÜZƏLT:\n- ' + '\n- '.join(probs)
    return best[0]


def main(n=None):
    if n is None: n = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 1
    pool_p = os.path.join(HERE, 'pool.json')
    pool = json.load(open(pool_p, encoding='utf-8')) if os.path.exists(pool_p) else []
    pool = [x for x in pool if not x.get('used')]
    if not pool: sys.exit('Hovuz boşdur — əvvəlcə collect.py')
    chosen = pick(pool, n)
    if not chosen: sys.exit('Uyğun musiqi xəbəri tapılmadı')
    posts = json.load(open(os.path.join(HERE, 'posts.json'), encoding='utf-8'))
    have = {p['slug'] for p in posts}
    os.makedirs(os.path.join(HERE, 'drafts'), exist_ok=True)
    for it in chosen:
        text, og = collect.article_text(it['url'])
        if len(text) < 200: text = it.get('summary', '') + '\n' + text
        j = rewrite(it, text)
        slug = slugify(j.get('title', it['title']))
        while slug in have: slug += '-2'
        draft = {'slug': slug, 'title': j['title'], 'description': j['description'], 'category': j['category'],
                 'date': dt.date.today().isoformat(), 'tags': j.get('tags', [])[:6], 'lead': j['lead'], 'body': j['body'],
                 'reel': j.get('reel', {}), 'ig_caption': j.get('ig_caption', ''),
                 'source': {'name': it['source'], 'url': it['url']}, 'source_image': og or it.get('image', ''),
                 'viral': it.get('viral'), 'source_title': it['title']}
        json.dump(draft, open(os.path.join(HERE, 'drafts', slug + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        full = json.load(open(pool_p, encoding='utf-8'))
        for x in full:
            if x['url'] == it['url']: x['used'] = True
        json.dump(full, open(pool_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'qaralama: drafts/{slug}.json  [{it["viral"]}/10]  {j["title"]}')


if __name__ == '__main__':
    main()
