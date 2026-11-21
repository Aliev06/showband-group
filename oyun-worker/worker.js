// Showband Oyun — canlı viktorina (Kahoot üslubu) üçün Worker + Durable Object.
// Hər telefon bir WebSocket saxlayır; otaq (Durable Object) sualı hamıya eyni anda göndərir,
// cavab vaxtını SERVER ölçür, xalları hesablayır, lider cədvəlini paylayır.
// Secret: ADMIN_PIN · Binding: ROOM (Durable Object, class Room)

const ORIGINS = ['https://showbandgroup.az', 'https://www.showbandgroup.az'];
const MAX_PLAYERS = 400;

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === '/ws') {
      if (req.headers.get('upgrade') !== 'websocket') return new Response('websocket only', { status: 426 });
      const origin = req.headers.get('origin') || '';
      if (origin && !ORIGINS.includes(origin) && !env.DEV) return new Response('forbidden', { status: 403 });
      const id = env.ROOM.idFromName('main');
      return env.ROOM.get(id).fetch(req);
    }
    return new Response('Showband Oyun', { headers: { 'content-type': 'text/plain; charset=utf-8' } });
  },
};

const clean = (s, n) => String(s ?? '').replace(/[\u0000-\u001f<>]/g, '').trim().slice(0, n);

export class Room {
  constructor(ctx, env) {
    this.ctx = ctx; this.env = env;
    this.g = null;      // oyun vəziyyəti
    this.sets = null;   // sual dəstləri
    ctx.blockConcurrencyWhile(async () => {
      this.g = (await ctx.storage.get('g')) || this.fresh();
      this.sets = (await ctx.storage.get('sets')) || [];
    });
  }

  fresh() {
    return { phase: 'lobby', setId: null, qs: [], qi: -1, startAt: 0, endsAt: 0, players: {}, answers: {}, prevRank: {}, gameId: Date.now().toString(36) };
  }
  save() { return this.ctx.storage.put('g', this.g); }

  async fetch(req) {
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    const role = new URL(req.url).searchParams.get('role') === 'admin' ? 'admin' : 'player';
    this.ctx.acceptWebSocket(server, [role]);
    server.serializeAttachment({ role, pid: null, authed: false });
    return new Response(null, { status: 101, webSocket: client });
  }

  send(ws, o) { try { ws.send(JSON.stringify(o)); } catch (e) {} }
  socks(tag) { return this.ctx.getWebSockets(tag); }
  admins() { return this.socks('admin').filter((w) => (w.deserializeAttachment() || {}).authed); }

  // ---------- hesablamalar ----------
  ranking() {
    return Object.entries(this.g.players)
      .map(([id, p]) => ({ id, name: p.name, score: p.score, gain: p.gain || 0, streak: p.streak || 0 }))
      .sort((a, b) => b.score - a.score || a.name.localeCompare(b.name))
      .map((r, i) => ({ ...r, rank: i + 1, prev: this.g.prevRank[r.id] || null }));
  }
  publicQ() {
    const q = this.g.qs[this.g.qi];
    return { i: this.g.qi, total: this.g.qs.length, text: q.text, opts: q.opts, dur: q.dur };
  }
  counts() { return { players: Object.keys(this.g.players).length, answered: Object.keys(this.g.answers).length }; }

