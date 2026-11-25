"""Alt səhifələrin (paketlər, xidmətlər, videolar) RU / EN versiyaları üçün ümumi köməkçilər.
AZ: /<yol>/   RU: /ru/<yol>/   EN: /en/<yol>/"""
import re
from build_news import SITE

LANGS = ('az', 'ru', 'en')
LOC = {'az': 'az_AZ', 'ru': 'ru_RU', 'en': 'en_US'}
NAV_AZ = ['Xidmətlər', 'Paketlər', 'Videolar', 'Komanda', 'Rəylər', 'Xəbərlər', 'Əlaqə']
UI = {
 'ru': {'nav': ['Услуги', 'Пакеты', 'Видео', 'Команда', 'Отзывы', 'Новости', 'Контакты'], 'date': 'Выбрать дату',
        'foot': 'Живая музыка и шоу для свадеб, помолвок, дней рождения и корпоративов. Баку.',
        'foot2': ['Свадьба и помолвка', 'Корпоратив', 'День рождения'], 'foot3': ['Главная', 'Новости', 'Бронь'], 'home': 'Главная',
        'cta_h': 'Забронируйте <em>дату</em>', 'cta_p': 'Напишите дату, место и тип мероприятия — уточним пакет и цену.'},
 'en': {'nav': ['Services', 'Packages', 'Videos', 'Team', 'Reviews', 'News', 'Contact'], 'date': 'Pick a date',
        'foot': 'Live music and show for weddings, engagements, birthdays and corporate events. Baku.',
        'foot2': ['Weddings & engagements', 'Corporate', 'Birthday'], 'foot3': ['Home', 'News', 'Booking'], 'home': 'Home',
        'cta_h': 'Book your <em>date</em>', 'cta_p': 'Tell us the date, venue and type of event — we will confirm the package and price.'},
}


def pre(lang):
    return '' if lang == 'az' else lang + '/'


def rel_of(path, lang):
    """path: 'paket/nisan/' → səhifədən kökə nisbi yol."""
    return '../' * (path.count('/') + (0 if lang == 'az' else 1))


def localize(html, lang, rel, path):
    """head/foot AZ şablonunu dilə uyğunlaşdırır + AZ·RU·EN keçidi + hreflang."""
    alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}/{pre(l)}{path}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}/{path}">'
    html = re.sub(r'<link rel="alternate" hreflang="az" href="[^"]*">', alts, html, count=1)
    sw = '<div class="lsw">' + ''.join(
        f'<a href="{rel}{pre(l)}{path}"{" class=on" if l == lang else ""} hreflang="{l}">{l.upper()}</a>' for l in LANGS) + '</div>'
    css = ('<style>.lsw{display:flex;gap:2px;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px}'
           '.lsw a{font:700 12px var(--s);color:var(--mute);text-decoration:none;padding:7px 10px;border-radius:999px}'
           '.lsw a.on{background:var(--red);color:#fff}@media(max-width:640px){.lsw a{padding:6px 8px;font-size:11px}}</style>')
    html = html.replace('</head>', f"<script>try{{localStorage.setItem('sb_lang','{lang}')}}catch(e){{}}</script>\n</head>", 1)
    if lang == 'az': return html.replace('<div class="nr">', css + '<div class="nr">' + sw, 1)
    u = UI[lang]
    html = (html.replace('<html lang="az">', f'<html lang="{lang}">')
            .replace('<meta http-equiv="content-language" content="az">', f'<meta http-equiv="content-language" content="{lang}">')
            .replace('content="az_AZ"', f'content="{LOC[lang]}"'))
    for a, b in zip(NAV_AZ, u['nav']): html = html.replace(f'>{a}</a>', f'>{b}</a>')
    html = html.replace('>Tarix seç</a>', f'>{u["date"]}</a>').replace('aria-label="Menyu"', 'aria-label="Menu"')
    html = html.replace('Toy, nişan, ad günü və korporativ tədbirlər üçün canlı musiqi və şou. Bakı.', u['foot'])
    for a, b in zip(['Toy və nişan', 'Korporativ', 'Ad günü'], u['foot2']):
        html = html.replace(f'>{a}</a> ·', f'>{b}</a> ·').replace(f'>{a}</a></p>', f'>{b}</a></p>')
    for a, b in zip(['Ana səhifə', 'Xəbərlər', 'Bron'], u['foot3']): html = html.replace(f'>{a}</a>', f'>{b}</a>')
    html = html.replace('<h2>Tarixinizi <em>bron</em> edin</h2>', f'<h2>{u["cta_h"]}</h2>').replace(
        '<p>Tarix, məkan və tədbir növünü yazın — paketi və qiyməti dəqiqləşdirək.</p>', f'<p>{u["cta_p"]}</p>')
    # xidmət / video səhifələrinə linklər həmin dildə qalsın
    for s in ('toy/', 'korporativ/', 'ad-gunu/', 'videolar/', 'paket/'):
        html = html.replace(f'href="{rel}{s}', f'href="{rel}{pre(lang)}{s}')
    # ana səhifə linkləri seçilmiş dildə açılsın
    html = html.replace(f'href="{rel}#', f'href="{rel}?lang={lang}#').replace(f'href="{rel}"', f'href="{rel}?lang={lang}"')
    html = html.replace(f'href="{rel}?pk=', f'href="{rel}?lang={lang}&pk=')
    return html.replace('<div class="nr">', css + '<div class="nr">' + sw, 1)
