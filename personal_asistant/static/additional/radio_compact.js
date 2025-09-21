// static/additional/radio_compact.js
function readCfg(){ const el=document.getElementById('radio-config'); try{ return JSON.parse(el?.textContent||'{}'); }catch{ return {}; } }
function $(id){ return document.getElementById(id); }

let actx, src, gain, analyser, rafId;
let vizOk = false;

function ensureGraph(audio){
  if (actx) return;
  actx = new (window.AudioContext || window.webkitAudioContext)();
  try {
    src = actx.createMediaElementSource(audio);
    gain = actx.createGain();
    analyser = actx.createAnalyser();
    analyser.fftSize = 256;
    src.connect(gain); gain.connect(analyser); analyser.connect(actx.destination);
    vizOk = true;
  } catch (e) {
    // iOS/Safari часто кидає помилку коли немає CORS
    console.warn('WebAudio graph failed (likely CORS)', e);
    vizOk = false;
  }
}

const unlock = () => {
  if (actx && actx.state !== 'running') actx.resume().catch(()=>{});
  window.removeEventListener('pointerdown', unlock);
  window.removeEventListener('touchend', unlock);
};
window.addEventListener('pointerdown', unlock, { once:true });
window.addEventListener('touchend', unlock, { once:true });

function startViz(canvas){
  if(!analyser) return;
  const dpr = window.devicePixelRatio || 1;
  const ctx = canvas.getContext('2d');
  function resize(){
    canvas.width  = Math.floor(canvas.clientWidth  * dpr);
    canvas.height = Math.floor(canvas.clientHeight * dpr);
  }
  resize(); window.addEventListener('resize', resize);

  const data = new Uint8Array(analyser.frequencyBinCount);
  function draw(){
    rafId = requestAnimationFrame(draw);
    analyser.getByteFrequencyData(data);
    const {width:w,height:h} = canvas;
    ctx.clearRect(0,0,w,h);
    const n = data.length, gap = 2*dpr, barW = (w - gap*(n-1)) / n;
    for(let i=0;i<n;i++){
      const v = data[i]/255, bh = v*h, x = i*(barW+gap), y = h - bh;
      const r = Math.min(6*dpr, barW/2, bh/2);
      ctx.beginPath();
      ctx.moveTo(x, y+r); ctx.arcTo(x,y,x+r,y,r);
      ctx.lineTo(x+barW-r, y); ctx.arcTo(x+barW,y,x+barW,y+r,r);
      ctx.lineTo(x+barW, h); ctx.lineTo(x, h); ctx.closePath();
      const g = ctx.createLinearGradient(x,0,x+barW,0);
      g.addColorStop(0,'#60a5fa'); g.addColorStop(1,'#22d3ee');
      ctx.fillStyle = g; ctx.fill();
    }
  }
  draw();
}
function stopViz(){ if(rafId) cancelAnimationFrame(rafId); rafId=null; }

