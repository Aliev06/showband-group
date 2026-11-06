#!/usr/bin/env python3
"""Showband Group — xidmət səhifələri (SEO): /toy/, /korporativ/, /ad-gunu/, /son-zeng/
build_news.py tərəfindən çağırılır; sitemap-ə də o əlavə edir."""
import json, re
from build_news import head, foot, SITE, CFG, E, w

WA = f'https://wa.me/{CFG["whatsapp"]}?text='

PAGES = [
 {'slug': 'toy', 'video': 'toy', 'img': 'img/pk_toy.webp',
  'title': 'Toy və nişan üçün canlı musiqi və şou Bakıda',
  'desc': 'Toy və nişan üçün canlı band, showman, DJ, ilk rəqs, sürprizlər və final şou. Səs, işıq, dekor, foto-video — hamısı bir komandada. Bakı.',
  'h1': 'Toy və nişan üçün <em>canlı musiqi</em> və şou',
  'lead': 'Toyunuzun hər anını — gəlin-bəyin girişindən ilk rəqsə və final şouya qədər — bir komanda idarə edir: canlı band, showman, DJ, səs, işıq və dekor.',
  'inc': ['DJ, Live Band və Showman', 'Ssenari və sürprizlər', 'Səs, işıq və dekor', 'Foto və video'],
  'about': [('Canlı band və showman', 'Qonaqlar oturub telefona baxmır: canlı ifa, interaktiv şou və enerjili aparıcılıq bütün gecə zalı ayaqda saxlayır.'),
            ('İlk rəqs və sürprizlər', 'Gəlin-bəyin girişi, ilk rəqs, tort anı və final şou — hər biri əvvəlcədən ssenariyə yazılır və vaxtında baş verir.'),
            ('Səs, işıq və dekor', 'Peşəkar səs sistemləri, işıqlandırma, lazer şouları və zalın konseptə uyğun bəzədilməsi bir komandadan.')],
  'venues': 'Altun Saray, Neapol Saray və Bakının digər şadlıq saraylarında çıxış etmişik.',
  'wa': 'Salam! Toy üçün məlumat almaq istəyirəm.'},
 {'slug': 'korporativ', 'video': 'korp', 'img': 'img/pk_korp.webp',
  'title': 'Korporativ tədbirlər üçün aparıcı, şou və canlı musiqi Bakıda',
  'desc': 'Korporativ tədbirlər, təqdimatlar və bayram gecələri: aparıcı, şou proqramı, Live Band və ya DJ, səs-işıq, səhnə və brend dekor. Bakı.',
  'h1': 'Korporativ tədbirlər üçün <em>aparıcı və şou</em>',
  'lead': 'Şirkət gecələri, təqdimatlar, Yeni il və bayram proqramları: aparıcı, şou, canlı musiqi, səhnə və brend dekor — hamısı bir komandadan.',
  'inc': ['Aparıcı və şou proqramı', 'Live Band və ya DJ', 'Səs, işıq və səhnə', 'Brend dekor', 'Foto və video'],
  'about': [('Aparıcı və proqram', 'Rəsmi hissədən əyləncəyə keçid, mükafatlandırma, interaktiv oyunlar — ssenarini şirkətinizə uyğun hazırlayırıq.'),
            ('Live Band və ya DJ', 'Tədbirin formatına görə canlı ifa, DJ və ya hər ikisi; milli və müasir repertuar.'),
            ('Səhnə və brend', 'Səhnə, işıq, ekranlar və brend rənglərinizdə dekor — tədbir şirkətinizin üslubunda görünür.')],
  'venues': 'Korporativ gecələr, təqdimatlar və bayram tədbirləri təşkil edirik.',
  'wa': 'Salam! Korporativ tədbir üçün məlumat almaq istəyirəm.'},
 {'slug': 'ad-gunu', 'video': 'adgunu', 'img': 'img/pk_mezun.webp',
  'title': 'Ad günü və party üçün DJ, showman və lazer şou Bakıda',
  'desc': 'Ad günü və party üçün DJ, showman, oyunlar, lazer və işıq şousu, tematik dekor və foto. Uşaq və böyük ad günləri. Bakı.',
  'h1': 'Ad günü və party üçün <em>DJ və şou</em>',
  'lead': 'Ad gününüzü yadda qalan gecəyə çeviririk: DJ, showman, oyunlar, lazer və işıq şousu, tematik dekor.',
  'inc': ['DJ və Showman', 'Lazer və işıq şousu', 'Tematik dekor', 'Foto'],
  'about': [('DJ və showman', 'Musiqi və aparıcılıq bir yerdə: oyunlar, müsabiqələr və rəqs — qonaqlar bütün gecə iştirak edir.'),
            ('Lazer və işıq şousu', 'Adi zalı bir neçə dəqiqəyə klub atmosferinə çeviririk.'),
            ('Tematik dekor', 'Mövzu, rənglər və detallar ad günü sahibinin zövqünə uyğun hazırlanır.')],
  'venues': 'Neolit və Bakının digər məkanlarında ad günləri keçirmişik.',
  'wa': 'Salam! Ad günü üçün məlumat almaq istəyirəm.'},
 {'slug': 'son-zeng', 'video': 'mezun', 'img': 'img/pk_mezun.webp',
  'title': 'Son zəng və məzun gecəsi üçün DJ, showman və lazer şou Bakıda',
  'desc': 'Son zəng və məzun gecələri üçün DJ, showman, işıq-lazer şou və foto-video. Məktəb və universitet məzunları üçün. Bakı.',
  'h1': 'Son zəng və <em>məzun gecəsi</em>',
  'lead': 'Məzunların ən vacib gecəsi üçün DJ, showman, işıq-lazer şou və foto-video — hər şey bir komandadan.',
  'inc': ['DJ və Showman', 'İşıq və lazer şousu', 'Tematik dekor', 'Foto və video'],
  'about': [('DJ və showman', 'Gənclərin sevdiyi musiqi, oyunlar və enerji — gecə boyu rəqs meydançası boş qalmır.'),
            ('İşıq və lazer şousu', 'Lazer, işıq effektləri və dramatik giriş anları məzun gecəsini xüsusi edir.'),
            ('Foto və video', 'Ən gözəl anlar peşəkar şəkildə çəkilir — xatirə həmişə qalır.')],
  'venues': 'Bağçalı Saray və digər məkanlarda məzun gecələri keçirmişik.',
  'wa': 'Salam! Son zəng / məzun gecəsi üçün məlumat almaq istəyirəm.'},
]

