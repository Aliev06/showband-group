// Showband Oyun — serverlə əlaqə (WebSocket, avtomatik yenidən qoşulma, saat sinxronu)
(function () {
  const q = new URLSearchParams(location.search);
  const local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) || location.protocol === 'file:';
  const API = q.get('api') || (local ? 'ws://127.0.0.1:8787/ws' : 'wss://showband-oyun.murad-f6f.workers.dev/ws');

  window.Net = function (role, onMsg, onStatus) {
    let ws = null, tries = 0, alive = false, pingT = null, queue = [];
    const self = { off: 0, rtt: 0, open: false };
    function connect() {
      ws = new WebSocket(API + '?role=' + role);
      ws.onopen = () => {
        tries = 0; self.open = true; onStatus && onStatus(true);
        self.onopen && self.onopen();
        queue.splice(0).forEach((m) => ws.send(m));
        ping(); clearInterval(pingT); pingT = setInterval(ping, 15000);
      };
      ws.onmessage = (e) => {
        let m; try { m = JSON.parse(e.data); } catch (x) { return; }
        if (m.t === 'pong') {
          const rtt = performance.now() - m.c;
          if (!self.rtt || rtt < self.rtt * 1.5) { self.rtt = rtt; self.off = m.now + rtt / 2 - Date.now(); }
          return;
        }
        if (m.now && !self.rtt) self.off = m.now - Date.now();
        onMsg(m);
      };
      ws.onclose = () => {
        self.open = false; clearInterval(pingT); onStatus && onStatus(false);
        const wait = Math.min(4000, 300 * Math.pow(1.6, tries++));
        setTimeout(connect, wait);
      };
      ws.onerror = () => { try { ws.close(); } catch (x) {} };
    }
    function ping() { self.send({ t: 'ping', c: performance.now() }); }
    self.send = (o) => { const s = JSON.stringify(o); if (ws && ws.readyState === 1) ws.send(s); else queue.push(s); };
    self.now = () => Date.now() + self.off;
    document.addEventListener('visibilitychange', () => { if (!document.hidden && ws && ws.readyState > 1) connect(); });
    connect();
    return self;
  };
})();
