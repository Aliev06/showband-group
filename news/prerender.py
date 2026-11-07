"""Ana səhifənin JS ilə qurulan bloklarını (xidmətlər, paketlər, kliplər, komanda, rəylər, addımlar, forma)
hazır HTML kimi index.html-ə yazır — Google, Yandex, Bing və AI axtarışları JS işlətmədən də bütün mətni görsün.

İş prinsipi: səhifəni brauzerdə (AZ dilində) açır, JS-in qurduğu HTML-i götürür və
<!--pre:ID-->…<!--/pre:ID--> markerləri arasına yazır. Brauzerdə JS yenə də işləyir (dil dəyişmək üçün).

İşlətmə: python3 news/prerender.py   (SV/PK/RV/TM/CL massivləri dəyişəndən sonra)
Tələb: pip install playwright && playwright install chromium (və ya hazır Chromium)
"""
import os, re, sys, threading, http.server, socketserver, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
IDS = ['svc', 'pl', 'alb', 'clips', 'team', 'rv', 'steps', 'ftype', 'fpk']


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Quiet, directory=ROOT)
    srv = socketserver.TCPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    from playwright.sync_api import sync_playwright
    src = open(INDEX, encoding='utf-8').read()
    # boş konteynerlərə marker qoy (ilk dəfə)
    for i in IDS:
        if f'<!--pre:{i}-->' in src: continue
        m = re.search(r'(<(div|select)\b[^>]*\bid="%s"[^>]*>)\s*(</\2>)' % i, src)
        if not m:
            print('  ! tapılmadı / boş deyil:', i); continue
        src = src[:m.start()] + m.group(1) + f'<!--pre:{i}--><!--/pre:{i}-->' + m.group(3) + src[m.end():]
    open(INDEX, 'w', encoding='utf-8').write(src)

    srv = serve()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 900})
        pg.route(re.compile(r'googletagmanager|workers\.dev|fonts\.g'), lambda r: r.fulfill(body='{}'))
        pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/index.html')
        pg.evaluate("try{localStorage.removeItem('sb_lang')}catch(e){}")
        pg.reload(); pg.wait_for_timeout(800)
        html = pg.evaluate("ids => { const o = {}; ids.forEach(i => { const e = document.getElementById(i); if (e) o[i] = e.innerHTML }); return o }", IDS)
        b.close()
    srv.shutdown()

    for i, h in html.items():
        a, z = f'<!--pre:{i}-->', f'<!--/pre:{i}-->'
        if a not in src: continue
        h = re.sub(r'<!--/?pre:[a-z]+-->', '', h)
        src = src[:src.index(a) + len(a)] + h + src[src.index(z):]
    open(INDEX, 'w', encoding='utf-8').write(src)
    print('prerender:', ', '.join(f'{k} {len(v)}' for k, v in html.items()))


if __name__ == '__main__':
    main()
