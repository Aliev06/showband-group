#!/usr/bin/env python3
"""Showband Group — xəbər səhifələrinin generatoru.
news/posts.json -> xeberler/index.html, xeberler/<slug>/index.html, sitemap.xml, robots.txt, xeberler/rss.xml
İşə salma (sayt qovluğundan): python3 news/build_news.py
"""
import json, os, html, re, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, 'news', 'config.json'), encoding='utf-8'))
POSTS = json.load(open(os.path.join(ROOT, 'news', 'posts.json'), encoding='utf-8'))
POSTS.sort(key=lambda p: p['date'], reverse=True)
SITE = CFG['site_url'].rstrip('/')
E = lambda s: html.escape(str(s), quote=True)
AY = ['yanvar','fevral','mart','aprel','may','iyun','iyul','avqust','sentyabr','oktyabr','noyabr','dekabr']

def fdate(d):
    d = dt.date.fromisoformat(d); return f'{d.day} {AY[d.month-1]} {d.year}'

def mins(p):
    words = len((p['lead'] + ' ' + ' '.join(b.get('p', '') for b in p['body'])).split())
    return max(1, round(words / 180))

# hər kateqoriyaya öz rəngi
GR = ['linear-gradient(135deg,#e3122b,#4a0711)', 'linear-gradient(135deg,#2b3a8f,#0b0b1e)',
      'linear-gradient(135deg,#8a2be2,#26073f)', 'linear-gradient(135deg,#d9480f,#3b0d02)',
      'linear-gradient(135deg,#0f9d8a,#04231f)']
CATS = []
for p in POSTS:
    if p['category'] not in CATS: CATS.append(p['category'])
def cidx(cat): return sum(map(ord, cat)) % len(GR)  # sabit rəng: kateqoriya adından
def grad(cat): return GR[cidx(cat)]

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;900&family=Montserrat:wght@400;500;600;700&display=swap">'
ICON = '<link rel="icon" type="image/png" sizes="48x48" href="/img/favicon-48.png?v=2"><link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png?v=2"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png">'

def head(title, desc, url, rel, og_type='website', extra='', og_img='img/og.jpg'):
    return f'''<!doctype html>
<html lang="az">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:site_name" content="{E(CFG['site_name'])}">
<meta property="og:locale" content="az_AZ">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Showband Group — Musiqi xəbərləri" href="{SITE}/xeberler/rss.xml">
{ICON}
{FONTS}
<link rel="stylesheet" href="{rel}xeberler/news.css">
{extra}
</head>
<body>
<div class="w">
 <header class="nav">
  <a class="logo" href="{rel}" aria-label="Showband Group"><img src="{rel}img/logo.png" alt="Showband Group" width="900" height="258"></a>
  <nav><a href="{rel}#xidmet">Xidmətlər</a><a href="{rel}#paket">Paketlər</a><a href="{rel}#video">Videolar</a><a class="on" href="{rel}xeberler/">Xəbərlər</a></nav>
  <a class="btn sm" href="{rel}#bron">Tarix seç</a>
 </header>
'''

FILEFIX = '<script>if(location.protocol==="file:")document.addEventListener("click",function(e){var a=e.target.closest("a[href]");if(!a)return;var h=a.getAttribute("href");if(/^(https?:|mailto:|tel:|#)/.test(h))return;var p=h.split("#");if(p[0]===""||p[0].slice(-1)==="/"){p[0]+="index.html";e.preventDefault();location.href=p.join("#")}});</script>'

def foot(rel):
    y = dt.date.today().year
    return f'''
 <footer>
  <a class="logo" href="{rel}"><img src="{rel}img/logo.png" alt="Showband Group" width="900" height="258"></a>
  <p>Toy, nişan, ad günü və korporativ tədbirlər üçün canlı musiqi və şou. Bakı.</p>
  <p class="pt"><a href="{rel}toy/">Toy və nişan</a> · <a href="{rel}korporativ/">Korporativ</a> · <a href="{rel}ad-gunu/">Ad günü</a></p>
  <p class="pt">© {y} Showband Group · <a href="{rel}">Ana səhifə</a> · <a href="{rel}xeberler/">Xəbərlər</a> · <a href="{rel}#bron">Bron</a> · <a href="{rel}privacy/">Məxfilik</a> · <a href="{rel}terms/">Şərtlər</a></p>
 </footer>
</div>
<a class="fab" href="{rel}#bron">Tarix seç</a>
'''+FILEFIX+'''
</body>
</html>
'''

def cover(p, big=False, rel=''):
    if p.get('image'):
        return (f'<div class="cv ph{" big" if big else ""}"><img src="{rel}{E(p["image"])}" alt="{E(p["title"])}" loading="lazy">'
                f'<span>{E(p["category"])}</span>' + f'<img class="wm" src="{rel}img/logo.png" alt="Showband Group">' + '</div>')
    return f'<div class="cv{" big" if big else ""}" style="background:{grad(p["category"])}"><span>{E(p["category"])}</span><b>{E(p["title"])}</b><i>SHOWBAND GROUP · XƏBƏR</i></div>'

