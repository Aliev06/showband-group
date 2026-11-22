"""Paket səhifələri: /paket/<slug>/ — hər paketin ətraflı təsviri (mənbə: müştərinin PDF paketləri, 22.11.2026).
Ana səhifədəki kartlar (index.html → var PK) qısa təsvir + qiymət + «Ətraflı» düyməsi ilə buraya aparır.
Qiymət dəyişəndə HƏM burada, HƏM index.html-dəki PK massivində dəyişin.
"""
import json
from build_news import head, foot, SITE, CFG, E, w

WA = f'https://wa.me/{CFG["whatsapp"]}?text='
PDF = 'files/Showband_Paketler_2026.pdf'
NOTE = ('Qiymətlər yalnız Bakı şəhəri daxilində keçirilən tədbirlər üçündür. Bölgələr, rayonlar və xarici ölkələr üçün, '
        'özəl bayram günlərində, otellərdə və bəzi restoranlarda qiymət dəyişə bilər. Xaricdə də çıxış edirik — istənilən ölkəyə uçuruq.')

# id — index.html-dəki PK id-si (forma üçün); price — rəqəm; from — «-dən»; old — köhnə (üstündən xətt)
P = [
 {'id': 'toydisko', 'slug': 'toy-disko', 'img': 'pk_toydisko', 'eb': 'Toy şou paketi', 'name': 'Toy Disko',
  'price': 600, 'dur': '1 saat',
  'desc': 'Toyunuzun ən enerjili saatını biz idarə edirik: işıqlı geyimdə DJ, canlı perkussiya, flashmob və şou effektləri ilə 1 saatlıq disko şou.',
  'items': [('DJ işıqlı (LED) geyimdə', 'Bütün disko proqramını aparır.'),
            ('Canlı perkussiya solisti', 'İşıqlı geyimdə, DJ-in yanında darbuka, davul və afro alətlərində canlı ifa.'),
            ('Qarışıq repertuar', 'Dünya hitləri, müasir və modern mahnılar, 70-ci, 80-ci, 90-cı illərin sevilən mahnıları, disko mahnıları və halay bölməsi.'),
            ('İnteraktiv şou', 'Qonaqlarla birlikdə flashmob, mahnıların qonaqlarla birgə ifası.'),
            ('Şou effektləri', '2 ədəd pul atan tapança və 2 ədəd konfetti (feyerverk) tapançası — bəy və gəlinə 1-1 ədəd.'),
            ('İşıqlı çubuqlar', 'Flashmob üçün — bəy, gəlin və müəyyən sayda qonaq üçün.')],
  'extra': ['100 AZN əlavə ödənişlə 1 ədəd tüstü tapançası sifariş edə bilərsiniz.']},
 {'id': 'mega', 'slug': 'mega-disco-show', 'img': 'pk_mega', 'eb': 'Kombo şou paketi', 'name': 'Mega Disco Show',
  'price': 800, 'old': 1000, 'dur': '≈ 1 saat 25 dəqiqə',
  'desc': 'Band + Toy Disko bir paketdə: canlı instrumental band ilə başlayır, işıqlı disko ilə zirvəyə çatır. Ayrı-ayrılıqda 1000 AZN.',
  'items': [('Showband Instrumental Band · 20–25 dəq', '3 solist canlı instrumental ifa edir; solistlər işıqlı geyim və eynəklərdə.'),
            ('Band effektləri', 'Feyerverk tapançası (əl qığılcım effekti) və pul yağışı effekti (əl tapançası).'),
            ('Ardınca: Toy Disko · 1 saat', 'DJ işıqlı (LED) geyimdə + canlı perkussiya solisti (darbuka, davul, afro alətləri).'),
            ('Qarışıq repertuar', 'Dünya hitləri, müasir mahnılar, 70-80-90-cı illərin sevilən mahnıları, disko və halay.'),
            ('İnteraktiv şou', 'Qonaqlarla birlikdə flashmob və mahnıların birgə ifası.'),
            ('Disko effektləri', '2 pul atan + 2 konfetti tapançası (bəy və gəlinə 1-1), flashmob üçün işıqlı çubuqlar.'),
            ('Hədiyyə', '1 ədəd tüstü tapançası paketə daxildir.')],
  'extra': []},
 {'id': 'kino', 'slug': 'kino-acilis', 'img': 'pk_kino', 'eb': 'Toy paketi', 'name': 'Kino Açılış',
  'price': 1000, 'from': True, 'dur': 'Toyun açılışı',
  'desc': 'Toyunuz köhnə filmlərin sehrli dünyası ilə açılsın! Sevdiyimiz film obrazları toyunuzda canlanır — hər açılış bəy və gəlinin hekayəsinə uyğun xüsusi ssenari ilə qurulur.',
  'items': [('Xüsusi yazılmış ssenari', 'Açılış toyun havasına və ab-havasına uyğun dəyişir, buna görə hər toy fərqli olur.'),
            ('Köhnə film obrazları ilə açılış', 'Xanım və bəylərdən ibarət rəqs girişi qrupu.'),
            ('Köhnə ritm + müasir ritm', 'DJ Orxan Abbasov köhnə film musiqilərini müasir remix ilə təqdim edir: Amantello, Sehrli xalat, Dərviş Parisi partladır və digərləri.'),
            ('Canlı ritm alətləri', 'Afro təbilləri, nağara, darbuka — ifaçılar işıqlı geyimlərdə, DJ qara işıqlı geyimdə.'),
            ('Bəy və gəlinin möhtəşəm girişi', 'Girişdə əl fişəng tapançaları + 1 ədəd RGB işıqlı əl tüstü tapançası (rəngi salonun dizaynına uyğun).'),
            ('Açılışı siz seçirsiniz', 'Əvvəl açılış, ardınca bəy və gəlin — və ya əvvəl bəy və gəlin daxil olub əyləşir, sonra açılış başlayır.')],
  'extra': ['Qiymət ssenaridən, rəqs qrupunun tərkibindən və iştirakçıların sayından asılı olaraq dəyişə bilər.']},
 {'id': 'nisan', 'slug': 'nisan', 'img': 'pk_nisan', 'eb': 'Tədbirin tam idarəsi', 'name': 'Nişan paketi',
  'price': 1500, 'dur': 'Tədbir boyu',
  'desc': 'Hamısı bir paketdə: canlı musiqi, müğənni, DJ, konkurslar və oyunlar, Showband, diskoteka, halay və yallı — nişanınızı əvvəldən sona qədər biz aparırıq.',
  'items': [('Səs sistemi', 'Kalonkalar, mikrofonlar və bütün səs avadanlığı.'),
            ('Aparıcı', 'Tədbiri əvvəldən sona aparır, rəsmi hissəni elan edir, konkurslar, oyunlar və təqdimatlar keçirir; nişana özəl ssenari yazır, bəy və gəlin üçün xüsusi giriş.'),
            ('Tar ifası', 'Qonaqlar yemək yeyərkən fonda yüngül, həzin mahnılar.'),
            ('Müğənni və canlı musiqiçilər', 'Müğənni 4 canlı alət ifaçısı ilə birlikdə gəlir — tədbirdə canlı musiqi səslənir.'),
            ('Ritm alətləri (perkussiya)', 'Popurilərdə canlı nağara, darbuka və afro alətləri — tədbirin əvvəlindən sonuna qədər.'),
            ('Showband instrumental qrup · 20–25 dəq', 'İşıqlı geyimlərlə instrumental mahnılar; pul atan və feyerverk tapançaları.'),
            ('DJ', 'Giriş, şou və tort mahnıları; milli popurilər, halaylar və yallılar.'),
            ('Diskoteka · 1 saat', 'Pul atan, feyerverk və tüstü tapançaları ilə.')],
  'extra': []},
 {'id': 'adgunu', 'slug': 'ad-gunu', 'img': 'pk_adgunu', 'eb': 'Tədbirin tam idarəsi', 'name': 'Ad günü paketi',
  'price': 1000, 'dur': 'Tədbir boyu',
  'desc': 'Ad gününüzü əvvəldən sona qədər biz aparırıq — aparıcı, tar, canlı ritm, Showband, DJ və 1 saatlıq diskoteka bir komandada.',
  'items': [('Səs sistemi', 'Kalonkalar, mikrofonlar və bütün səs avadanlığı.'),
            ('Aparıcı', 'Tədbiri əvvəldən sona aparır, rəsmi hissəni elan edir, konkurslar, oyunlar və təqdimatlar keçirir; günün ssenarisini yazır.'),
            ('Tar ifası', 'Qonaqlar yemək yeyərkən fonda yüngül, həzin mahnılar.'),
            ('Ritm alətləri (perkussiya)', 'Popurilərdə canlı nağara, darbuka və afro alətləri — tədbirin əvvəlindən sonuna qədər.'),
            ('Showband instrumental qrup · 20–25 dəq', 'İşıqlı geyimlərlə instrumental mahnılar; pul atan və feyerverk tapançaları.'),
            ('DJ', 'Giriş, şou və tort mahnıları; milli popurilər, halaylar və yallılar.'),
            ('Diskoteka · 1 saat', 'Pul atan, feyerverk və tüstü tapançaları ilə.')],
  'extra': ['Müğənni əlavə etmək olar — qiyməti ayrıca razılaşdırılır.']},
 {'id': 'mezun', 'slug': 'mezun-gecesi', 'img': 'pk_mezun', 'eb': 'Son zəng · məzun gecələri', 'name': 'Məzun gecəsi və Party',
  'price': 1000, 'from': True, 'dur': 'Tədbir boyu',
  'desc': 'Son zəng, məzun gecəsi və party üçün özəl ssenari, showman aparıcı, Showband və işıqlı full diskoteka — gecə yadda qalsın!',
  'items': [('Səs sistemi', 'Kalonkalar, mikrofonlar və bütün səs avadanlığı.'),
            ('Ssenarinin qurulması', 'Məzun gecəsi və party üçün özəl ssenari, tədbirin gedişatı əvvəlcədən planlaşdırılır.'),
            ('Aparıcı-showman', 'Tədbiri idarə edir, əyləncəli konkurslar və oyunlar keçirir; disko vaxtı işıqlı geyimdə.'),
            ('DJ', 'Tədbirin əvvəlindən sonuna qədər, qarışıq repertuar; disko vaxtı işıqlı geyimdə.'),
            ('Showband instrumental qrup · 20–25 dəq', 'İşıqlı geyimlərlə instrumental mahnılar.'),
            ('Full diskoteka · 1 saat', 'Qarışıq repertuar, konkurslar və oyunlar; pul atan, feyerverk və tüstü tapançaları daxil.')],
  'extra': ['Gitarist qrup, müğənni və rəqs qrupları əlavə ödənişlə dəvət oluna bilər.']},
 {'id': 'korp', 'slug': 'korporativ', 'img': 'pk_korp', 'eb': 'Hər şey daxil', 'name': 'Korporativ paket',
  'price': 2000, 'dur': 'Tədbir boyu · gedişat daxil',
  'desc': 'Şirkət korporativləri üçün hazırlıqdan diskotekaya qədər tam əyləncə paketi — bütün komanda, şou proqramlar, texniki təminat və gedişat daxil. Əlavə ödəniş yoxdur.',
  'items': [('Hazırlıq mərhələsi', 'İlkin görüş, ssenarinin hazırlanması, şirkətin sahəsinə uyğun suallar və viktorinalar, tərtibat və texniki plan.'),
            ('Qarşılanma', 'Tar ifaçısı həzin, retro və instrumental mahnılarla qonaqları qarşılayır.'),
            ('Rəsmi hissə', 'Aparıcı (MC) tədbiri açır; uğurlar, yekunlar və təbriklər üçün rəhbərliyə söz verilir.'),
            ('Əyləncəli interaktivlər', 'Şirkətə aid oyunlar və konkurslar, qaliblərə hədiyyələr.'),
            ('Müğənni-gitarist', 'Geniş repertuarla canlı mahnı proqramı.'),
            ('Show band · 20–25 dəq', 'Ud, saksafon, baraban və darbuka — işıqlı geyimlərdə xüsusi şou.'),
            ('Ritm ansamblı', 'Nağara, afro, zərb alətləri və davul — bütün tədbir boyu canlı müşayiət.'),
            ('Full diskoteka · 1 saat', 'Müasir və milli rəqslər, yallılar və halaylar; işıqlı geyimlər, flashmob çubuqları, işıqlı eynəklər.'),
            ('Texniki təminat', 'Peşəkar səs sistemi (6 kalonka, 2 mikrofon), quraşdırma və sökülmə, komandanın və avadanlığın gedişatı.')],
  'extra': []},
 {'id': 'band', 'slug': 'instrumental-band', 'img': 'pk_band', 'eb': 'Canlı musiqi · şou', 'name': 'Instrumental Band',
  'price': 300, 'from': True, 'dur': '25–40 dəqiqə',
  'desc': 'İşıqlı geyimlərdə 3 solistin canlı instrumental şousu — istənilən tədbirə ayrıca sifariş edilə bilər. İstəsəniz DJ ilə birlikdə.',
  'items': [('Əsas paket — 300 AZN', 'Çıxış müddəti 25 dəqiqə, 3 solist; işıqlı geyim və eynəklər, feyerverk tapançası (əl qığılcım effekti), pul yağışı effekti.'),
            ('Band + DJ — 500 AZN', 'Əvvəl band 20–25 dəq, ardınca DJ 15 dəq; DJ-in çıxışı üçün 1 ədəd əl tüstü tapançası. Əsas paketdəki hər şey daxildir. Ümumi müddət ≈ 35–40 dəq.'),
            ('Rekvizitlər', 'İşıqlı geyimlər, işıqlı eynəklər, feyerverk tapançası, pul yağışı, tüstü tapançası (DJ ilə).')],
  'extra': []},
]

