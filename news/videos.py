#!/usr/bin/env python3
"""Showband Group — video səhifələri: /videolar/ və /videolar/<kateqoriya>/
Klip siyahısı index.html-dəki `var CL=[...]`-dan oxunur (yeni video ora əlavə olunanda səhifələr özü yenilənir).
build_news.py tərəfindən çağırılır."""
import json, os, re
from build_news import head, foot, SITE, CFG, E, w, ROOT

WA = f'https://wa.me/{CFG["whatsapp"]}?text='

# slug, CL-dəki e, başlıq (h1 üçün), qısa ad (düymə), WhatsApp mətni
CATS = [
    ('toy', 'toy', 'Toy və nişan', 'Toy', 'Salam! Toy üçün məlumat almaq istəyirəm.'),
    ('instrumental-band', 'band', 'İnstrumental Band', 'İnstrumental Band', 'Salam! İnstrumental band üçün məlumat almaq istəyirəm.'),
    ('korporativ', 'korp', 'Korporativ', 'Korporativ', 'Salam! Korporativ tədbir üçün məlumat almaq istəyirəm.'),
    ('ad-gunu', 'adgunu', 'Ad günü', 'Ad günü', 'Salam! Ad günü üçün məlumat almaq istəyirəm.'),
    ('party', 'party', 'Son Zəng & Party', 'Son Zəng & Party', 'Salam! Son zəng / party üçün məlumat almaq istəyirəm.'),
    ('acilis', 'acilis', 'Toy açılışı', 'Açılış', 'Salam! Toy açılışı üçün məlumat almaq istəyirəm.'),
    ('diger', 'diger', 'Digər çıxışlar', 'Digər', 'Salam! Tədbir üçün məlumat almaq istəyirəm.'),
]

CSS = '''<style>
.vh{padding-top:24px;max-width:860px}
.vh h1{font:900 clamp(32px,4.4vw,56px)/1.04 var(--d);letter-spacing:-.035em;margin:18px 0 14px;text-wrap:balance}
.vh h1 em{font-style:normal;color:var(--red2)}
.vh .lead{font-size:18px;line-height:1.6;color:#e2e2e8;margin:0;max-width:640px}
.vcat{display:flex;flex-wrap:wrap;gap:8px;margin-top:26px}
.vcat a{font:600 14px var(--s);padding:10px 18px;border-radius:999px;border:1px solid var(--line);text-decoration:none;color:var(--fg)}
.vcat a.on{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.vcat a small{color:var(--mute);margin-left:4px}.vcat a.on small{color:var(--bg);opacity:.6}
.vg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-top:30px}
.vc{margin:0}
.vc video{width:100%;aspect-ratio:9/16;border-radius:20px;background:#000;object-fit:cover;display:block}
.vc figcaption{margin-top:10px;font-weight:600;font-size:14px;line-height:1.35}
.vc figcaption span{display:block;color:var(--mute);font-weight:500;font-size:12px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:2px}
.vbt{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
@media(max-width:1000px){.vg{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.vg{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.vc figcaption{font-size:13px}}
</style>'''

PLAY1 = '<script>document.addEventListener("play",function(e){document.querySelectorAll(".vg video").forEach(function(v){if(v!==e.target)v.pause()})},true)</script>'


def clips():
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r"var CL=\[\n(.*?)\n\];", s, re.S)
    return [{'e': e, 'k': k, 'w': bool(wd), 'n': n} for e, k, wd, n in re.findall(r"\{e:'(\w+)',k:'(\w+)',(w:1,)?n:\['([^']*)'", m.group(1))]