def card(p, rel, big=False):
    return (f'<a class="nc{" big" if big else ""}" href="{rel}xeberler/{p["slug"]}/" data-cat="{E(p["category"])}">{cover(p, big, rel)}'
            f'<div class="nb"><small>{fdate(p["date"])} · {mins(p)} dəq</small><h3>{E(p["title"])}</h3><p>{E(p["description"])}</p></div></a>')

def article(p):
    rel = '../../'
    url = f'{SITE}/xeberler/{p["slug"]}/'
    ld = {
        '@context': 'https://schema.org', '@graph': [
            {'@type': 'NewsArticle', 'headline': p['title'][:110], 'description': p['description'],
             'datePublished': p['date'], 'dateModified': p.get('updated', p['date']),
             'inLanguage': 'az', 'mainEntityOfPage': url, 'image': [f'{SITE}/' + p.get('image', 'img/og.jpg')],
             'keywords': ', '.join(p['tags']), 'articleSection': p['category'],
             'author': {'@type': 'Organization', 'name': CFG['site_name'], 'url': SITE + '/'},
             'publisher': {'@type': 'Organization', 'name': CFG['site_name'],
                           'logo': {'@type': 'ImageObject', 'url': f'{SITE}/img/logo.png'}}},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Ana səhifə', 'item': SITE + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Xəbərlər', 'item': SITE + '/xeberler/'},
                {'@type': 'ListItem', 'position': 3, 'name': p['title'], 'item': url}]}]}
    extra = (f'<meta property="article:published_time" content="{p["date"]}">'
             f'<meta property="article:section" content="{E(p["category"])}">'
             + ''.join(f'<meta property="article:tag" content="{E(t)}">' for t in p['tags'])
             + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')
    body = ''.join(f'<h2>{E(b["h"])}</h2>' if 'h' in b else f'<p>{E(b["p"])}</p>' for b in p['body'])
    rel_posts = [x for x in POSTS if x['slug'] != p['slug']]
    rel_posts = sorted(rel_posts, key=lambda x: (x['category'] != p['category'], x['date']), reverse=False)[:3]
    wa = f'https://wa.me/{CFG["whatsapp"]}?text=' + re.sub(' ', '%20', 'Salam! Tədbir üçün məlumat almaq istəyirəm.')
    return head(f'{p["title"]} | Showband Group', p['description'], url, rel, 'article', extra, p.get('image', 'img/og.jpg')) + f'''
 <nav class="bc" aria-label="breadcrumb"><a href="{rel}">Ana səhifə</a><span>›</span><a href="{rel}xeberler/">Xəbərlər</a><span>›</span><em>{E(p["category"])}</em></nav>
 <article class="art">
  <header class="ah">
   <span class="chip">{E(p["category"])}</span>
   <h1>{E(p["title"])}</h1>
   <div class="meta"><time datetime="{p["date"]}">{fdate(p["date"])}</time><span>{mins(p)} dəq oxu</span><span>Showband Group</span></div>
  </header>
  {cover(p, True, rel)}
  <div class="tx">
   <p class="lead">{E(p["lead"])}</p>
   {body}
   <ul class="tags">{"".join(f"<li>#{E(t)}</li>" for t in p["tags"])}</ul>
   {(f'<p class="src">Mənbə: <a href="{E(p["source"]["url"])}" target="_blank" rel="noopener nofollow">{E(p["source"]["name"])}</a></p>' if p.get("source") else '')}
  </div>
 </article>
 <aside class="cta">
  <div><span class="k">Showband Group</span><h2>Tədbiriniz üçün <em>canlı musiqi</em>?</h2><p>Toy, nişan, ad günü və korporativ tədbirlər — band, showman, DJ, səs-işıq bir komandada.</p></div>
  <div class="cb"><a class="btn" href="{rel}#bron">Tarixi seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </aside>
 <section class="more"><h2>Digər xəbərlər</h2><div class="ng">{"".join(card(x, rel) for x in rel_posts)}</div></section>
''' + foot(rel)

def listing():
    rel = '../'
    url = f'{SITE}/xeberler/'
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Musiqi xəbərləri — Showband Group',
          'url': url, 'inLanguage': 'az',
          'mainEntity': {'@type': 'ItemList', 'itemListElement': [
              {'@type': 'ListItem', 'position': i + 1, 'url': f'{SITE}/xeberler/{p["slug"]}/'} for i, p in enumerate(POSTS[:30])]}}
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    chips = '<button class="on" data-f="">Hamısı</button>' + ''.join(f'<button data-f="{E(c)}">{E(c)}</button>' for c in CATS)
    first, rest = (POSTS[0], POSTS[1:]) if POSTS else (None, [])
    return head('Musiqi xəbərləri — yeni mahnılar, kliplər, artistlər | Showband Group',
                'Azərbaycan və dünya musiqisindən son xəbərlər: yeni mahnılar, kliplər, konsertlər və artistlər. Showband Group xəbər lenti.',
                url, rel, 'website', extra) + f'''
 <section class="lh">
  <span class="k">Xəbər lenti</span>
  <h1>Musiqi <em>xəbərləri</em></h1>
  <p>Yeni mahnılar, kliplər, konsertlər və artistlər haqqında ən son xəbərlər.</p>
  <div class="chips" id="chips">{chips}</div>
 </section>
 <section class="ng" id="ng">{(card(first, rel) if first else '')}{"".join(card(p, rel) for p in rest)}</section>
 <p class="empty" id="empty" hidden>Bu bölmədə hələ xəbər yoxdur.</p>
<script>
(function(){{var b=document.querySelectorAll('#chips button'),c=document.querySelectorAll('#ng .nc'),e=document.getElementById('empty');
b.forEach(function(x){{x.onclick=function(){{b.forEach(function(y){{y.classList.toggle('on',y===x)}});var f=x.dataset.f,n=0;
c.forEach(function(k){{var s=!f||k.dataset.cat===f;k.hidden=!s;if(s)n++}});e.hidden=n>0}}}})}})();
</script>
''' + foot(rel)

