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
CATS = ['Şou-biznes', 'Yeni mahnı', 'Klip', 'Konsert', 'Albom', 'Festival', 'Avroviziya', 'Toy və nişan', 'Ad günü', 'Korporativ', 'Son zəng', 'Açılış', 'Party', 'Məsləhət']


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
    for attempt in range(6):  # Google pulsuz planda tez-tez 503 (yüklənmə) verir — gözləyib yenidən
        for m in MODELS:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent', data=body,
                                         headers={'x-goog-api-key': key(), 'content-type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    j = json.load(r)
                return json.loads(j['candidates'][0]['content']['parts'][0]['text'])
            except Exception as e:
                last = f'{m}: {e}'; print('  ! Gemini', last)
        time.sleep([20, 40, 60, 90, 120, 0][attempt])
    raise RuntimeError('Gemini cavab vermədi: ' + last)


RULES = """Uyğun: MÜĞƏNNİLƏR, MUSİQİÇİLƏR, REPERLƏR, DJ-lər, musiqi qrupları, bəstəkarlar və musiqi hadisələri
(mahnı, klip, konsert, albom, festival, Avroviziya, mükafat). Qalmaqal, ayrılıq, mübahisə, açıqlama — olar, baxış gətirir.
Aktyor, film, serial, model, idmançı — UYĞUN DEYİL.
QADAĞAN: zorakılıq və cinayət təfərrüatı, cinsi zorakılıq, uşaqlarla bağlı xəbər, ölüm/xəstəlik spekulyasiyası, siyasət."""


RULES_EVENT = """Showband Group tədbir təşkilatçısıdır (toy, nişan, ad günü, korporativ, son zəng/məzun, açılış, party, şou proqramı).
Uyğun: bu tədbirlərlə bağlı xəbərlər — məşhurların toyu, nişanı, ad günü, ziyafəti; Bakıda/Azərbaycanda konsertlər, festivallar,
şou proqramları, yeni il və bayram tədbirləri; yeni restoran, şadlıq sarayı, məkan açılışları; toy və tədbir trendləri, dekor,
viktorina/intellektual oyun gecələri, korporativ tədbirlər, məzun gecələri.
UYĞUN DEYİL: ümumi qalmaqal, ayrılıq, məhkəmə, siyasət, idman, Avroviziya, xəstəlik, ölüm, cinayət."""


def pick(pool, n, mode='hype'):
    pool = sorted(pool, key=lambda x: x.get('score', 0), reverse=True)[:50]
    rules = RULES if mode == 'hype' else RULES_EVENT
    res = gemini('Sən "Showband Group" saytının redaktorusan. Başlıqları qiymətləndir.\n' + rules +
                 '\nHər biri üçün: {"i":indeks,"music":bool,"allowed":bool,"viral":1-10}. Yalnız JSON massiv.\nBaşlıqlar:\n' +
                 '\n'.join(f'{i}. {x["title"]}' for i, x in enumerate(pool)), temp=0.2)
    ok = [r for r in res if r.get('music') and r.get('allowed') and 0 <= r.get('i', -1) < len(pool)]
    if mode != 'hype': ok = [r for r in ok if r.get('viral', 0) >= 4]
    ok.sort(key=lambda r: r.get('viral', 0), reverse=True)
    return [pool[r['i']] | {'viral': r['viral']} for r in ok[:n]]


def slugify(s):
    s = s.lower()
    for a, b in zip('əıöüçşğ', 'eioucsg'): s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    s = '-'.join(s.split('-')[:9])
    return s[:60].rstrip('-')


CTA = {'hype': '📲 Ətraflı — showbandgroup.az',
       'event': '🎉 Toy, nişan, ad günü və korporativ tədbirləri biz təşkil edirik — Direct-ə yazın 📩'}


def add_cta(cap, mode):
    """Instagram mətninə sonda çağırış əlavə edir (heşteqlərdən əvvəl)."""
    cta = CTA['hype' if mode == 'hype' else 'event']
    cap = cap.split('\n\n🎵')[0]
    for c in CTA.values(): cap = cap.replace('\n\n' + c, '').replace(c, '')
    m = re.search(r'(\s*#\S+)+\s*$', cap)
    txt, tags = (cap[:m.start()], cap[m.start():].strip()) if m else (cap, '')
    return txt.rstrip() + '\n\n' + cta + ('\n\n' + tags if tags else '')


def save_draft(it, j, og, mode):
    import random
    posts = json.load(open(os.path.join(HERE, 'posts.json'), encoding='utf-8'))
    have = {p['slug'] for p in posts}
    slug = slugify(j.get('title', it['title']))
    while slug in have or os.path.exists(os.path.join(HERE, 'drafts', slug + '.json')): slug += '-2'
    draft = {'slug': slug, 'title': j['title'], 'description': j['description'], 'category': j['category'],
             'date': dt.date.today().isoformat(), 'tags': j.get('tags', [])[:6], 'lead': j['lead'], 'body': j['body'],
             'reel': j.get('reel', {}), 'ig_caption': add_cta(j.get('ig_caption', ''), mode),
             'source': {'name': it['source'], 'url': it['url']}, 'source_image': og or it.get('image', ''),
             'viral': it.get('viral'), 'source_title': it['title'], 'mode': mode}
    if mode == 'article':  # öz tədbir şəkillərimiz
        draft['image'] = random.choice(['img/pk_toy.jpg', 'img/pk_korp.jpg', 'img/pk_mezun.jpg', 'video/ev_toy.jpg', 'video/ev_mezun.jpg'])
        draft.pop('source', None); draft['source'] = {'name': 'Showband Group', 'url': 'https://showbandgroup.az/'}
    os.makedirs(os.path.join(HERE, 'drafts'), exist_ok=True)
    json.dump(draft, open(os.path.join(HERE, 'drafts', slug + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'qaralama ({mode}): drafts/{slug}.json  [{it.get("viral")}/10]  {j["title"]}')


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
    if j.get('_article'): return out
    names = [w for w in re.findall(r'[A-ZƏĞIİÖÜÇŞ][\wəğıöüçş]{3,}', t)]
    low = src.lower().replace('i̇', 'i')
    if names and not any(n.lower().replace('i̇', 'i')[:5] in low for n in names):
        out.append('başlıqdakı adlar mənbədə yoxdur — faktları mənbədən götür')
    return out


def rewrite(it, text, article=False):
    """Yazır, yoxlayır, problem varsa 2 dəfəyə qədər yenidən yazdırır."""
    best, fix = None, ''
    for attempt in range(3):
        j = _rewrite(it, text, fix)
        if article: j['_article'] = True
        probs = check(j, it.get('title', '') + ' ' + text)
        print(f'  yoxlama #{attempt + 1}:', 'OK' if not probs else '; '.join(probs))
        if best is None or len(probs) < best[1]: best = (j, len(probs))
        if not probs: break
        fix = '\n\nƏVVƏLKİ CAVABDA PROBLEMLƏR VAR İDİ, DÜZƏLT:\n- ' + '\n- '.join(probs)
    best[0].pop('_article', None)
    return best[0]


TOPICS = ['Toy üçün ilk rəqs mahnısı necə seçilir', 'Toyda gəlin-bəy girişi üçün 7 ideya', 'Ad günü üçün şou proqram ideyaları',
 'Uşaq ad günü: animator, DJ və oyunlar', 'Korporativ tədbir necə təşkil olunur: addım-addım', 'Korporativ gecə üçün 10 əyləncə ideyası',
 'Son zəng və məzun gecəsi: unudulmaz gecə üçün ideyalar', 'Nişan mərasimi: musiqi və dekor seçimi', 'Canlı band, yoxsa DJ: nə seçməli',
 'Toyda işıq və səs: nəyə diqqət etməli', 'Restoran və ya şadlıq sarayı açılışı necə təşkil olunur', 'Yeni il korporativi üçün ideyalar',
 'Toyda milli musiqi: saz, nağara, balaban', 'Party üçün lazer və işıq şousu', 'Tədbir üçün aparıcı (showman) necə seçilir',
 'Viktorina gecəsi necə təşkil olunur', 'Toy büdcəsi: musiqi və şou üçün nə qədər ayırmalı', 'Ad günü sürprizləri: 10 ideya']


def write_article():
    """Uyğun tədbir xəbəri olmayanda — xidmətlərlə bağlı faydalı məqalə."""
    sp = os.path.join(HERE, 'articles_state.json')
    used = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else []
    free = [t for t in TOPICS if t not in used] or TOPICS
    topic = free[0]
    it = {'source': 'Showband Group', 'url': 'https://showbandgroup.az/', 'title': topic}
    text = ('Bu, xəbər deyil — Showband Group-un mütəxəssis məsləhət məqaləsidir. Mövzu: ' + topic +
            '. Praktik, faydalı məsləhətlər ver, Bakıdakı tədbirlər kontekstində. Sonda Showband Group-un bu işdə kömək edə biləcəyini qısa qeyd et. Kateqoriya: Məsləhət.')
    j = rewrite(it, text, article=True); j['category'] = 'Məsləhət'
    json.dump((used + [topic])[-len(TOPICS):], open(sp, 'w', encoding='utf-8'), ensure_ascii=False)
    return it, j


def main(n=None, mode=None):
    if n is None: n = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 1
    if mode is None: mode = sys.argv[sys.argv.index('--mode') + 1] if '--mode' in sys.argv else (
        'hype' if dt.datetime.now(dt.timezone.utc).hour < 10 else 'event')
    print('rejim:', mode)
    pool_p = os.path.join(HERE, 'pool.json')
    pool = json.load(open(pool_p, encoding='utf-8')) if os.path.exists(pool_p) else []
    pool = [x for x in pool if not x.get('used')]
    # artıq qaralaması olan (göndərilmiş, ləğv edilmiş, gözləyən) xəbərləri təkrar götürmə
    dd = os.path.join(HERE, 'drafts'); urls, sigs = set(), []
    for f in os.listdir(dd) if os.path.isdir(dd) else []:
        try: d = json.load(open(os.path.join(dd, f), encoding='utf-8'))
        except Exception: continue
        urls.add((d.get('source') or {}).get('url', ''))
        sigs.append(set(collect.norm(d.get('source_title') or d.get('title', ''))))
    def dup(x):
        w = set(collect.norm(x['title']))
        return x['url'] in urls or any(w and len(w & s) / max(1, len(w | s)) > .45 for s in sigs)
    pool = [x for x in pool if not dup(x)]
    chosen = pick(pool, n, mode) if pool else []
    if not chosen and mode == 'event':
        it, j = write_article(); save_draft(it, j, '', 'article'); return
    if not chosen: sys.exit('Uyğun xəbər tapılmadı')
    posts = json.load(open(os.path.join(HERE, 'posts.json'), encoding='utf-8'))
    have = {p['slug'] for p in posts}
    os.makedirs(os.path.join(HERE, 'drafts'), exist_ok=True)
    for it in chosen:
        text, og = collect.article_text(it['url'])
        if len(text) < 200: text = it.get('summary', '') + '\n' + text
        j = rewrite(it, text)
        save_draft(it, j, og, mode)
        full = json.load(open(pool_p, encoding='utf-8'))
        for x in full:
            if x['url'] == it['url']: x['used'] = True
        json.dump(full, open(pool_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)



if __name__ == '__main__':
    main()
