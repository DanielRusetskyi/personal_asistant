// static/noteapp/js/push.js
(function () {
  const DEBUG = true; // => false у проді
  const ENDPOINTS = window.PUSH_ENDPOINTS || {};
  const LS_DISABLED = "push_disabled"; // "1" означає локально вимкнено

  function log(...a){ if (DEBUG) console.log("[push]", ...a); }
  function warn(...a){ if (DEBUG) console.warn("[push]", ...a); }

  // ---- helpers ----
  function normalizeKey(s){ return (s || "").trim().replace(/\s+/g, ""); }

  function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
    return outputArray;
  }

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[2]) : "";
  }

  const locallyDisabled = () => localStorage.getItem(LS_DISABLED) === "1";
  const setLocallyDisabled = (on) => {
    if (on) localStorage.setItem(LS_DISABLED, "1");
    else localStorage.removeItem(LS_DISABLED);
  };

  async function fetchJSON(url, opts) {
    const r = await fetch(url, opts);
    if (!r.ok) throw new Error(`${opts?.method || "GET"} ${url} -> ${r.status}`);
    return r.json();
  }

  async function getBackendStatus() {
    if (!ENDPOINTS.status) return { enabled: true, has_subscription: false };
    try {
      return await fetchJSON(ENDPOINTS.status, { cache: "no-store" });
    } catch (e) {
      warn("status fetch failed", e);
      // якщо статус не дістався — не вмикаємо
      return { enabled: false, has_subscription: false };
    }
  }

  async function fetchPublicKey() {
    if (!ENDPOINTS.publicKey) throw new Error("PUSH_ENDPOINTS.publicKey is missing");
    const r = await fetch(ENDPOINTS.publicKey, { cache: "no-store" });
    if (!r.ok) throw new Error("Cannot get VAPID public key: " + r.status);
    return (await r.text()).trim();
  }

  async function sendSubscriptionToServer(sub, vapidPk) {
    if (!ENDPOINTS.subscribe) throw new Error("PUSH_ENDPOINTS.subscribe is missing");
    const r = await fetch(ENDPOINTS.subscribe, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ subscription: sub.toJSON(), vapid_pk: vapidPk }),
    });
    if (!r.ok) throw new Error("Subscribe POST failed: " + r.status);
  }

  async function unsubscribeOnServer(endpoint) {
    if (!ENDPOINTS.unsubscribe) { warn("PUSH_ENDPOINTS.unsubscribe is missing"); return; }
    try {
      await fetch(ENDPOINTS.unsubscribe, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ endpoint }),
      });
    } catch (e) { warn("unsubscribeOnServer error:", e); }
  }

  async function toggleBackend(enabled) {
    if (!ENDPOINTS.toggle) { warn("PUSH_ENDPOINTS.toggle is missing"); return; }
    await fetch(ENDPOINTS.toggle, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ enabled }),
    });
  }

  async function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) throw new Error("Service Worker not supported");
    await navigator.serviceWorker.register("/sw.js"); // sw.js у корені
    return await navigator.serviceWorker.ready;
  }

  // ВАЖЛИВО: нічого не підписуємо, якщо заборонено
  async function ensureFreshSubscription(reg, allowed) {
    if (!allowed) { log("ensureFreshSubscription skipped (disabled)"); return null; }

    const currentKey = normalizeKey(await fetchPublicKey());
    const storedKey  = normalizeKey(localStorage.getItem("vapid_pk"));
    let sub = await reg.pushManager.getSubscription();

    if (!sub || storedKey !== currentKey) {
      if (sub) {
        try { await unsubscribeOnServer(sub.endpoint); await sub.unsubscribe(); }
        catch (e) { warn("unsubscribe old failed", e); }
      }
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(currentKey),
      });
      await sendSubscriptionToServer(sub, currentKey);
      localStorage.setItem("vapid_pk", currentKey);
      log("Subscribed with fresh key");
    }
    return sub;
  }

  function setStatus(on) {
  const statusEl  = document.getElementById("push-status");
  const enableBtn = document.getElementById("enable-push-btn");
  const disableBtn= document.getElementById("disable-push-btn");

  if (statusEl) {
    const enabledLabel  = statusEl.dataset.enabledLabel  || "Enabled";
    const disabledLabel = statusEl.dataset.disabledLabel || "Disabled";
    statusEl.textContent = on ? enabledLabel : disabledLabel;
    statusEl.className = "badge " + (on ? "text-bg-success" : "text-bg-secondary");
  }
  if (enableBtn)  enableBtn.hidden  = !!on;
  if (disableBtn) disableBtn.hidden = !on;
}

  // ---- flows ----
  async function enablePushFlow() {
    if (!("serviceWorker" in navigator) || !("PushManager" in window) || !("Notification" in window)) {
      alert("Браузер не підтримує Push/Service Worker."); return;
    }
    if (Notification.permission === "denied") {
      alert("Сповіщення заборонені у браузері. Дозволь у налаштуваннях сайту."); return;
    }
    if (Notification.permission === "default") {
      const res = await Notification.requestPermission();
      if (res !== "granted") { alert("Без дозволу на сповіщення підписка неможлива."); return; }
    }

    await toggleBackend(true);     // 1) вмикаємо на бекенді
    setLocallyDisabled(false);     // 2) прибираємо локальну заборону

    const reg = await registerServiceWorker();
    await ensureFreshSubscription(reg, /*allowed=*/true);
    setStatus(true);
    log("Push enabled");
  }

  async function disablePushFlow() {
    try {
      await toggleBackend(false);  // 1) вимикаємо на бекенді
      setLocallyDisabled(true);    // 2) локально забороняємо ресабскрайб

      const reg = await navigator.serviceWorker.getRegistration();
      const sub = reg && await reg.pushManager.getSubscription();
      if (sub) {
        await unsubscribeOnServer(sub.endpoint);
        await sub.unsubscribe();
      }
      // (реєстрацію SW не чіпаємо: хай лишається для інших задач)
    } catch (e) { warn("Disable flow error", e); }

    setStatus(false);
    log("Push disabled");
  }

  // ---- bootstrap ----
  document.addEventListener("DOMContentLoaded", async () => {
    // кнопки
    document.getElementById("enable-push-btn")?.addEventListener("click", () => {
      enablePushFlow().catch(err => { warn(err); alert("Помилка увімкнення push."); });
    });
    document.getElementById("disable-push-btn")?.addEventListener("click", () => {
      disablePushFlow().catch(warn);
    });

    // якщо немає підтримки — підказка
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      document.getElementById("push-support-hint")?.removeAttribute("hidden");
      document.getElementById("enable-push-btn")?.setAttribute("disabled", "disabled");
      return;
    }

    // 1) дізнаємось бекенд-статус
    const { enabled } = await getBackendStatus();
    const allowed = enabled && !locallyDisabled();

    // 2) виставляємо початковий UI
    try {
      const reg = await navigator.serviceWorker.register("/sw.js").then(() => navigator.serviceWorker.ready);
      const sub = await reg.pushManager.getSubscription();
      setStatus(allowed && !!sub);
    } catch (_) { setStatus(false); }

    // 3) «тиха» перепідписка — ЛИШЕ якщо дозволено
    if (allowed && Notification.permission === "granted") {
      try {
        const reg = await registerServiceWorker();
        const sub = await ensureFreshSubscription(reg, /*allowed=*/true);
        setStatus(!!sub);
      } catch (e) { warn("Silent ensure failed", e); }
    }

    // 4) SW може попросити перевивантажити підписку — теж лише якщо allowed
    navigator.serviceWorker.addEventListener("message", async (evt) => {
      if (evt.data && evt.data.type === "REUPLOAD_SUBSCRIPTION") {
        const { enabled: en2 } = await getBackendStatus();
        const ok = en2 && !locallyDisabled();
        if (!ok) return;
        try {
          const reg = await navigator.serviceWorker.ready;
          const sub = await ensureFreshSubscription(reg, /*allowed=*/true);
          setStatus(!!sub);
        } catch (e) { warn("reupload from SW failed", e); }
      }
    });
    navigator.serviceWorker?.addEventListener("message", (evt) => {
      if (!evt.data) return;
      if (evt.data.type === "PLAY_SOUND") {
        window.playPushDing?.();
      }
      // якщо хочеш ще показувати тости із payload:
      // if (evt.data.type === "PUSH_PAYLOAD") { ... }
    });
  });
})();
