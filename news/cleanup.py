"""Showband bot — köhnə media fayllarını silir ki, repo və sayt böyüməsin.

- Paylaşılmış / ləğv edilmiş / silinmiş qaralamaların news/out/ fayllarını (mp4, jpg, json, img) silir.
- Instagram-a artıq paylaşılmış (ig_status=done) və ya saytdan silinmiş Reels-in reels/<slug>.mp4 faylını silir.
Gözləyən (pending) qaralamalara və Instagram növbəsində/xətada olanlara toxunmur.
"""
import glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def rm(path):
    if os.path.exists(path):
        os.remove(path); return 1
    return 0


def main():
    n = 0
    for f in glob.glob(os.path.join(HERE, 'drafts', '*.json')):
        try:
            with open(f, encoding='utf-8') as fh: d = json.load(fh)
        except Exception:
            continue
        slug, st = d.get('slug'), d.get('status')
        if not slug or st not in ('published', 'rejected', 'deleted'): continue
        for ext in ('.mp4', '.jpg', '.json'):
            n += rm(os.path.join(HERE, 'out', slug + ext))
        n += rm(os.path.join(HERE, 'out', 'img', slug + '.jpg'))
        if st == 'deleted' or d.get('ig_status') == 'done':
            n += rm(os.path.join(ROOT, 'reels', slug + '.mp4'))
    print('təmizləndi:', n, 'fayl')


if __name__ == '__main__':
    main()
