// Showband Group — Telegram düymələri üçün ani webhook (v10).
// Cron Triggers: '0 6 * * *' → 10:00 hype, '0 13 * * *' → 17:00 tədbir (Bakı vaxtı)
// Secrets: TG_TOKEN, CHAT_ID, GH_TOKEN, SECRET · D1 binding: DB (baxış sayğacı, /v)
const REPO = 'Aliev06/showband-group';
const TXT = { ok: '⏳ Paylaşılır… 1-2 dəqiqə', no: 'Ləğv edilir…', rw: '✍️ Yenidən yazılır… ~1 dəqiqə',
  tt: '✏️ Yeni başlığı cavab olaraq yazın', dl: '🗑 Təsdiq gözlənilir', dy: '🗑 Silinir… ~1 dəqiqə', dn: 'Ləğv edildi', gt: '🔎 Yeni xəbər axtarılır… ~2 dəqiqə', ph: '🖼 Şəkilsiz hazırlanır… ~1 dəqiqə', nx: '🔄 Başqa variant hazırlanır… ~2 dəqiqə',
  tx: '📝 Yeni mətni cavab olaraq yazın', pv: '🎬 Başqa video hazırlanır… ~1 dəqiqə' };

// 👁 Baxış sayğacı — yalnız real insanlar: sayt JS-i 10 san / scroll-dan sonra göndərir, botlar UA ilə süzülür,
// bir cihaz (IP+brauzer) bir xəbəri gündə 1 dəfə sayılır.
const ORIGINS = ['https://showbandgroup.az', 'https://www.showbandgroup.az'];
const BOT = /bot|crawl|spider|slurp|preview|fetch|curl|wget|python|axios|headless|lighthouse|facebookexternalhit|whatsapp|telegram|vkshare|semrush|ahrefs|bing|yandex|google|baidu|duckduck|petal|bytespider|gptbot|claude|openai|phantom|selenium|puppeteer|playwright/i;
let ready = false;
async function views(req, env) {
  const origin = req.headers.get('origin') || '';
  const cors = { 'access-control-allow-origin': ORIGINS.includes(origin) ? origin : ORIGINS[0],
                 'access-control-allow-methods': 'GET,POST', 'access-control-allow-headers': 'content-type',
                 'content-type': 'application/json', 'cache-control': 'no-store' };
  const out = (o) => new Response(JSON.stringify(o), { headers: cors });
  if (req.method === 'OPTIONS') return new Response(null, { headers: cors });
  if (!env.DB) return out({});
  if (!ready) {
    await env.DB.batch([env.DB.prepare('CREATE TABLE IF NOT EXISTS views (slug TEXT PRIMARY KEY, n INTEGER NOT NULL DEFAULT 0)'),
                        env.DB.prepare('CREATE TABLE IF NOT EXISTS seen (h TEXT PRIMARY KEY, d TEXT NOT NULL)')]);
    ready = true;
  }
  const ok = (x) => /^[a-z0-9-]{3,120}$/.test(x);
  if (req.method === 'GET') {
    const list = (new URL(req.url).searchParams.get('s') || '').split(',').filter(ok).slice(0, 60);
    if (!list.length) return out({});
    const r = await env.DB.prepare(`SELECT slug, n FROM views WHERE slug IN (${list.map(() => '?').join(',')})`).bind(...list).all();
    return out(Object.fromEntries(r.results.map((x) => [x.slug, x.n])));
  }
  if (req.method === 'POST') {
    const ua = req.headers.get('user-agent') || '';
    if (!ORIGINS.includes(origin) || ua.length < 20 || BOT.test(ua)) return out({ ok: 0 });
    let b = {}; try { b = await req.json(); } catch (e) {}
    if (!ok(b.s || '') || b.t < 3000) return out({ ok: 0 });
    const day = new Date().toISOString().slice(0, 10);
    const raw = new TextEncoder().encode([req.headers.get('cf-connecting-ip'), ua, b.s, day].join('|'));
    const h = [...new Uint8Array(await crypto.subtle.digest('SHA-256', raw))].map((x) => x.toString(16).padStart(2, '0')).join('');
    const ins = await env.DB.prepare('INSERT OR IGNORE INTO seen (h, d) VALUES (?, ?)').bind(h, day).run();
    if (ins.meta.changes) await env.DB.prepare('INSERT INTO views (slug, n) VALUES (?, 1) ON CONFLICT(slug) DO UPDATE SET n = n + 1').bind(b.s).run();
    return out({ ok: 1 });
  }
  return out({});
}