def rss():
    items = ''.join(f'''<item><title>{E(p["title"])}</title><link>{SITE}/xeberler/{p["slug"]}/</link><guid>{SITE}/xeberler/{p["slug"]}/</guid><pubDate>{dt.datetime.fromisoformat(p["date"]).strftime("%a, %d %b %Y 09:00:00 +0400")}</pubDate><description>{E(p["description"])}</description><category>{E(p["category"])}</category></item>''' for p in POSTS[:30])
    return f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Showband Group — Musiqi xəbərləri</title><link>{SITE}/xeberler/</link><description>Musiqi xəbərləri</description><language>az</language>{items}</channel></rss>'

def sitemap():
    today = dt.date.today().isoformat()
    urls = [(SITE + '/', today, '1.0'), (SITE + '/xeberler/', POSTS[0]['date'] if POSTS else today, '0.8')]
    urls += [(f'{SITE}/{s}/', today, '0.9') for s in ('toy', 'korporativ', 'ad-gunu')]  # xidmət səhifələri (pages.py)
    try:
        import videos; urls += [(f'{SITE}/{s}/', today, '0.7') for s in videos.build()]  # video səhifələri (videos.py)
    except Exception as e: print('videos:', e)
    urls += [(f'{SITE}/xeberler/{p["slug"]}/', p.get('updated', p['date']), '0.6') for p in POSTS]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f' <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n' for u, d, pr in urls) + '</urlset>\n'

def w(path, txt):
    path = os.path.join(ROOT, path); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(txt)

def home_block():
    """Ana səhifədəki <!--NEWS--> blokunu son 3 xəbərlə doldurur."""
    path = os.path.join(ROOT, 'index.html')
    s = open(path, encoding='utf-8').read()
    a, b = '<!--NEWS-->', '<!--/NEWS-->'
    if a not in s or b not in s: print('index.html: NEWS marker tapılmadı'); return
    cards = ''.join(
        f'<a class="nwc" href="xeberler/{p["slug"]}/">' + (f'<div class="cv ph"><img src="{E(p["image"])}" alt="{E(p["title"])}" loading="lazy"><span>{E(p["category"])}</span></div>' if p.get('image') else f'<div class="cv" style="background:{grad(p["category"])}"><span>{E(p["category"])}</span><b>{E(p["title"])}</b><i>SHOWBAND GROUP · XƏBƏR</i></div>') +
        f'<div class="nb"><small>{fdate(p["date"])}</small><h3>{E(p["title"])}</h3></div></a>' for p in POSTS[:3])
    s = s[:s.index(a) + len(a)] + cards + s[s.index(b):]
    open(path, 'w', encoding='utf-8').write(s)

if __name__ == '__main__':
    w('xeberler/index.html', listing())
    for p in POSTS: w(f'xeberler/{p["slug"]}/index.html', article(p))
    import shutil  # posts.json-da olmayan köhnə səhifələri sil
    for dname in os.listdir(os.path.join(ROOT, 'xeberler')):
        dp = os.path.join(ROOT, 'xeberler', dname)
        if os.path.isdir(dp) and dname not in {p['slug'] for p in POSTS}:
            try: shutil.rmtree(dp)
            except Exception as e: print('silinmədi:', dname, e)
    w('xeberler/rss.xml', rss()); w('sitemap.xml', sitemap())
    home_block()
    import pages; pages.build()
    import legal; legal.build()
    import videos; videos.build()
    w('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    print('ok:', len(POSTS), 'xəbər')