EXTRAS = [('İşıqlı eynəklər və flashmob çubuqları', '100 AZN'), ('Reels maker (videoqraf)', '200 AZN'),
          ('Müğənni', 'razılaşma ilə'), ('Gitarist qrup', 'razılaşma ilə'), ('Rəqs qrupları', 'razılaşma ilə')]

CSS = '''<style>
.pkx{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:56px;align-items:start;padding-top:24px}
.pkimg{border-radius:28px;overflow:hidden;aspect-ratio:1;position:sticky;top:96px;box-shadow:0 30px 80px rgba(227,18,43,.18)}
.pkimg img{width:100%;height:100%;object-fit:cover;display:block}
.pkx h1{font:900 clamp(34px,4.6vw,60px)/1.02 var(--d);letter-spacing:-.035em;margin:14px 0 16px;text-wrap:balance}
.pkx .lead{font-size:19px;line-height:1.6;color:#e2e2e8;margin:0 0 24px}
.pkpr{display:flex;flex-wrap:wrap;gap:12px 28px;align-items:baseline;padding:18px 22px;border-radius:20px;background:var(--card,#16161c);border:1px solid var(--line,#26262e);margin-bottom:22px}
.pkpr b{font:900 34px var(--d);color:var(--fg)}.pkpr b s{font-size:20px;opacity:.45;margin-right:8px}.pkpr b small{font-size:18px}
.pkpr span{color:var(--mut,#a9a9b3);font-size:15px}
.pkbt{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:34px}
.pkx h2{font:700 22px/1.3 var(--d);margin:0 0 14px}
.pkl{list-style:none;padding:0;margin:0 0 28px;display:grid;gap:10px}
.pkl li{display:grid;grid-template-columns:34px minmax(0,1fr);gap:12px;background:var(--card,#16161c);border:1px solid var(--line,#26262e);border-radius:16px;padding:14px 16px}
.pkl li i{width:34px;height:34px;border-radius:50%;background:rgba(227,18,43,.14);color:var(--red2);font:800 14px/34px var(--d);text-align:center;font-style:normal}
.pkl b{display:block;font-weight:700}.pkl p{margin:4px 0 0;color:var(--mut,#a9a9b3);font-size:15px;line-height:1.55}
.pkex{margin:0 0 28px;padding:0;list-style:none;display:grid;gap:8px}.pkex li{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid var(--line,#26262e);padding:10px 0}.pkex li span{color:var(--red2);font-weight:700;white-space:nowrap}
.pknote{color:var(--mut,#a9a9b3);font-size:14px;line-height:1.6}
.pko{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
@media(max-width:900px){.pkx{grid-template-columns:1fr;gap:28px}.pkimg{position:static;max-width:480px}}
</style>'''


