"""Paket səhifələri: /paket/<slug>/ — hər paketin ətraflı təsviri (mənbə: müştərinin PDF paketləri, 22.11.2026).
Ana səhifədəki kartlar (index.html → var PK) qısa təsvir + qiymət + «Ətraflı» düyməsi ilə buraya aparır.
Qiymət dəyişəndə HƏM burada, HƏM index.html-dəki PK massivində dəyişin.
"""
import json
from build_news import head, foot, SITE, CFG, E, w
from paketler_i18n import T, UI

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
.ah{position:relative;margin:0 calc(50% - 50vw);min-height:min(86vh,760px);display:flex;align-items:flex-end;overflow:hidden}
.ah img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 30%}
.ah:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,11,14,.15) 0%,rgba(11,11,14,.35) 45%,var(--bg) 100%),linear-gradient(90deg,rgba(11,11,14,.85),rgba(11,11,14,0) 70%)}
.ahi{position:relative;z-index:2;width:min(1180px,100% - 40px);margin:0 auto;padding:0 0 56px}
.ahi .chip{background:rgba(227,18,43,.18);border-color:rgba(255,74,92,.5)}
.ahi h1{font:900 clamp(44px,7vw,96px)/.95 var(--d);letter-spacing:-.04em;margin:16px 0 18px;max-width:900px;text-wrap:balance}
.ahi p{font-size:19px;line-height:1.6;color:#e7e7ec;max-width:640px;margin:0 0 28px}
.arow{display:flex;flex-wrap:wrap;align-items:center;gap:14px 26px}
.apr{font:900 40px var(--d)}.apr s{font-size:22px;opacity:.45;margin-right:8px}.apr small{font-size:20px}
.adur{color:var(--mute);font-size:15px;border-left:1px solid var(--line);padding-left:20px}
.abt{display:flex;gap:12px}.abt .btn{padding:16px 26px;font-size:16px}
.asec{padding:70px 0 10px}
.asec h2{font:800 clamp(28px,3.4vw,44px)/1.1 var(--d);letter-spacing:-.03em;margin:0 0 30px}.asec h2 em{font-style:normal;color:var(--red2)}
.agrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.ac{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:24px;transition:transform .3s,border-color .3s}
.ac:hover{transform:translateY(-4px);border-color:rgba(255,74,92,.45)}
.ac .ic{width:48px;height:48px;border-radius:14px;background:rgba(227,18,43,.14);color:var(--red2);display:grid;place-items:center;margin-bottom:16px}.ac .ic svg{width:24px;height:24px}
.ac b{display:block;font:700 17px/1.3 var(--s)}.ac p{margin:8px 0 0;color:var(--mute);font-size:14.5px;line-height:1.55}
.aex{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.aex div{background:var(--card);border-radius:18px;padding:18px;border:1px solid var(--line)}.aex b{display:block;font-weight:700;font-size:14.5px}.aex span{display:block;margin-top:8px;color:var(--red2);font:800 17px var(--d)}
.anote{color:var(--mute);font-size:14px;line-height:1.6;max-width:820px;margin-top:22px}
.aoth{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
.aoth a{position:relative;border-radius:18px;overflow:hidden;aspect-ratio:4/3;display:flex;align-items:flex-end;padding:16px;color:#fff;text-decoration:none}
.aoth a img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .5s}.aoth a:hover img{transform:scale(1.05)}
.aoth a:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,.85))}
.aoth a span{position:relative;z-index:1;font:800 17px/1.15 var(--d)}.aoth a small{display:block;font:600 13px var(--s);color:var(--red2);margin-top:4px}
.abar{display:none}.abar s,.aoth s{margin-right:6px;opacity:.55;font-size:.8em}
@media(max-width:900px){.agrid{grid-template-columns:1fr 1fr}.aex{grid-template-columns:1fr 1fr}.aoth{grid-template-columns:1fr 1fr}.ah{min-height:78vh}.abt{display:none}
 .abar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:60;gap:12px;align-items:center;justify-content:space-between;padding:12px 16px calc(12px + env(safe-area-inset-bottom));background:rgba(11,11,14,.92);backdrop-filter:blur(14px);border-top:1px solid var(--line)}
 .abar b{font:900 22px var(--d)}.abar small{display:block;color:var(--mute);font:500 12px var(--s)}.abar .btn{padding:14px 22px}
 .sticky{display:none!important}}
