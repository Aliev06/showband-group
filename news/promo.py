#!/usr/bin/env python3
"""Showband Group — promo Reels (yalnız Instagram Reels, saytda post yoxdur).
Fon: müştərinin öz canlı videosu (video/ev_<k>.mp4) + öz səsi. Üstündə xəbər üslubunda başlıq.
Növlər:
  news    — XƏBƏR üslubu (mövcud kart, reels.py): «Showband ... etdi — siz də istəyirsinizsə yazın»
  event   — YENİ üslub, canlı video fonda: «Bu həftə səhnədə»: tədbirdən canlı kadr + başlıq
  review  — «Rəy»: Google rəyi kartı, 5 ulduz
  season  — mövsüm/tarix: «Dekabr korporativləri — tarixlər dolur»
İstifadə: python3 news/promo.py <event|review|season> [k] [out_dir]
"""
import json, os, re, sys, random, subprocess
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import reels as R
import videos as V

W, H, FPS, TOTAL, OUT_AT = 1080, 1920, 30, 10.0, 7.6
F, WHITE, MUTE, RED = R.F, R.WHITE, R.MUTE, R.RED
LABEL = {'toy': 'Toy', 'korp': 'Korporativ', 'adgunu': 'Ad günü', 'party': 'Party', 'acilis': 'Toy açılışı', 'diger': 'Səhnədə'}


def reviews():
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r"var RV=\[\n(.*?)\n\];", s, re.S)
    return [{'u': u, 't': t} for u, t in re.findall(r"\{u:'([^']*)',t:'([^']*)'\}", m.group(1))]


def chip(d, x, y, txt, fill=RED, col=WHITE, size=30):
    f = F('montserrat-600', size); tw = d.textlength(txt, font=f)
    d.rounded_rectangle((x, y, x + tw + 44, y + size + 30), radius=(size + 30) // 2, fill=fill)
    d.text((x + 22, y + 13), txt, font=f, fill=col); return x + tw + 44


def shade(top=True):
    """yuxarı/aşağı qaraltma — mətn oxunsun"""
    g = Image.linear_gradient('L').resize((W, H))
    a = g.point(lambda v: int(max(0, 1 - v / 255 / .42) * 210)) if top else g.point(lambda v: int(max(0, (v / 255 - .55) / .45) * 230))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); L.putalpha(a); return L


def header(d, sub):
    av = R.logo(150); return av, sub


def layer_event(c):
    L = shade(True); d = ImageDraw.Draw(L)
    x = chip(d, 70, 170, 'CANLI · SHOWBAND', RED); chip(d, x + 14, 170, R.up(LABEL.get(c['e'], 'Tədbir')), (255, 255, 255, 40))
    tf, tl = R.fit(d, c['n'], 'unbounded-900', 74, W - 140, 3)
    y = 260
    for l in tl: d.text((70, y), l, font=tf, fill=WHITE); y += int(tf.size * 1.18)
    d.text((70, y + 14), 'Bu həftə səhnədə — Showband Group', font=F('montserrat-500', 34), fill=(230, 230, 236))
    L.alpha_composite(shade(False))
    lg = R.logo(260); L.alpha_composite(lg, (W - 260 - 60, H - lg.height - 90))
    return L


