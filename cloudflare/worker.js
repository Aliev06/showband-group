// Showband Group — Telegram düymələri üçün ani webhook (v6).
// Cron Triggers: '0 6 * * *' → 10:00 hype, '0 13 * * *' → 17:00 tədbir (Bakı vaxtı)
// Secrets: TG_TOKEN, CHAT_ID, GH_TOKEN, SECRET
const REPO = 'Aliev06/showband-group';
const TXT = { ok: '⏳ Paylaşılır… 1-2 dəqiqə', no: 'Ləğv edilir…', rw: '✍️ Yenidən yazılır… ~1 dəqiqə',
  tt: '✏️ Yeni başlığı cavab olaraq yazın', dl: '🗑 Təsdiq gözlənilir', dy: '🗑 Silinir… ~1 dəqiqə', dn: 'Ləğv edildi', gt: '🔎 Yeni xəbər axtarılır… ~2 dəqiqə', ph: '🖼 Şəkilsiz hazırlanır… ~1 dəqiqə', nx: '🔄 Başqa xəbər axtarılır… ~2 dəqiqə' };

export default {
  async scheduled(ev, env) {
    const cmd = ev.cron === '0 13 * * *' ? 'tedbir' : 'yeni';
    await fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
      method: 'POST',
      headers: { authorization: `Bearer ${env.GH_TOKEN}`, accept: 'application/vnd.github+json',
                 'user-agent': 'showband-bot', 'content-type': 'application/json' },
      body: JSON.stringify({ event_type: 'tg', client_payload: { kind: 'cmd', cmd, chat_id: env.CHAT_ID } }) });
  },
  async fetch(req, env) {
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
