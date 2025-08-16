document.addEventListener('DOMContentLoaded', () => {
  const toggle     = document.getElementById('enableReminder');
  const block      = document.getElementById('timeBlock');
  const hours      = document.getElementById('hours');
  const minutes    = document.getElementById('minutes');
  const hourValue  = document.getElementById('hourValue');
  const minuteValue= document.getElementById('minuteValue');
  const due        = document.getElementById('due_time');

  if (!toggle || !block || !hours || !minutes || !hourValue || !minuteValue || !due) return;

  const pad = n => String(n).padStart(2, '0');

  function syncFromSliders() {
    const h = pad(hours.value);
    const m = pad(minutes.value);
    hourValue.textContent   = h;
    minuteValue.textContent = m;
    due.value = toggle.checked ? `${h}:${m}` : '';
  }

  function applyEnabled() {
    const on = toggle.checked;
    block.classList.toggle('d-none', !on);
    hours.disabled   = !on;
    minutes.disabled = !on;
    syncFromSliders();
  }

  // Ініціалізація з уже наявного due_time (якщо редагування або сервер підставив)
  if (due.value) {
    const [h, m] = due.value.split(':');
    if (h != null) hours.value = parseInt(h, 10);
    if (m != null) minutes.value = parseInt(m, 10);
    toggle.checked = true;
  }

  applyEnabled();

  // Слухачі
  toggle.addEventListener('change', applyEnabled);
  hours.addEventListener('input',  syncFromSliders);
  minutes.addEventListener('input',syncFromSliders);
});