  stateFor(pid) {
    const g = this.g, base = { t: 'state', phase: g.phase, gameId: g.gameId, now: Date.now(), ...this.counts() };
    if (g.phase === 'q') Object.assign(base, { q: this.publicQ(), endsAt: g.endsAt, mine: pid && g.answers[pid] ? g.answers[pid].a : null });
    if (g.phase === 'reveal' || g.phase === 'final') Object.assign(base, this.result(pid));
    if (pid && g.players[pid]) base.me = { name: g.players[pid].name, score: g.players[pid].score };
    return base;
  }
  result(pid) {
    const g = this.g, q = g.qs[g.qi], rk = this.ranking(), me = pid ? rk.find((r) => r.id === pid) : null;
    const a = pid ? g.answers[pid] : null;
    return {
      q: q ? { i: g.qi, total: g.qs.length, text: q.text, opts: q.opts, correct: q.correct } : null,
      top: rk.slice(0, g.phase === 'final' ? 10 : 5).map(({ id, ...r }) => ({ ...r, me: id === pid })),
      mine: me ? { ...me, id: undefined, answered: !!a, ok: a ? a.ok : false, pick: a ? a.a : null } : null,
      n: rk.length,
    };
  }
  adminView() {
    const g = this.g, q = g.qs[g.qi];
    const dist = q ? q.opts.map((_, k) => Object.values(g.answers).filter((x) => x.a === k).length) : [];
    return { t: 'admin', phase: g.phase, gameId: g.gameId, setId: g.setId, now: Date.now(), endsAt: g.endsAt, ...this.counts(),
      q: q ? { i: g.qi, total: g.qs.length, text: q.text, opts: q.opts, correct: q.correct, dur: q.dur } : null, dist,
      board: this.ranking().map(({ id, ...r }) => r), sets: this.sets };
  }

  broadcastState() {
    for (const ws of this.socks('player')) this.send(ws, this.stateFor((ws.deserializeAttachment() || {}).pid));
    this.pushAdmin();
  }
  pushAdmin() { const v = this.adminView(); for (const ws of this.admins()) this.send(ws, v); }
  pushCounts() {
    const c = { t: 'count', ...this.counts() };
    for (const ws of this.socks('player')) this.send(ws, c);
    this.pushAdmin();
  }

  // ---------- oyun axını ----------
  async startQuestion() {
    const g = this.g;
    if (g.qi + 1 >= g.qs.length) return this.finish();
    g.prevRank = g.qi < 0 ? {} : Object.fromEntries(this.ranking().map((r) => [r.id, r.rank]));
    for (const p of Object.values(g.players)) p.gain = 0;
    g.qi += 1; g.answers = {}; g.phase = 'q';
    g.startAt = Date.now() + 600;                 // telefonlar sualı göstərməyə hazırlaşsın
    g.endsAt = g.startAt + g.qs[g.qi].dur * 1000;
    await this.save();
    await this.ctx.storage.setAlarm(g.endsAt + 150);
    this.broadcastState();
  }
  async closeQuestion() {
    const g = this.g; if (g.phase !== 'q') return;
    const q = g.qs[g.qi];
    for (const [id, p] of Object.entries(g.players)) {
      const a = g.answers[id];
      if (a && a.ok) {
        const el = Math.min(1, Math.max(0, (a.at - g.startAt) / (q.dur * 1000)));
        p.streak = (p.streak || 0) + 1;
        p.gain = Math.round(1000 * (1 - el / 2)) + (p.streak >= 3 ? 100 : 0);
      } else { p.streak = 0; p.gain = 0; }
      p.score += p.gain;
    }
    g.phase = 'reveal';
    await this.ctx.storage.deleteAlarm();
    await this.save();
    this.broadcastState();
  }
  async finish() { this.g.phase = 'final'; await this.save(); this.broadcastState(); }
  async alarm() { if (this.g.phase === 'q') await this.closeQuestion(); }

  // ---------- mesajlar ----------
  async webSocketMessage(ws, raw) {
    let m; try { m = JSON.parse(raw); } catch (e) { return; }
    const at = ws.deserializeAttachment() || {};
    if (m.t === 'ping') return this.send(ws, { t: 'pong', now: Date.now(), c: m.c });
    return at.role === 'admin' ? this.onAdmin(ws, at, m) : this.onPlayer(ws, at, m);
  }