def price_html(p):
    o = f'<s>{p["old"]}</s>' if p.get('old') else ''
    return f'{o}{p["price"]} AZN' + ('<small>-dən</small>' if p.get('from') else '')


def page(p):
    rel = '../../'
    url = f'{SITE}/paket/{p["slug"]}/'
    title = f'{p["name"]} — {p["price"]} AZN{"-dən" if p.get("from") else ""} | Showband Group'
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Service', 'name': p['name'], 'description': p['desc'], 'url': url, 'image': f'{SITE}/img/{p["img"]}.webp',
         'areaServed': {'@type': 'City', 'name': 'Bakı'},
         'provider': {'@type': 'EntertainmentBusiness', 'name': 'Showband Group', 'url': SITE + '/', 'telephone': '+994556118787'},
         'offers': {'@type': 'Offer', 'price': p['price'], 'priceCurrency': 'AZN', 'url': url,
                    **({'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': p['price'], 'priceCurrency': 'AZN'}} if p.get('from') else {})}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Ana səhifə', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Paketlər', 'item': SITE + '/#paket'},
            {'@type': 'ListItem', 'position': 3, 'name': p['name'], 'item': url}]}]}
    extra = CSS + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    wa = WA + (f'Salam! «{p["name"]}» paketi ilə maraqlanıram.').replace(' ', '%20')
    others = ''.join(f'<a class="btn o sm" href="../{o["slug"]}/">{E(o["name"])}</a>' for o in P if o is not p)
    items = ''.join(f'<li><i>{i}</i><div><b>{E(t)}</b><p>{E(d)}</p></div></li>' for i, (t, d) in enumerate(p['items'], 1))
    extra_p = ''.join(f'<p class="pknote">• {E(x)}</p>' for x in p['extra'])
    return head(title, p['desc'][:155], url, rel, 'website', extra, f'img/{p["img"]}.webp').replace(
        '<a class="on" href="../../xeberler/">', '<a href="../../xeberler/">').replace(
        '<a href="../../#paket">', '<a class="on" href="../../#paket">', 1) + f'''
 <nav class="bc" aria-label="breadcrumb"><a href="{rel}">Ana səhifə</a><span>›</span><a href="{rel}#paket">Paketlər</a><span>›</span><em>{E(p["name"])}</em></nav>
 <article class="svp">
  <div class="pkx">
   <div class="pkimg"><img src="{rel}img/{p["img"]}.webp" alt="{E(p["name"])} — Showband Group" width="720" height="720"></div>
   <div>
    <span class="chip">{E(p["eb"])}</span>
    <h1>{E(p["name"])}</h1>
    <p class="lead">{E(p["desc"])}</p>
    <div class="pkpr"><b>{price_html(p)}</b><span>Müddət: {E(p["dur"])}</span></div>
    <div class="pkbt"><a class="btn" href="{rel}?pk={p["id"]}#bron">Rezerv et</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
    <h2>Paketə nə daxildir</h2>
    <ul class="pkl">{items}</ul>
    {extra_p}
    <h2 style="margin-top:28px">Əlavə xidmətlər</h2>
    <ul class="pkex">{"".join(f"<li>{E(a)}<span>{E(b)}</span></li>" for a, b in EXTRAS)}</ul>
    <p class="pknote">{E(NOTE)}</p>
    <p class="pknote"><a href="{rel}{PDF}" target="_blank" rel="noopener" style="color:var(--red2)">📄 Bütün paketlər — PDF kataloq</a></p>
    <h2 style="margin-top:28px">Digər paketlər</h2>
    <div class="pko">{others}</div>
   </div>
  </div>
 </article>
 <aside class="cta">
  <div><span class="k">Showband Group</span><h2>Tarixinizi <em>bron</em> edin</h2><p>Tarix, məkan və qonaq sayını yazın — paketi və ssenarini birlikdə seçək.</p></div>
  <div class="cb"><a class="btn" href="{rel}?pk={p["id"]}#bron">Rezerv et</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div>
 </aside>
''' + foot(rel)


def build():
    for p in P: w(f'paket/{p["slug"]}/index.html', page(p))
    return [f'paket/{p["slug"]}' for p in P]


if __name__ == '__main__':
    print(build())