def page(slug, items, allc, cur):
    rel = '../../' if slug else '../'
    url = f'{SITE}/videolar/{slug + "/" if slug else ""}'
    lab = {c[1]: c[3] for c in CATS}
    if cur:
        _, e, h1, short, wa_t = cur
        title = f'{h1} videoları — Showband Group | Bakı'
        desc = f'Showband Group-un {h1.lower()} tədbirlərindən canlı videolar: DJ, showman, instrumental band və şou. Bakı.'
        h1h = f'{E(h1)} <em>videoları</em>'
        lead = f'{h1} tədbirlərimizdən {len(items)} video. Baxın, bəyənin — tarixinizi bron edin.'
    else:
        wa_t = 'Salam! Tədbir üçün məlumat almaq istəyirəm.'
        title = 'Videolar — Showband Group | Bakı'
        desc = 'Showband Group-un toy, korporativ, ad günü, son zəng, party, açılış və instrumental band tədbirlərindən canlı videolar. Bakı.'
        h1h = 'Səhnədən <em>canlı</em>'
        lead = f'Toy, korporativ, ad günü, son zəng, party, açılış və instrumental band çıxışlarından {len(items)} video.'
    wa = WA + wa_t.replace(' ', '%20')
    og = f'video/ev_{items[0]["k"]}.jpg' if items else 'img/og.jpg'
    crumbs = [{'@type': 'ListItem', 'position': 1, 'name': 'Ana səhifə', 'item': SITE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': 'Videolar', 'item': SITE + '/videolar/'}]
    if cur: crumbs.append({'@type': 'ListItem', 'position': 3, 'name': cur[2], 'item': url})
    vids = []
    for c in items:
        v = {'@type': 'VideoObject', 'name': f'Showband Group — {c["n"]}', 'description': f'{c["n"]}: Showband Group canlı şou. Bakı.',
             'thumbnailUrl': f'{SITE}/video/ev_{c["k"]}.jpg', 'contentUrl': f'{SITE}/video/ev_{c["k"]}.mp4', 'uploadDate': '2026-11-06'}
        vids.append(v)
    ld = {'@context': 'https://schema.org', '@graph': [{'@type': 'BreadcrumbList', 'itemListElement': crumbs}] + vids}
    extra = CSS + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    count = lambda e: sum(1 for c in allc if c['e'] == e)
    tabs = f'<a href="{rel}videolar/"{" class=on" if not cur else ""}>Hamısı <small>{len(allc)}</small></a>' + ''.join(
        f'<a href="{rel}videolar/{s}/"{" class=on" if cur and cur[0] == s else ""}>{E(sh)} <small>{count(e)}</small></a>'
        for s, e, _, sh, _ in CATS if count(e))
    grid = ''.join(
        f'<figure class="vc"><video{" style=\"object-fit:contain\"" if c["w"] else ""} controls playsinline preload="none" poster="{rel}video/ev_{c["k"]}.jpg" src="{rel}video/ev_{c["k"]}.mp4" aria-label="{E(c["n"])}"></video>'
        f'<figcaption><span>{E(lab.get(c["e"], ""))}</span>{E(c["n"])}</figcaption></figure>' for c in items)
    bc = (f'<a href="{rel}">Ana səhifə</a><span>›</span>' + (f'<a href="{rel}videolar/">Videolar</a><span>›</span><em>{E(cur[2])}</em>' if cur else '<em>Videolar</em>'))
    return head(title, desc, url, rel, 'website', extra, og).replace(f'<a class="on" href="{rel}xeberler/">', f'<a href="{rel}xeberler/">').replace(f'<a href="{rel}#video">', f'<a class="on" href="{rel}#video">') + f'''
 <nav class="bc" aria-label="breadcrumb">{bc}</nav>
 <section class="vh">
  <span class="chip">Showband Group · Videolar</span>
  <h1>{h1h}</h1>
  <p class="lead">{E(lead)}</p>
  <div class="vbt"><a class="btn" href="{rel}#bron">Tarix seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </section>
 <nav class="vcat" aria-label="Kateqoriyalar">{tabs}</nav>
 <div class="vg">{grid}</div>
 <aside class="cta">
  <div><span class="k">Showband Group</span><h2>Tarixinizi <em>bron</em> edin</h2><p>Tarix, məkan və tədbir növünü yazın — paketi və qiyməti dəqiqləşdirək.</p></div>
  <div class="cb"><a class="btn" href="{rel}#bron">Tarix seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </aside>
''' + PLAY1 + foot(rel)


def build():
    allc = clips()
    w('videolar/index.html', page('', allc, allc, None))
    out = ['videolar']
    for cat in CATS:
        items = [c for c in allc if c['e'] == cat[1]]
        if not items: continue
        w(f'videolar/{cat[0]}/index.html', page(cat[0], items, allc, cat))
        out.append(f'videolar/{cat[0]}')
    return out


if __name__ == '__main__':
    print(build())