  async onPlayer(ws, at, m) {
    const g = this.g;
    if (m.t === 'hello') {               // qayıdan oyunçu (internet kəsilib-gəlib)
      const pid = clean(m.id, 40);
      if (pid && g.players[pid] && m.gameId === g.gameId) { at.pid = pid; ws.serializeAttachment(at); }
      return this.send(ws, this.stateFor(at.pid));
    }
    if (m.t === 'join') {
      const pid = clean(m.id, 40), name = clean(m.name, 24);
      if (!pid || name.length < 2) return this.send(ws, { t: 'err', e: 'name' });
      if (!g.players[pid] && Object.keys(g.players).length >= MAX_PLAYERS) return this.send(ws, { t: 'err', e: 'full' });
      const taken = Object.entries(g.players).some(([id, p]) => id !== pid && p.name.toLowerCase() === name.toLowerCase());
      if (taken) return this.send(ws, { t: 'err', e: 'taken' });
      g.players[pid] = g.players[pid] ? { ...g.players[pid], name } : { name, score: 0, gain: 0, streak: 0 };
      at.pid = pid; ws.serializeAttachment(at);
      await this.save();
      this.send(ws, this.stateFor(pid));
      return this.pushCounts();
    }
    if (m.t === 'ans' && g.phase === 'q' && at.pid && g.players[at.pid] && !g.answers[at.pid]) {
      const now = Date.now(), q = g.qs[g.qi], a = Number(m.a);
      if (m.i !== g.qi || now > g.endsAt + 300 || !(a >= 0 && a < q.opts.length)) return;
      g.answers[at.pid] = { a, at: Math.max(now, g.startAt), ok: a === q.correct };
      this.send(ws, { t: 'got', a });
      await this.save();
      if (Object.keys(g.answers).length >= Object.keys(g.players).length) return this.closeQuestion();
      return this.pushCounts();
    }
  }

  async onAdmin(ws, at, m) {
    if (m.t === 'auth') {
      if (!this.env.ADMIN_PIN || String(m.pin) !== String(this.env.ADMIN_PIN)) return this.send(ws, { t: 'err', e: 'pin' });
      at.authed = true; ws.serializeAttachment(at);
      return this.send(ws, this.adminView());
    }
    if (!at.authed) return this.send(ws, { t: 'err', e: 'pin' });
    const g = this.g;
    switch (m.t) {
      case 'saveSet': {
        const s = m.set || {};
        const qs = (Array.isArray(s.qs) ? s.qs : []).slice(0, 60).map((q) => ({
          text: clean(q.text, 200),
          opts: (Array.isArray(q.opts) ? q.opts : []).map((o) => clean(o, 80)).filter(Boolean).slice(0, 4),
          correct: Math.max(0, Number(q.correct) || 0),
          dur: [10, 15, 20, 30].includes(Number(q.dur)) ? Number(q.dur) : 20,
        })).filter((q) => q.text && q.opts.length >= 2 && q.correct < q.opts.length);
        const set = { id: clean(s.id, 20) || Date.now().toString(36), name: clean(s.name, 60) || 'Sual dəsti', qs };
        const i = this.sets.findIndex((x) => x.id === set.id);
        if (i >= 0) this.sets[i] = set; else this.sets.push(set);
        await this.ctx.storage.put('sets', this.sets);
        return this.pushAdmin();
      }
      case 'delSet':
        this.sets = this.sets.filter((x) => x.id !== m.id);
        await this.ctx.storage.put('sets', this.sets);
        return this.pushAdmin();
      case 'newGame': {
        const set = this.sets.find((x) => x.id === m.setId);
        if (!set || !set.qs.length) return this.send(ws, { t: 'err', e: 'set' });
        await this.ctx.storage.deleteAlarm();
        this.g = { ...this.fresh(), setId: set.id, qs: set.qs };
        await this.save();
        for (const p of this.socks('player')) { const a = p.deserializeAttachment() || {}; a.pid = null; p.serializeAttachment(a); }
        return this.broadcastState();
      }
      case 'next':
        if (g.phase === 'lobby' || g.phase === 'reveal') return this.startQuestion();
        if (g.phase === 'q') return this.closeQuestion();
        return;
      case 'end': return this.finish();
      case 'kick':
        delete g.players[m.name && Object.keys(g.players).find((id) => g.players[id].name === m.name)];
        await this.save(); return this.broadcastState();
    }
  }

  async webSocketClose(ws) { /* oyunçu siyahıda qalır — geri qayıda bilər */ }
  async webSocketError(ws) {}
}