document.addEventListener('DOMContentLoaded', () => {
  const cfg = readCfg();
  const ST_URL = cfg.stationsUrl;

  const sel    = $('station');
  const audio  = $('audio');
  const play   = $('btn-play');
  const stop   = $('btn-stop');
  const mute   = $('btn-mute');
  const vol    = $('volume');
  const title  = $('now-title');
  const sub    = $('now-sub');
  const logo   = $('logo');
  const status = $('status');
  const viz    = $('viz');

  let stations = [];
  let current  = null;
  let isStopped = false;

  function pickSrc(s){ return s.stream; }
  function updatePlayIcon(){ play.innerHTML = audio.paused ? '<i class="bi bi-play-fill"></i>' : '<i class="bi bi-pause-fill"></i>'; }
  function updateMuteIcon(){ mute.innerHTML = audio.muted ? '<i class="bi bi-volume-mute"></i>' : '<i class="bi bi-volume-up"></i>'; }

  async function loadStations(){
    let res;
    try { res = await fetch(new URL(ST_URL, location.origin)); }
    catch(e){ status.textContent = 'Помилка мережі'; return; }
    if (!res.ok){ status.textContent = 'Помилка ' + res.status; return; }

    let data;
    try { data = await res.json(); }
    catch { status.textContent = 'Невірний JSON'; return; }

    stations = data.stations || [];
    sel.innerHTML = '<option value="">Обрати станцію…</option>' +
      stations.map(s => `<option value="${s.slug}">${s.name}</option>`).join('');

    try {
      const last = localStorage.getItem('radio.last');
      if (last) { sel.value = last; onSelect(); }
    } catch {}
  }

  function onSelect(){
    const slug = sel.value;
    const s = stations.find(x => x.slug === slug);
    if (!s){ audio.pause(); return; }
    current = s;
    isStopped = false;

    ensureGraph(audio);

    audio.crossOrigin = 'anonymous';
    audio.src = pickSrc(s);

    title.textContent = s.name;
    sub.textContent = s.country || '';
    logo.src = s.icon || '';
    logo.classList.toggle('hidden', !s.icon);

    status.textContent = 'Завантаження…';
    audio.play().then(()=> actx?.resume?.()).catch(()=>{});
    updatePlayIcon();
    try { localStorage.setItem('radio.last', s.slug); } catch {}

    if ('mediaSession' in navigator){
      navigator.mediaSession.metadata = new MediaMetadata({
        title: s.name,
        artist: s.country || 'Radio',
        artwork: s.icon ? [{ src: s.icon, sizes: '96x96', type: 'image/png' }] : []
      });
    }
  }

  // Події керування
  sel.addEventListener('change', onSelect);
  play.addEventListener('click', () => {
    if (!current && stations.length){ sel.value = stations[0].slug; onSelect(); return; }
    ensureGraph(audio);

    if (isStopped && current) {
    audio.crossOrigin = 'anonymous';
    audio.src = pickSrc(current);
    isStopped = false;
  }

    if (audio.paused) audio.play().then(()=> actx?.resume?.()); else audio.pause();
  });
  stop.addEventListener('click', () => {
    audio.pause(); audio.removeAttribute('src'); audio.load();
    isStopped = true;
    status.textContent = 'Зупинено'; updatePlayIcon(); stopViz();
  });
  mute.addEventListener('click', () => { audio.muted = !audio.muted; updateMuteIcon(); });
  vol.addEventListener('input', () => { if (gain) gain.gain.value = parseFloat(vol.value||'1'); else audio.volume = parseFloat(vol.value||'1'); });

  // Події аудіо
  audio.addEventListener('playing', () => {
  status.textContent = 'Грає';
  updatePlayIcon();
  if (vizOk && analyser) startViz(viz);
  else status.textContent = 'Грає (без візуалізації — CORS)';
  });
  audio.addEventListener('pause',   () => { status.textContent = 'Пауза'; updatePlayIcon(); stopViz(); });
  audio.addEventListener('stalled', () =>  status.textContent = 'Буфер…');
  audio.addEventListener('error',   () =>  status.textContent = 'Помилка відтворення');

  // === ТІЛЬКИ ДЛЯ ДЕСКТОПУ: гарячі клавіші ===
  const isDesktop =
    window.matchMedia('(hover: hover) and (pointer: fine)').matches &&
    (navigator.maxTouchPoints || 0) === 0;

  function onHotkey(e){
    const tag = (e.target.tagName||'').toLowerCase();
    if (['input','select','textarea'].includes(tag)) return;
    if (e.code === 'Space'){ e.preventDefault(); play.click(); }
    else if (e.key.toLowerCase() === 's'){ e.preventDefault(); stop.click(); }
    else if (e.key.toLowerCase() === 'm'){ e.preventDefault(); mute.click(); }
    else if (e.key === 'ArrowUp'){ e.preventDefault(); vol.value = Math.min(1, (+vol.value||1) + 0.05); vol.dispatchEvent(new Event('input')); }
    else if (e.key === 'ArrowDown'){ e.preventDefault(); vol.value = Math.max(0, (+vol.value||1) - 0.05); vol.dispatchEvent(new Event('input')); }
  }

  if (isDesktop) {
    window.addEventListener('keydown', onHotkey);
  }

  loadStations();
});