FAQ = [
 ('Qiymət nə qədərdir?', 'Qiymət tarixdən, məkandan, qonaq sayından və seçdiyiniz proqramdan asılıdır. WhatsApp-a yazın və ya saytda tarix seçin — paketi və dəqiq qiyməti dəqiqləşdirək.'),
 ('Səs, işıq və dekor paketə daxildir?', 'Toy və korporativ paketlərə səs və işıq daxildir, dekor və foto-video da paketdə var. Hamısı bir komandadan — ayrı-ayrı podratçı axtarmağa ehtiyac yoxdur.'),
 ('Tarixi necə bron etmək olar?', 'Saytda «Tarix seç» düyməsi ilə və ya WhatsApp vasitəsilə: tarix, məkan və tədbir növünü yazın, sizinlə əlaqə saxlayaq.'),
]

CSS = '''<style>
.svx{max-width:1180px;margin:0;padding-top:24px;display:grid;grid-template-columns:minmax(0,1fr) 380px;grid-template-rows:auto 1fr;grid-template-areas:"a v" "b v";column-gap:64px;align-items:start}
.sva{grid-area:a}.svb{grid-area:b}.svv{grid-area:v}
.svx h1{font:900 clamp(34px,4.4vw,58px)/1.04 var(--d);letter-spacing:-.035em;margin:18px 0 18px;text-wrap:balance}
.svx h1 em,.svx h2 em{font-style:normal;color:var(--red2)}
.svx .lead{font-size:20px;line-height:1.6;color:#e2e2e8;margin:0 0 30px;max-width:560px}
.svx h2{font:700 22px/1.3 var(--d);margin:0 0 14px}
.svp .tx{max-width:760px;margin:0}
.svbt{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.svv{position:sticky;top:96px;width:100%;border-radius:24px;overflow:hidden;background:#000;aspect-ratio:9/16;box-shadow:0 30px 80px rgba(227,18,43,.18)}
@media(max-width:900px){.svx{grid-template-columns:1fr;grid-template-areas:"a" "v" "b"}.svv{position:static;width:min(420px,100%);margin:0 auto 30px}.svx .lead{margin-bottom:24px}}
.svv video{width:100%;height:100%;object-fit:cover;display:block}
.inc{list-style:none;padding:0;margin:0 0 10px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.inc li{background:var(--card,#16161c);border:1px solid var(--line,#26262e);border-radius:16px;padding:14px 16px;font-weight:600}
.inc li:before{content:"✓ ";color:var(--red2)}
.faq details{border-bottom:1px solid var(--line,#26262e);padding:14px 0}
.faq summary{cursor:pointer;font-weight:600;color:var(--fg)}
.faq p{margin:10px 0 0}
.svl{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}
@media(max-width:600px){.inc{grid-template-columns:1fr}}
</style>'''


