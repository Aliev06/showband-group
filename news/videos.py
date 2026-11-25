#!/usr/bin/env python3
"""Showband Group — video səhifələri: /videolar/ və /videolar/<kateqoriya>/
Klip siyahısı index.html-dəki `var CL=[...]`-dan oxunur (yeni video ora əlavə olunanda səhifələr özü yenilənir).
build_news.py tərəfindən çağırılır."""
import json, os, re
from build_news import head, foot, SITE, CFG, E, w, ROOT
from i18n_site import LANGS, pre, localize

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

# RU / EN: başlıq (h1), qısa ad, WhatsApp mətni — CATS sırası ilə
CATS_T = {
 'ru': [('Свадьба и помолвка', 'Свадьба', 'Здравствуйте! Хочу узнать о свадьбе.'),
        ('Instrumental Band', 'Instrumental Band', 'Здравствуйте! Хочу узнать об инструментальном бэнде.'),
        ('Корпоратив', 'Корпоратив', 'Здравствуйте! Хочу узнать о корпоративе.'),
        ('День рождения', 'День рождения', 'Здравствуйте! Хочу узнать о дне рождения.'),
        ('Последний звонок и Party', 'Последний звонок и Party', 'Здравствуйте! Хочу узнать о последнем звонке / party.'),
        ('Открытие свадьбы', 'Открытие', 'Здравствуйте! Хочу узнать об открытии свадьбы.'),
        ('Другие выступления', 'Другое', 'Здравствуйте! Хочу узнать о мероприятии.')],
 'en': [('Weddings & engagements', 'Weddings', 'Hello! I would like to know more about a wedding.'),
        ('Instrumental Band', 'Instrumental Band', 'Hello! I would like to know more about the instrumental band.'),
        ('Corporate', 'Corporate', 'Hello! I would like to know more about a corporate event.'),
        ('Birthday', 'Birthday', 'Hello! I would like to know more about a birthday party.'),
        ('Last Bell & Party', 'Last Bell & Party', 'Hello! I would like to know more about a last bell / party.'),
        ('Wedding opening', 'Opening', 'Hello! I would like to know more about a wedding opening.'),
        ('Other performances', 'Other', 'Hello! I would like to know more about an event.')],
}
TX = {
 'ru': dict(t_cat='Видео: {} — Showband Group | Баку', d_cat='Живые видео Showband Group с мероприятий «{}»: DJ, шоумен, инструментальный бэнд и шоу. Баку.',
            h_cat='{} <em>видео</em>', l_cat='{n} видео с наших мероприятий «{h}». Смотрите — и бронируйте дату.',
            t_all='Видео — Showband Group | Баку', d_all='Живые видео Showband Group: свадьбы, корпоративы, дни рождения, последний звонок, party, открытия и инструментальный бэнд. Баку.',
            h_all='Живьём <em>со сцены</em>', l_all='{n} видео со свадеб, корпоративов, дней рождения, последних звонков, party, открытий и выступлений инструментального бэнда.',
            wa_all='Здравствуйте! Хочу узнать о мероприятии.', home='Главная', vids='Видео', all='Все', chip='Showband Group · Видео', cats='Категории'),
 'en': dict(t_cat='{} videos — Showband Group | Baku', d_cat='Live videos from Showband Group {} events: DJ, showman, instrumental band and show. Baku.',
            h_cat='{} <em>videos</em>', l_cat='{n} videos from our {h} events. Watch — and book your date.',
            t_all='Videos — Showband Group | Baku', d_all='Live videos from Showband Group weddings, corporate events, birthdays, last bell, parties, openings and instrumental band shows. Baku.',
            h_all='Live <em>from the stage</em>', l_all='{n} videos from weddings, corporate events, birthdays, last bell, parties, openings and instrumental band shows.',
            wa_all='Hello! I would like to know more about an event.', home='Home', vids='Videos', all='All', chip='Showband Group · Videos', cats='Categories'),
}


