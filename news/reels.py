#!/usr/bin/env python3
"""Showband Group — xəbərdən Instagram Reels hazırlayır (üslub C: xəbər kartı).
İstifadə (sayt qovluğundan):
  python3 news/reels.py <slug>      # bir xəbər
  python3 news/reels.py --all       # bütün xəbərlər
Nəticə: news/out/<slug>.mp4, news/out/<slug>.jpg (örtük)

Xəbərdə istifadə olunan sahələr:
  title, category, date            — kartda
  reel.caption                     — kartın altındakı qısa mətn (yoxdursa: description)
  image                            — şəkil yolu (sayt qovluğuna nisbətən), yoxdursa səhnə fonu
Musiqi: news/music/ qovluğundakı mahnılar növbə ilə istifadə olunur (news/music/state.json).
  Konkret an üçün news/music/starts.json: {"mahni.mp3": 47.0}
  Qovluq boşdursa video səssiz qalır.
"""
import json, os, re, sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_news as B

W, H, FPS, TOTAL, OUT_AT = 1080, 1920, 30, 9.0, 7.2
MX, CW = 90, 1080 - 140
RED, WHITE, MUTE = (227, 18, 43), (255, 255, 255), (160, 160, 170)
MUSIC = os.path.join(HERE, 'music')
F = lambda n, s: ImageFont.truetype(os.path.join(HERE, 'fonts', n + '.ttf'), s)
LOGO = Image.open(os.path.join(ROOT, 'img', 'logo.png')).convert('RGBA')
SITE_HOST = re.sub(r'^https?://', '', B.SITE).rstrip('/')
AY = B.AY