def layer_review(rv, c):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 90)); d = ImageDraw.Draw(L)
    cw = W - 140; tf, tl = R.fit(d, '«' + rv['t'] + '»', 'montserrat-600', 52, cw - 100, 6, 36)
    ch = 230 + len(tl) * int(tf.size * 1.4) + 110
    C = Image.new('RGBA', (cw, ch)); cd = ImageDraw.Draw(C)
    cd.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=44, fill=(18, 18, 22, 235), outline=(255, 255, 255, 40), width=2)
    import math
    for j in range(5):  # 5 ulduz (şriftdə ★ yoxdur — çəkirik)
        cx, cy, r1, r2 = 84 + j * 70, 86, 32, 13
        cd.polygon([(cx + (r1 if q % 2 == 0 else r2) * math.cos(math.pi / 2 + q * math.pi / 5), cy - (r1 if q % 2 == 0 else r2) * math.sin(math.pi / 2 + q * math.pi / 5)) for q in range(10)], fill=(255, 196, 0))
    cd.text((50, 140), 'Google rəyi', font=F('montserrat-500', 32), fill=MUTE)
    y = 210
    for l in tl: cd.text((50, y), l, font=tf, fill=WHITE); y += int(tf.size * 1.4)
    cd.text((50, y + 30), '— ' + rv['u'], font=F('unbounded-700', 34), fill=WHITE)
    L.alpha_composite(C, (70, (H - ch) // 2 - 60))
    chip(d, 70, 170, 'MÜŞTƏRİLƏR NƏ DEYİR', RED)
    lg = R.logo(260); L.alpha_composite(lg, (W - 260 - 60, H - lg.height - 90))
    return L


def layer_season(s, c):
    L = shade(True); d = ImageDraw.Draw(L)
    chip(d, 70, 170, s['chip'], RED)
    y = 270; tf = F('unbounded-900', s.get('size', 96))
    for l in s['title']: d.text((70, y), l, font=tf, fill=WHITE); y += int(tf.size * 1.15)
    tf2, tl2 = R.fit(d, s['sub'], 'montserrat-600', 40, W - 140, 3, 30)
    for l in tl2: d.text((70, y + 20), l, font=tf2, fill=(235, 235, 240)); y += int(tf2.size * 1.4)
    L.alpha_composite(shade(False))
    lg = R.logo(260); L.alpha_composite(lg, (W - 260 - 60, H - lg.height - 90))
    return L


SEASONS = [
    {'chip': 'DEKABR · KORPORATİV', 'title': ['Dekabr', 'tarixləri', 'dolur'], 'sub': 'Yeni il korporativiniz üçün tarixi indi bron edin — DJ, showman, canlı band.'},
    {'chip': 'TOY MÖVSÜMÜ', 'title': ['Toyunuz', 'üçün tarix', 'seçin'], 'sub': 'Showman, canlı band, fleşmob və ssenari — hamısı bir komandada.'},
]


# xəbər üslubu (mövcud kart dizaynı): «Showband ... etdi — siz də istəyirsinizsə»
NEWS = {
    'toy': ('{place} toyunda Showband Group səhnəni alovlandırdı', 'Showman, canlı band və fleşmob — qonaqlar gecəni unutmayacaq. Toyunuzda da belə olsun?'),
    'korp': ('{place}: Showband Group korporativ gecəni şouya çevirdi', 'DJ, showman və müsabiqələr — komanda ruhu üçün ən yaxşı gecə. Korporativiniz üçün yazın.'),
    'adgunu': ('{place}-da ad günü: Showband Group sürprizlərlə gəldi', 'DJ, showman, lazer şou — ad gününüz də belə yadda qalsın.'),
    'party': ('{place}: Showband Group ilə gecə səhərə qədər davam etdi', 'Party, son zəng, məzun gecəsi — Showband enerjisi ilə.'),
    'acilis': ('Toy açılışı: Showband Group xüsusi ssenari ilə qonaqları heyran etdi', 'Fərdi ssenari, işıq və musiqi — toyunuzun ilk dəqiqəsi möhtəşəm olsun.'),
    'diger': ('{place}: Showband Group səhnədə', 'Canlı ifa, showman və DJ — tədbiriniz üçün yazın.'),
}


def news_render(c, out_dir):
    import datetime
    place = c['n'].split('·')[-1].strip() if '·' in c['n'] else c['n']
    t, cap = NEWS.get(c['e'], NEWS['diger'])
    img = next((f'video/ev_{c["k"]}{x}.jpg' for x in ('_hd', '') if os.path.exists(os.path.join(ROOT, f'video/ev_{c["k"]}{x}.jpg'))), None)
    p = {'slug': f'promo-news-{c["k"]}', 'title': t.format(place=place), 'category': 'Showband', 'date': datetime.date.today().isoformat(),
         'image': img, 'description': cap, 'reel': {'caption': cap}, 'mode': 'event'}
    R.render(p, out_dir)
    return {'slug': p['slug'], 'mp4': os.path.join(out_dir, p['slug'] + '.mp4'), 'caption': p['title'] + ' 🎉\n' + cap}


def video_frames(path, start, dur):
    cmd = ['ffmpeg', '-loglevel', 'error', '-ss', f'{start:.2f}', '-t', f'{dur}', '-i', path,
           '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE); n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield Image.frombytes('RGB', (W, H), b)


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]))