export default {
  async scheduled(ev, env) {
    if (env.DB) try { await env.DB.prepare("DELETE FROM seen WHERE d < date('now','-2 day')").run(); } catch (e) {}
    // hər saat :23 — Instagram növbəsi (GitHub schedule etibarsızdır)
    const igq = ev.cron === '23 * * * *';
    const cmd = ev.cron === '0 13 * * *' ? 'tedbir' : 'yeni';
    await fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
      method: 'POST',
      headers: { authorization: `Bearer ${env.GH_TOKEN}`, accept: 'application/vnd.github+json',
                 'user-agent': 'showband-bot', 'content-type': 'application/json' },
      body: JSON.stringify(igq ? { event_type: 'igq', client_payload: {} }
                               : { event_type: 'tg', client_payload: { kind: 'cmd', cmd, chat_id: env.CHAT_ID } }) });
  },
  async fetch(req, env) {
    if (new URL(req.url).pathname === '/v') return views(req, env);
    if (req.method !== 'POST') return new Response('ok');
    if (req.headers.get('X-Telegram-Bot-Api-Secret-Token') !== env.SECRET) return new Response('forbidden', { status: 403 });
    const u = await req.json();
    const gh = (payload) => fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
      method: 'POST',
      headers: { authorization: `Bearer ${env.GH_TOKEN}`, accept: 'application/vnd.github+json',
                 'user-agent': 'showband-bot', 'content-type': 'application/json' },
      body: JSON.stringify({ event_type: 'tg', client_payload: payload }) });
    const tg = (m, b) => fetch(`https://api.telegram.org/bot${env.TG_TOKEN}/${m}`, {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(b) });

    // ✏️ Başlığı dəyiş — botun sualına cavab
    const m = u.message;
    const cmd = m && String(m.chat.id) === String(env.CHAT_ID) && ((m.text || '').trim().match(/^\/(xeberler|yeni|tedbir)(@\w+)?$/i) || [])[1];
    if (cmd) {
      await gh({ kind: 'cmd', cmd: cmd.toLowerCase(), chat_id: m.chat.id });
      if (cmd.toLowerCase() !== 'xeberler') await tg('sendMessage', { chat_id: m.chat.id, text: '🔎 Yeni xəbər axtarılır… ~2 dəqiqə' });
      return new Response('ok');
    }
    // 🎛 Klaviatura düymələri (yazı sətrinin üstündə)
    const KEYS = { '⭐ Promo video': ['gt:p', '⭐ Promo video hazırlanır… ~1 dəqiqə'],
                   '📰 Xəbər': ['gt:n', '🔎 Yeni xəbər axtarılır… ~2 dəqiqə'],
                   '📋 Saytdakı xəbərlər': ['gt:l', null] };
    const key = m && String(m.chat.id) === String(env.CHAT_ID) && KEYS[(m.text || '').trim()];
    if (key) {
      const r = await gh({ data: key[0], message_id: m.message_id, chat_id: m.chat.id });
      if (!r.ok) await tg('sendMessage', { chat_id: m.chat.id, text: '⚠️ GitHub xətası: ' + r.status });
      else if (key[1]) await tg('sendMessage', { chat_id: m.chat.id, text: key[1] });
      return new Response('ok');
    }
    if (m && String(m.chat.id) === String(env.CHAT_ID) && m.text && m.reply_to_message?.from?.is_bot) {
      await gh({ kind: 'reply', text: m.text, reply_to: m.reply_to_message.message_id, chat_id: m.chat.id });
      return new Response('ok');
    }
    const q = u.callback_query;
    if (!q || String(q.message?.chat?.id) !== String(env.CHAT_ID)) return new Response('ok');
    const r = await gh({ data: q.data, message_id: q.message.message_id, chat_id: q.message.chat.id, video: !!q.message.video });
    await tg('answerCallbackQuery', { callback_query_id: q.id,
      text: r.ok ? (TXT[q.data.split(':')[0]] || 'OK') : '⚠️ GitHub xətası: ' + r.status });
    return new Response('ok');
  }
};
