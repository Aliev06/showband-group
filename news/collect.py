#!/usr/bin/env python3
"""Showband Group — musiqi xəbərlərinin toplayıcısı (yalnız standart kitabxana).
  python3 news/collect.py                 # mənbələri oxuyur → news/candidates.json
  python3 news/collect.py --snap DIR      # internet əvəzinə DIR-dəki saxlanmış fayllardan (test üçün)
Nəticə: ən çox 25 namizəd, musiqi ehtimalına görə sıralanmış. Sonrakı addım: news/write.py (Gemini).
"""
import json, os, re, sys, html, hashlib, urllib.request, urllib.parse, datetime as dt
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'

SOURCES = [
    # RSS: yalnız uyğun kateqoriyalar götürülür (cats boşdursa hamısı, sonra açar sözlə süzülür)
    {'name': 'Oxu.az', 'type': 'rss', 'url': 'https://oxu.az/feed', 'cats': ['Mədəniyyət', 'Şou-biznes', 'Digər', 'Dünya']},
    {'name': 'Report.az', 'type': 'rss', 'url': 'https://report.az/rss', 'cats': ['Mədəniyyət', 'Şou-biznes', 'Digər ölkələr']},
    {'name': 'APA', 'type': 'rss', 'url': 'https://apa.az/rss', 'cats': ['Mədəniyyət', 'Şou-biznes']},
    {'name': 'Oxu.az', 'type': 'html', 'url': 'https://oxu.az/shou-biznes', 'link': r'^/shou-biznes/[a-z0-9-]{15,}'},
    {'name': 'Oxu.az', 'type': 'html', 'url': 'https://oxu.az/medeniyyet', 'link': r'^/medeniyyet/[a-z0-9-]{15,}'},
    # HTML bölmələr: hamısı mədəniyyət/şou olduğuna görə hamısı namizəddir
    {'name': 'Qafqazinfo', 'type': 'html', 'url': 'https://qafqazinfo.az/news/category/sou-20', 'link': r'/news/detail/'},
    {'name': 'Qafqazinfo', 'type': 'html', 'url': 'https://qafqazinfo.az/news/category/medeniyyet-10/', 'link': r'/news/detail/'},
    {'name': 'Axar.az', 'type': 'html', 'url': 'https://axar.az/news/kult/', 'link': r'/news/kult/\d+\.html'},
]

# musiqi siqnalları (ilkin süzgəc; son qərarı Gemini verir)
MUSIC = r'mahnı|mahnısı|klip|konsert|albom|müğənni|ifaçı|ifa |səhnəyə|festival|avroviziya|eurovision|duet|trek|sinql|musiqi|bəstəkar|bəstə|reper|rep |qrupu|orkestr|opera|caz|muğam|aşıq|tur |turne|qrammi|grammy|spotify|youtube|hit|nəğmə|xanəndə|dj '
NOISE = r'futbol|məhkəmə|həbs|qəza|siyasi|parlament|nazirlik|bank|manat|neft|hava proqnozu|serial|film|aktyor|aktrisa|arıqla|boşan|hamilə'


def get(url, snap=None):
    if snap:
        fn = os.path.join(snap, hashlib.md5(url.encode()).hexdigest()[:12] + '.txt')
        return open(fn, encoding='utf-8').read() if os.path.exists(fn) else ''
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'az,en;q=0.8'})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode(r.headers.get_content_charset() or 'utf-8', 'replace')
    except Exception as e:
        print('  ! oxunmadı:', url, e); return ''