@media(max-width:560px){.agrid{grid-template-columns:1fr}.adur{border:0;padding:0}}
.aoth s{margin-right:6px;opacity:.6}</style>'''

ICON = {
 'mic': '<path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M8 21h8"/>',
 'spk': '<rect x="6" y="3" width="12" height="18" rx="2"/><circle cx="12" cy="14" r="3.2"/><circle cx="12" cy="7.5" r="1.3"/>',
 'note': '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
 'drum': '<ellipse cx="12" cy="8" rx="8" ry="3"/><path d="M4 8v8c0 1.7 3.6 3 8 3s8-1.3 8-3V8M8 3l3 4M16 3l-3 4"/>',
 'star': '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
 'disc': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="M12 3a9 9 0 0 1 9 9"/>',
 'spark': '<path d="M12 2v6M12 16v6M2 12h6M16 12h6M5 5l4 4M15 15l4 4M19 5l-4 4M9 15l-4 4"/>',
 'doc': '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 12h7M9 16h7"/>',
 'film': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 5v14M17 5v14M3 9h4M3 15h4M17 9h4M17 15h4"/>',
 'gift': '<rect x="3" y="8" width="18" height="13" rx="1"/><path d="M12 8v13M3 12h18M12 8c-2-4-6-4-6-1s6 1 6 1zM12 8c2-4 6-4 6-1s-6 1-6 1z"/>',
}
def icon_for(t):
    t = t.lower()
    for k, ic in (('səs', 'spk'), ('texniki', 'spk'), ('aparıcı', 'mic'), ('müğənni', 'mic'), ('tar', 'note'), ('qarşılanma', 'note'), ('ritm', 'drum'), ('perkussiya', 'drum'),
                  ('band', 'star'), ('dj', 'disc'), ('disko', 'spark'), ('effekt', 'spark'), ('çubuq', 'spark'), ('ssenari', 'doc'), ('hazırlıq', 'doc'), ('rəsmi', 'doc'),
                  ('film', 'film'), ('hədiyyə', 'gift'), ('interaktiv', 'star'), ('repertuar', 'note'), ('giriş', 'star'), ('açılış', 'film'), ('rekvizit', 'spark')):
        if k in t: return ICON[ic]
    return ICON['star']
svg = lambda t: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{icon_for(t)}</svg>'



from i18n_site import LANGS, pre, localize


def price_html(p, lang='az'):
    o = f'<s>{p["old"]}</s>' if p.get('old') else ''
    if not p.get('from'): return f'{o}{p["price"]} AZN'
    if lang == 'az': return f'{o}{p["price"]} AZN<small>-dən</small>'
    return f'<small>{UI[lang]["from_pre"]}</small>{o}{p["price"]} AZN'


def loc(p, lang):
    """Paketin həmin dildə versiyası (ikonlar üçün AZ başlıqlar 'az_items'-də qalır)."""
    q = dict(p, az_items=p['items'])
    if lang != 'az': q.update(T[lang][p['id']])
    return q


def page(p0, lang='az'):
    p = loc(p0, lang)
    rel = '../../' if lang == 'az' else '../../../'
    url = f'{SITE}/{pre(lang)}paket/{p["slug"]}/'
    u = UI.get(lang)
    fr = (('-dən' if lang == 'az' else '') if p.get('from') else '')
    title = (f'{p["name"]} — {"" if lang == "az" or not p.get("from") else u["from_pre"]}{p["price"]} AZN{fr} | Showband Group')
    home, pkn = ('Ana səhifə', 'Paketlər') if lang == 'az' else (u['home'], u['pk'])
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Service', 'name': p['name'], 'description': p['desc'], 'url': url, 'image': f'{SITE}/img/{p["img"]}.webp',
         'inLanguage': lang, 'areaServed': {'@type': 'City', 'name': 'Bakı'},
         'provider': {'@type': 'EntertainmentBusiness', 'name': 'Showband Group', 'url': SITE + '/', 'telephone': '+994556118787'},
         'offers': {'@type': 'Offer', 'price': p['price'], 'priceCurrency': 'AZN', 'url': url,
                    **({'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': p['price'], 'priceCurrency': 'AZN'}} if p.get('from') else {})}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': home, 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': pkn, 'item': SITE + '/#paket'},
            {'@type': 'ListItem', 'position': 3, 'name': p['name'], 'item': url}]}]}
    extra = CSS + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    wmsg = (f'Salam! «{p["name"]}» paketi ilə maraqlanıram.' if lang == 'az' else u['wa'].format(p['name']))
    wa = WA + wmsg.replace(' ', '%20')
    book = 'Rezerv et' if lang == 'az' else u['book']
    bron = f'{rel}?pk={p["id"]}#bron'
    others = ''.join(f'<a href="../{o["slug"]}/"><img src="{rel}img/{o["img"]}.webp" alt="" loading="lazy"><span>{E(loc(o, lang)["name"])}<small>{price_html(o, lang)}</small></span></a>' for o in P if o is not p0)
    items = ''.join(f'<div class="ac"><div class="ic">{svg(ta)}</div><b>{E(t)}</b><p>{E(d)}</p></div>' for (t, d), (ta, _) in zip(p['items'], p['az_items']))
    extra_p = ''.join(f'<p class="anote">• {E(x)}</p>' for x in p['extra'])
    if lang == 'az':
        h_dur, h_inc, h_ex, h_oth, note, pdf = 'Müddət', 'Paketə nə <em>daxildir</em>', 'Əlavə <em>xidmətlər</em>', 'Digər <em>paketlər</em>', NOTE, '📄 Bütün paketlər — PDF kataloq'
        exl = EXTRAS
    else:
        h_dur, h_inc, h_ex, h_oth, note, pdf = u['dur'], u['inc'], u['extras'], u['others'], u['note'], u['pdf']
        exl = [(n, v if 'AZN' in v else u['agree']) for n, (_, v) in zip(u['extras_list'], EXTRAS)]
    hd = head(title, p['desc'][:155], url, rel, 'website', extra, f'img/{p["img"]}.webp').replace(
        f'<a class="on" href="{rel}xeberler/">', f'<a href="{rel}xeberler/">').replace(
        f'<a href="{rel}#paket">', f'<a class="on" href="{rel}#paket">', 1)
    body = f'''
 <section class="ah"><img src="{rel}img/{p["img"]}.webp" alt="{E(p["name"])} — Showband Group" width="1600" height="1000">
  <div class="ahi"><span class="chip">{E(p["eb"])}</span><h1>{E(p["name"])}</h1><p>{E(p["desc"])}</p>
   <div class="arow"><span class="apr">{price_html(p, lang)}</span><span class="adur">{h_dur}: {E(p["dur"])}</span>
   <div class="abt"><a class="btn" href="{bron}">{book}</a><a class="btn o" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div></div></div></section>
 <section class="asec"><h2>{h_inc}</h2><div class="agrid">{items}</div>{extra_p}</section>
 <section class="asec"><h2>{h_ex}</h2><div class="aex">{"".join(f"<div><b>{E(a)}</b><span>{E(b)}</span></div>" for a, b in exl)}</div>
  <p class="anote">{E(note)}</p><p class="anote"><a href="{rel}{PDF}" target="_blank" rel="noopener" style="color:var(--red2)">{pdf}</a></p></section>
 <section class="asec" style="padding-bottom:70px"><h2>{h_oth}</h2><div class="aoth">{others}</div></section>
 <div class="abar"><div><small>{E(p["name"])}</small><b>{price_html(p, lang)}</b></div><a class="btn" href="{bron}">{book}</a></div>
'''
    return localize(hd + body + foot(rel), lang, rel, f'paket/{p["slug"]}/')


def build():
    out = []
    for lang in LANGS:
        for p in P:
            w(f'{pre(lang)}paket/{p["slug"]}/index.html', page(p, lang)); out.append(f'{pre(lang)}paket/{p["slug"]}')
    return out


if __name__ == '__main__':
    print(build())