def logo(w): return LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
def up(t): return t.replace('i', 'İ').replace('ı', 'I').upper()  # Azərbaycan dili: i→İ, ı→I
def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def back(x): x = max(0., min(1., x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width or not cur: cur = t
        else: out.append(cur); cur = w
    return out + ([cur] if cur else [])


def fit(d, text, name, size, width, max_lines, min_size=40):
    while True:
        f = F(name, size); ls = wrap(d, text, f, width)
        if len(ls) <= max_lines or size <= min_size: return f, ls[:max_lines]
        size -= 3


# ---------- səhnə fonu ----------
def beam(col, w=520, h=2300):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).polygon([(w * .44, 0), (w * .56, 0), (w, h), (0, h)], fill=150)
    m = m.filter(ImageFilter.GaussianBlur(18))
    m = Image.composite(m, Image.new('L', (w, h), 0), Image.linear_gradient('L').resize((w, h)).point(lambda v: 255 - int(v * .85)))
    s = Image.new('RGBA', (w, h), (*col, 0)); s.putalpha(m); return s


def stage(seed=7, base=(18, 6, 10), top=(70, 8, 18)):
    im = Image.new('RGBA', (W, H))
    im.paste(Image.composite(Image.new('RGB', (W, H), base), Image.new('RGB', (W, H), top), Image.linear_gradient('L').resize((W, H))))
    for col, x0, ang in [((255, 255, 255), 150, -16), ((255, 70, 90), 540, 8), ((255, 255, 255), 930, 20)]:
        b = beam(col).rotate(ang, resample=Image.BICUBIC, expand=True, center=(260, 0))
        im.paste(b, (int(x0 - b.width / 2), -120), b)
    d = ImageDraw.Draw(im); random.seed(seed)
    for i in range(26):
        x = i * 46 - 20 + (i % 3) * 8; hh = 150 + random.randint(0, 110); r = 26 + random.randint(0, 10)
        d.ellipse((x, H - hh - r * 2, x + r * 2, H - hh), fill=(5, 4, 6, 255))
        d.rounded_rectangle((x - 18, H - hh - 6, x + r * 2 + 18, H), radius=30, fill=(5, 4, 6, 255))
        if i % 6 == 2: d.line((x + r, H - hh, x + r + 30, H - hh - 200), fill=(5, 4, 6, 255), width=22)
    return im


def cover_crop(img, w, h):
    s = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 3
    return img.crop((x, y, x + w, y + h))


def fdate(p): return B.fdate(p['date'])


def photo(p):
    """Xəbərin şəkli: lokal 'image' və ya mənbədən 'source_image' (news/out/img/ qovluğuna yüklənir)."""
    if p.get('image') and os.path.exists(os.path.join(ROOT, p['image'])):
        return Image.open(os.path.join(ROOT, p['image'])).convert('RGB')
    url = p.get('source_image')
    if not url: return None
    import urllib.request
    fn = os.path.join(HERE, 'out', 'img', p['slug'] + '.jpg')
    try:
        if not os.path.exists(fn):
            os.makedirs(os.path.dirname(fn), exist_ok=True)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': (p.get('source') or {}).get('url', '')})
            with urllib.request.urlopen(req, timeout=30) as r: open(fn, 'wb').write(r.read())
        im = Image.open(fn).convert('RGB')
        return im if min(im.size) >= 300 else None
    except Exception as e:
        print('  ! şəkil yüklənmədi:', e); return None


# ---------- kart ----------
def make_card(p):
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    tf, tl = fit(tmp, p['title'], 'unbounded-900', 66, CW - 90, 4)
    lh = int(tf.size * 1.2)
    iw = CW - 88; ih = int(iw * .62)
    ch = 190 + lh * len(tl) + 20 + ih + 44
    C = Image.new('RGBA', (CW, ch)); d = ImageDraw.Draw(C)
    d.rounded_rectangle((0, 0, CW - 1, ch - 1), radius=44, fill=(20, 20, 24, 255), outline=(255, 255, 255, 30), width=2)
    av = Image.new('RGBA', (96, 96)); ImageDraw.Draw(av).ellipse((0, 0, 95, 95), fill=(10, 10, 12)); lg = logo(80)
    av.alpha_composite(lg, (8, 48 - lg.height // 2)); C.alpha_composite(av, (44, 44))
    nf = F('unbounded-700', 34); d.text((160, 52), 'Showband Group', font=nf, fill=WHITE)
    x = 160 + d.textlength('Showband Group', font=nf) + 14
    d.ellipse((x, 60, x + 32, 92), fill=(56, 151, 240)); d.line((x + 9, 76, x + 14, 82, x + 23, 69), fill=WHITE, width=4)
    d.text((160, 100), f'Musiqi xəbərləri · {fdate(p)}', font=F('montserrat-500', 28), fill=MUTE)
    y = 190
    for l in tl: d.text((44, y), l, font=tf, fill=WHITE); y += lh
    y += 20
    ph = p.get('_photo')
    img = cover_crop(ph, iw, ih) if ph else cover_crop(stage(seed=len(p['slug'])).convert('RGB'), iw, ih)
    m = Image.new('L', (iw, ih), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, iw, ih), radius=28, fill=255)
    C.paste(img, (44, y), m)
    cf = F('montserrat-600', 26); tg = up(p['category']); tw = d.textlength(tg, font=cf)
    d.rounded_rectangle((70, y + 26, 70 + tw + 40, y + 76), radius=25, fill=RED); d.text((90, y + 36), tg, font=cf, fill=WHITE)
    if ph and (p.get('source') or {}).get('name'):
        cr = 'Foto: ' + p['source']['name']; crf = F('montserrat-500', 22); cw2 = d.textlength(cr, font=crf)
        d.rounded_rectangle((CW - 44 - cw2 - 36, y + ih - 50, CW - 44 - 12, y + ih - 14), radius=18, fill=(0, 0, 0, 150))
        d.text((CW - 44 - cw2 - 24, y + ih - 45), cr, font=crf, fill=(255, 255, 255, 220))
    return C


def caption_layer(p, top):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    txt = (p.get('reel') or {}).get('caption') or p['description']
    f, ls = fit(d, txt, 'montserrat-600', 44, W - 2 * MX, 3, 34)
    for i, l in enumerate(ls): d.text((MX, top + i * int(f.size * 1.4)), l, font=f, fill=WHITE)
    return L


def outro_layer():
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    L.alpha_composite(logo(560), ((W - 560) // 2, 700))
    ft = F('unbounded-700', 50); s = 'Ətraflı — saytda'
    d.text(((W - d.textlength(s, font=ft)) / 2, 940), s, font=ft, fill=WHITE)
    pf = F('montserrat-600', 40); tw = d.textlength(SITE_HOST, font=pf); x = (W - tw) / 2
    d.rounded_rectangle((x - 40, 1040, x + tw + 40, 1130), radius=45, fill=RED); d.text((x, 1062), SITE_HOST, font=pf, fill=WHITE)
    return L


def blend(base, layer, a, dx=0, dy=0):
    if a <= 0: return
    if a < 1: layer = layer.copy(); layer.putalpha(layer.getchannel('A').point(lambda v: int(v * a)))
    base.paste(layer, (dx, dy), layer) if dx < 0 or dy < 0 else base.alpha_composite(layer, (dx, dy))


# ---------- musiqi ----------
def next_track():
    if not os.path.isdir(MUSIC): return None, 0.0
    tracks = sorted(f for f in os.listdir(MUSIC) if f.lower().endswith(('.mp3', '.m4a', '.wav', '.aac', '.ogg', '.flac')))
    if not tracks: return None, 0.0
    sp = os.path.join(MUSIC, 'state.json')
    st = json.load(open(sp)) if os.path.exists(sp) else {'last': -1}
    i = (st.get('last', -1) + 1) % len(tracks)
    json.dump({'last': i, 'track': tracks[i]}, open(sp, 'w'))
    starts = os.path.join(MUSIC, 'starts.json')
    manual = json.load(open(starts, encoding='utf-8')) if os.path.exists(starts) else {}
    path = os.path.join(MUSIC, tracks[i])
    return path, float(manual[tracks[i]]) if tracks[i] in manual else best_start(path)


def best_start(path, win=TOTAL):
    """Mahnının ən enerjili 9 saniyəsini (adətən nəqarət) tapır."""
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32)
    if len(a) < 8000 * (win + 2): return 0.0
    e = (a[: len(a) // 800 * 800].reshape(-1, 800) ** 2).mean(1)      # 0.1 san bloklar
    rms = np.sqrt(np.convolve(e, np.ones(int(win * 10)) / (win * 10), 'valid'))
    n = len(rms); lo, hi = int(n * .15), int(n * .85)  # intro və sonluğu keç
    return float((lo + int(np.argmax(rms[lo:hi]))) / 10)


# ---------- render ----------
def render(p, out_dir):
    p = dict(p); p['_photo'] = photo(p)
    card = make_card(p)
    cy = max(240, (1480 - card.height) // 2)
    cap = caption_layer(p, cy + card.height + 50)
    outro = outro_layer()
    if p['_photo']:  # fon: xəbərin şəkli, bulanıq və tünd
        bg = cover_crop(p['_photo'], W, H).filter(ImageFilter.GaussianBlur(45)).convert('RGBA'); bg.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 150)))
    else:
        bg = stage(seed=3).filter(ImageFilter.GaussianBlur(40)); bg.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 120)))

    def frame(t):
        im = bg.copy()
        if t < OUT_AT:
            a = 1 - ease((t - (OUT_AT - .4)) / .4)
            k = back(t / .6); s = .86 + .14 * min(1, k) + .025 * (t / OUT_AT)
            c = card.resize((int(card.width * s), int(card.height * s)), Image.BICUBIC)
            blend(im, c, a * min(1, k * 1.4), (W - c.width) // 2, cy + int(card.height * (1 - s) / 2) + int(80 * (1 - min(1, k))))
            kc = ease((t - 2.2) / .5); blend(im, cap, a * kc, 0, int(30 * (1 - kc)))
        else:
            k = ease((t - OUT_AT) / .5); blend(im, outro, k, 0, int(40 * (1 - k)))
        return im.convert('RGB')

    os.makedirs(out_dir, exist_ok=True)
    mp4 = os.path.join(out_dir, p['slug'] + '.mp4')
    track, ss = next_track()
    if track:
        ain = ['-ss', f'{ss:.2f}', '-t', f'{TOTAL}', '-i', track]
        af = ['-af', f'loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.6,afade=t=out:st={TOTAL - 1.2}:d=1.2,aresample=48000']
    else:
        ain = ['-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000']; af = []
    cmd = (['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
           + ain + ['-map', '0:v', '-map', '1:a'] + af +
           ['-t', f'{TOTAL}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
            '-c:a', 'aac', '-b:a', '128k', '-ac', '2', '-movflags', '+faststart', mp4])
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)):
        fr = frame(i / FPS)
        if i == int(3.0 * FPS): fr.save(os.path.join(out_dir, p['slug'] + '.jpg'), quality=90)
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    meta = {'slug': p['slug'], 'video': mp4, 'track': os.path.basename(track) if track else None, 'start': round(ss, 1)}
    json.dump(meta, open(os.path.join(out_dir, p['slug'] + '.json'), 'w'), ensure_ascii=False)
    print('ok:', mp4, '| musiqi:', meta['track'] or 'yoxdur', f'@{ss:.1f}s' if track else '')
    return meta


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else '--all'
    if arg.endswith('.json'): todo = [json.load(open(arg, encoding='utf-8'))]   # qaralama faylı
    else: todo = B.POSTS if arg == '--all' else [p for p in B.POSTS if p['slug'] == arg]
    if not todo: sys.exit('xəbər tapılmadı: ' + arg)
    for p in todo: render(p, os.path.join(HERE, 'out'))
