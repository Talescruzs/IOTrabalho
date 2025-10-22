(function() {
  const script = document.currentScript;
  const controlUrl = (script && script.dataset && script.dataset.controlUrl) || '/control';

  const keyMap = { 'w': 'forward', 'a': 'left', 'd': 'right' };
  const pressed = new Set();
  const statusEl = document.getElementById('status');

  function updateUI(key, isDown) {
    const el = document.getElementById('key-' + key);
    if (!el) return;
    if (isDown) el.classList.add('pressed'); else el.classList.remove('pressed');
  }

  async function send(action, event) {
    try {
      const res = await fetch(controlUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, event })
      });
      const data = await res.json().catch(() => ({}));
      if (statusEl) statusEl.textContent = `Enviado: ${action} (${event})` + (data && data.ok ? ' ✓' : '');
    } catch (e) {
      if (statusEl) statusEl.textContent = 'Falha ao enviar comando.';
    }
  }

  document.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (!keyMap[k]) return;
    if (pressed.has(k)) return;
    pressed.add(k);
    updateUI(k, true);
    send(keyMap[k], 'down');
  });

  document.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    if (!keyMap[k]) return;
    pressed.delete(k);
    updateUI(k, false);
    send(keyMap[k], 'up');
  });
})();