def render(kind, k=None, out_dir=None, seed=None):
    rnd = random.Random(seed)
    cl = [c for c in V.clips() if not c['w']]
    c = next((x for x in cl if x['k'] == k), None) or rnd.choice(cl)
    if kind == 'news': return news_render(c, out_dir or os.path.join(HERE, 'out'))
    src = os.path.join(ROOT, 'video', f'ev_{c["k"]}.mp4')
    if kind == 'event': ov = layer_event(c); slug = f'promo-event-{c["k"]}'; cap = f'{c["n"]} 🎉\nBu həftə səhnədə — Showband Group.'
    elif kind == 'review':
        rv = rnd.choice([r for r in reviews() if len(r['t']) > 30] or reviews()); ov = layer_review(rv, c); slug = f'promo-review-{c["k"]}'; cap = f'«{rv["t"]}» — {rv["u"]} ⭐️⭐️⭐️⭐️⭐️\nRəyiniz üçün təşəkkür edirik!'
    else:
        s = SEASONS[0] if c['e'] == 'korp' else SEASONS[1] if c['e'] in ('toy', 'acilis') else rnd.choice(SEASONS); ov = layer_season(s, c); slug = f'promo-season-{c["k"]}'; cap = ' '.join(s['title']) + ' 📅\n' + s['sub']
    outro = R.outro_layer('event')
    d = duration(src); start = max(0., min(d - TOTAL - .2, d * .3))
    out_dir = out_dir or os.path.join(HERE, 'out'); os.makedirs(out_dir, exist_ok=True)
    mp4 = os.path.join(out_dir, slug + '.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', f'{start:.2f}', '-t', f'{TOTAL}', '-i', src, '-map', '0:v', '-map', '1:a?',
                            '-af', f'afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1}:d=1', '-t', f'{TOTAL}',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                            '-movflags', '+faststart', mp4], stdin=subprocess.PIPE)
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 170))
    for i, fr in enumerate(video_frames(src, start, TOTAL)):
        t = i / FPS; im = fr.convert('RGBA')
        if t < OUT_AT:
            k1 = R.ease((t - .3) / .6); R.blend(im, ov, k1 * (1 - R.ease((t - (OUT_AT - .4)) / .4)), 0, int(40 * (1 - k1)))
        else:
            k2 = R.ease((t - OUT_AT) / .5); R.blend(im, dark, k2); R.blend(im, outro, k2, 0, int(40 * (1 - k2)))
        im = im.convert('RGB')
        if i == int(3 * FPS): im.save(os.path.join(out_dir, slug + '.jpg'), quality=90)
        enc.stdin.write(im.tobytes())
    enc.stdin.close(); enc.wait()
    tags = '#showbandgroup #bakı #toy #şou #canlımusiqi #dj #showman'
    cap += '\n\nTədbirinizi biz təşkil edək — Direct-ə yazın 📩\n' + tags
    print('ok:', mp4); return {'slug': slug, 'mp4': mp4, 'caption': cap}


if __name__ == '__main__':
    a = sys.argv[1:]
    r = render(a[0] if a else 'event', a[1] if len(a) > 1 and a[1] != '-' else None, a[2] if len(a) > 2 else None)
    print(r['caption'])