def links(rel, cur=''):
    names = {'toy': 'Toy və nişan', 'korporativ': 'Korporativ', 'ad-gunu': 'Ad günü və party', 'son-zeng': 'Party'}
    return '<div class="svl">' + ''.join(f'<a class="btn o sm" href="{rel}{s}/">{n}</a>' for s, n in names.items() if s != cur) + '</div>'


def page(p):
    rel = '../'
    url = f'{SITE}/{p["slug"]}/'
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Service', 'name': re.sub('<[^>]+>', '', p['h1']), 'description': p['desc'], 'url': url,
         'areaServed': {'@type': 'City', 'name': 'Bakı'}, 'image': f'{SITE}/{p["img"].replace(".webp", ".jpg")}',
         'provider': {'@type': 'EntertainmentBusiness', 'name': 'Showband Group', 'url': SITE + '/', 'telephone': '+994556118787'}},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Ana səhifə', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': re.sub('<[^>]+>', '', p['h1']), 'item': url}]}]}
    extra = CSS + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    wa = WA + p['wa'].replace(' ', '%20')
    plain = re.sub('<[^>]+>', '', p['h1'])
    body = ''.join(f'<h2>{E(h)}</h2><p>{E(t)}</p>' for h, t in p['about'])
    return head(f'{p["title"]} | Showband Group', p['desc'], url, rel, 'website', extra,
                p['img'].replace('.webp', '.jpg')).replace('<a class="on" href="../xeberler/">', '<a href="../xeberler/">') + f'''
 <nav class="bc" aria-label="breadcrumb"><a href="{rel}">Ana səhifə</a><span>›</span><em>{E(plain)}</em></nav>
 <article class="svp">
  <div class="svx">
   <div class="sva">
    <span class="chip">Showband Group · Bakı</span>
    <h1>{p["h1"]}</h1>
    <p class="lead">{E(p["lead"])}</p>
   </div>
   <div class="svv"><video controls playsinline preload="none" poster="{rel}video/ev_{p["video"]}_hd.jpg" src="{rel}video/ev_{p["video"]}.mp4" aria-label="{E(plain)} — video"></video></div>
   <div class="svb">
    <h2>Paketə nə daxildir</h2>
    <ul class="inc">{"".join(f"<li>{E(i)}</li>" for i in p["inc"])}</ul>
    <div class="svbt"><a class="btn" href="{rel}#bron">Tarix seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
   </div>
  </div>
  <div class="tx">
   {body}
   <p>{E(p["venues"])}</p>
   <h2>Tez-tez verilən suallar</h2>
   <div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in FAQ)}</div>
   <h2>Digər xidmətlər</h2>
   {links(rel, p["slug"])}
  </div>
 </article>
 <aside class="cta">
  <div><span class="k">Showband Group</span><h2>Tarixinizi <em>bron</em> edin</h2><p>Tarix, məkan və tədbir növünü yazın — paketi və qiyməti dəqiqləşdirək.</p></div>
  <div class="cb"><a class="btn" href="{rel}#bron">Tarix seç</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </aside>
''' + foot(rel)


def build():
    for p in PAGES: w(f'{p["slug"]}/index.html', page(p))
    return [p['slug'] for p in PAGES]
