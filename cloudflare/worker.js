// Showband Group — Telegram düymələri üçün ani webhook.
// Telegram düyməyə basılan kimi bu Worker cavab verir və GitHub-da paylaşımı dərhal başladır.
// Cloudflare → Worker → Settings → Variables and Secrets:
//   TG_TOKEN  — Telegram bot tokeni
//   CHAT_ID   — 1029301688
//   GH_TOKEN  — GitHub fine-grained token (yalnız showband-group, Contents: Read and write)
//   SECRET    — istənilən uzun söz (webhook qorunması üçün)
const REPO = 'Aliev06/showband-group';

export default {
  async fetch(req, env) {
    if (req.method !== 'POST') return new Response('ok');
    if (req.headers.get('X-Telegram-Bot-Api-Secret-Token') !== env.SECRET) return new Response('forbidden', { status: 403 });
    const u = await req.json();
    const q = u.callback_query;
    if (!q || String(q.message?.chat?.id) !== String(env.CHAT_ID)) return new Response('ok');
    const tg = (m, b) => fetch(`https://api.telegram.org/bot${env.TG_TOKEN}/${m}`, {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(b) });
    const ok = q.data.startsWith('ok:');
    const r = await fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
      method: 'POST',
      headers: { authorization: `Bearer ${env.GH_TOKEN}`, accept: 'application/vnd.github+json',
                 'user-agent': 'showband-bot', 'content-type': 'application/json' },
      body: JSON.stringify({ event_type: 'tg', client_payload: { data: q.data, message_id: q.message.message_id,
        chat_id: q.message.chat.id, video: !!q.message.video } }) });
    await tg('answerCallbackQuery', { callback_query_id: q.id,
      text: r.ok ? (ok ? '⏳ Paylaşılır… 1-2 dəqiqə' : 'Ləğv edilir…') : '⚠️ GitHub xətası: ' + r.status });
    return new Response('ok');
  }
};