def cats(lang):
    if lang == 'az': return CATS
    return [(s, e, *CATS_T[lang][i]) for i, (s, e, *_r) in enumerate(CATS)]


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
.vc .yt{position:relative;display:block;width:100%;aspect-ratio:9/16;border:0;padding:0;border-radius:20px;overflow:hidden;background:#000;cursor:pointer}
.vc .yt img{width:100%;height:100%;object-fit:cover;display:block}
.vc .yt i{position:absolute;left:50%;top:50%;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;background:rgba(0,0,0,.55);color:#fff;font-style:normal;font-size:24px;display:grid;place-items:center;backdrop-filter:blur(4px)}
.vc iframe{width:100%;aspect-ratio:9/16;border:0;border-radius:20px;display:block;background:#000}
.vc figcaption{margin-top:10px;font-weight:600;font-size:14px;line-height:1.35}
.vc figcaption span{display:block;color:var(--mute);font-weight:500;font-size:12px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:2px}
.vbt{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
@media(max-width:1000px){.vg{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.vg{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.vc figcaption{font-size:13px}}
</style>'''

PLAY1 = '<script>document.addEventListener("play",function(e){document.querySelectorAll(".vg video").forEach(function(v){if(v!==e.target)v.pause()})},true);document.querySelectorAll(".vc .yt").forEach(function(b){b.onclick=function(){document.querySelectorAll(".vg video").forEach(function(v){v.pause()});var f=document.createElement("iframe");f.src="https://www.youtube-nocookie.com/embed/"+b.dataset.yt+"?autoplay=1&rel=0&playsinline=1";f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;b.replaceWith(f)}})</script>'


def clips():
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r"var CL=\[\n(.*?)\n\];", s, re.S)
    out = []
    for line in m.group(1).split('\n'):
        r = re.search(r"\{e:'(\w+)',k:'(\w+)',(w:1,)?n:\['([^']*)','([^']*)','([^']*)'", line)
        if not r: continue
        y = re.search(r"url:'[^']*?([\w-]{11})'", line)
        out.append({'e': r.group(1), 'k': r.group(2), 'w': bool(r.group(3)), 'n': r.group(4), 'nl': {'az': r.group(4), 'ru': r.group(5), 'en': r.group(6)},
                    'yt': y.group(1) if y else ''})
    return out


def page(slug, items, allc, cur, lang='az'):
    rel = ('../../' if slug else '../') + ('' if lang == 'az' else '../')
    url = f'{SITE}/{pre(lang)}videolar/{slug + "/" if slug else ""}'
    CS = cats(lang)
    lab = {c[1]: c[3] for c in CS}
    items = [dict(c, n=c['nl'][lang]) for c in items]
    X = TX.get(lang)
    if lang != 'az':
        if cur:
            _, e, h1, short, wa_t = cur
            title, desc = X['t_cat'].format(h1), X['d_cat'].format(h1)
            h1h, lead = X['h_cat'].format(E(h1)), X['l_cat'].format(n=len(items), h=h1)
        else:
            wa_t, title, desc, h1h, lead = X['wa_all'], X['t_all'], X['d_all'], X['h_all'], X['l_all'].format(n=len(items))
    elif cur:
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
    home, vl, allw, chip, catw = ('Ana səhifə', 'Videolar', 'Hamısı', 'Showband Group · Videolar', 'Kateqoriyalar') if lang == 'az' else (X['home'], X['vids'], X['all'], X['chip'], X['cats'])
    crumbs = [{'@type': 'ListItem', 'position': 1, 'name': home, 'item': SITE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': vl, 'item': f'{SITE}/{pre(lang)}videolar/'}]
    if cur: crumbs.append({'@type': 'ListItem', 'position': 3, 'name': cur[2], 'item': url})
    vids = []
    for c in items:
        v = {'@type': 'VideoObject', 'name': f'Showband Group — {c["n"]}', 'description': f'{c["n"]}: Showband Group canlı şou. Bakı.',
             'thumbnailUrl': f'{SITE}/video/ev_{c["k"]}.jpg', 'contentUrl': f'{SITE}/video/ev_{c["k"]}.mp4', 'uploadDate': '2026-11-06'}
        if c['yt']: v['embedUrl'] = f'https://www.youtube.com/embed/{c["yt"]}'
        vids.append(v)
    ld = {'@context': 'https://schema.org', '@graph': [{'@type': 'BreadcrumbList', 'itemListElement': crumbs}] + vids}
    extra = CSS + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    count = lambda e: sum(1 for c in allc if c['e'] == e)
    tabs = f'<a href="{rel}videolar/"{" class=on" if not cur else ""}>{allw} <small>{len(allc)}</small></a>' + ''.join(
        f'<a href="{rel}videolar/{s}/"{" class=on" if cur and cur[0] == s else ""}>{E(sh)} <small>{count(e)}</small></a>'
        for s, e, _, sh, _ in CS if count(e))
    grid = ''.join(
        (f'<figure class="vc"><button class="yt" data-yt="{c["yt"]}" aria-label="{E(c["n"])} — video"><img src="{rel}video/ev_{c["k"]}.jpg" alt="{E(c["n"])}" loading="lazy"{" style=\"object-fit:contain\"" if c["w"] else ""}><i>▶</i></button>' if c['yt'] else
         f'<figure class="vc"><video{" style=\"object-fit:contain\"" if c["w"] else ""} controls playsinline preload="none" poster="{rel}video/ev_{c["k"]}.jpg" src="{rel}video/ev_{c["k"]}.mp4" aria-label="{E(c["n"])}"></video>') +
        f'<figcaption><span>{E(lab.get(c["e"], ""))}</span>{E(c["n"])}</figcaption></figure>' for c in items)
    bc = (f'<a href="{rel}">{home}</a><span>›</span>' + (f'<a href="{rel}videolar/">{vl}</a><span>›</span><em>{E(cur[2])}</em>' if cur else f'<em>{vl}</em>'))
    return localize(head(title, desc, url, rel, 'website', extra, og).replace(f'<a class="on" href="{rel}xeberler/">', f'<a href="{rel}xeberler/">').replace(f'<a href="{rel}#video">', f'<a class="on" href="{rel}#video">') + f'''
 <nav class="bc" aria-label="breadcrumb">{bc}</nav>
 <section class="vh">
  <span class="chip">{chip}</span>
  <h1>{h1h}</h1>
  <p class="lead">{E(lead)}</p>
  <div class="vbt"><a class="btn" href="{rel}#bron">Tarix seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </section>
 <nav class="vcat" aria-label="{catw}">{tabs}</nav>
 <div class="vg">{grid}</div>
 <aside class="cta">
  <div><span class="k">Showband Group</span><h2>Tarixinizi <em>bron</em> edin</h2><p>Tarix, məkan və tədbir növünü yazın — paketi və qiyməti dəqiqləşdirək.</p></div>
  <div class="cb"><a class="btn" href="{rel}#bron">Tarix seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </aside>
''' + PLAY1 + foot(rel), lang, rel, f'videolar/{slug + "/" if slug else ""}')


def build():
    allc = clips()
    out = []
    for lang in LANGS:
        w(f'{pre(lang)}videolar/index.html', page('', allc, allc, None, lang)); out.append(f'{pre(lang)}videolar')
        for cat in cats(lang):
            items = [c for c in allc if c['e'] == cat[1]]
            if not items: continue
            w(f'{pre(lang)}videolar/{cat[0]}/index.html', page(cat[0], items, allc, cat, lang))
            out.append(f'{pre(lang)}videolar/{cat[0]}')
    return out


if __name__ == '__main__':
    print(build())