def clean(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def norm(t):  # dublikat yoxlaması üçün
    t = clean(t).lower()
    t = re.sub(r'[^\wəğıöüçş ]', ' ', t)
    return [w for w in t.split() if len(w) > 3]


def parse_rss(src, text):
    out = []
    text = text.strip()
    if text and not text.rstrip().endswith('</rss>'): text = text[: text.rfind('</item>') + 7] + '</channel></rss>'
    try: root = ET.fromstring(text)
    except Exception as e: print('  ! RSS xətası', src['name'], e); return out
    for it in root.iter('item'):
        g = lambda k: (it.findtext(k) or '').strip()
        cat = g('category')
        if src.get('cats') and cat and cat not in src['cats']: continue
        enc = it.find('enclosure')
        try: d = parsedate_to_datetime(g('pubDate')).isoformat()
        except Exception: d = ''
        out.append({'title': clean(g('title')), 'url': g('link'), 'source': src['name'], 'cat': cat, 'date': d,
                    'summary': clean(g('description'))[:400], 'image': enc.get('url') if enc is not None else ''})
    return out


def parse_html(src, text):
    out, seen = [], set()
    base = '{0.scheme}://{0.netloc}'.format(urllib.parse.urlparse(src['url']))
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', text, re.S | re.I):
        href, inner = m.group(1), m.group(2)
        if not re.search(src['link'], href): continue
        title = clean(inner)
        if len(title) < 25: continue
        url = urllib.parse.urljoin(base, href)
        if url in seen: continue
        seen.add(url)
        img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', inner)
        out.append({'title': title, 'url': url, 'source': src['name'], 'cat': 'Şou/Mədəniyyət', 'date': '',
                    'summary': '', 'image': urllib.parse.urljoin(base, img.group(1)) if img else ''})
    return out[:30]


def score(it):
    t = (it['title'] + ' ' + it['summary']).lower()
    s = 3 * len(re.findall(MUSIC, t)) - 2 * len(re.findall(NOISE, t))
    if it['cat'] in ('Mədəniyyət', 'Şou-biznes', 'Şou/Mədəniyyət'): s += 1
    return s


def article_text(url, snap=None):
    """Məqalə səhifəsindən əsas mətni çıxarır (ən uzun <p> bloku)."""
    h = get(url, snap)
    h = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    ps = [clean(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>', h, re.S | re.I)]
    ps = [p for p in ps if len(p) > 60 and not re.search(r'©|bütün hüquqlar|abunə ol|reklam', p, re.I)]
    og = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', h)
    return '\n'.join(ps)[:6000], (og.group(1) if og else '')


def main():
    snap = sys.argv[sys.argv.index('--snap') + 1] if '--snap' in sys.argv else None
    seen_p = os.path.join(HERE, 'seen.json')
    seen = json.load(open(seen_p, encoding='utf-8')) if os.path.exists(seen_p) else {'urls': [], 'titles': []}
    items = []
    for s in SOURCES:
        txt = get(s['url'], snap)
        got = parse_rss(s, txt) if s['type'] == 'rss' else parse_html(s, txt)
        print(f"{s['name']:<11} {len(got):>3} xəbər  ({s['url']})")
        items += got
    # artıq istifadə olunanları və dublikatları at
    out, sigs = [], [set(t) for t in seen['titles']]
    for it in sorted(items, key=score, reverse=True):
        if it['url'] in seen['urls']: continue
        w = set(norm(it['title']))
        if not w or any(len(w & s) / max(1, len(w | s)) > .45 for s in sigs): continue
        sigs.append(w); it['score'] = score(it); out.append(it)
    # hər saat işləyir: yeni namizədlər 24 saatlıq hovuza (pool.json) əlavə olunur
    now = dt.datetime.now(dt.timezone.utc)
    pool_p = os.path.join(HERE, 'pool.json')
    pool = json.load(open(pool_p, encoding='utf-8')) if os.path.exists(pool_p) else []
    pool = [x for x in pool if now - dt.datetime.fromisoformat(x['found']) < dt.timedelta(hours=24)]
    known = {x['url'] for x in pool}
    added = 0
    for it in out:
        if it['url'] in known or it['score'] < 0: continue
        if any(len(set(norm(it['title'])) & set(norm(x['title']))) / max(1, len(set(norm(it['title'])) | set(norm(x['title'])))) > .45 for x in pool): continue
        it['found'] = now.isoformat(); pool.append(it); known.add(it['url']); added += 1
    json.dump(pool, open(pool_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\nCəmi {len(items)} → dublikatsız {len(out)} → hovuza yeni {added} (hovuzda {len(pool)})')


if __name__ == '__main__':
    main()
