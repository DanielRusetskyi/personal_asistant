// /sw.js — Service Worker для Web Push + запит звуку у відкритої вкладки

// миттєво активуємо нову версію SW
self.addEventListener("install", (e) => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

// утиліта: розіслати повідомлення у всі відкриті вкладки сайту
async function broadcastToPages(msg) {
  const all = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  for (const c of all) c.postMessage(msg);
}

// допоміжне: нормалізувати URL відкриття
function toAbsUrl(target) {
  try { return new URL(target, self.location.origin).href; }
  catch { return self.location.origin + "/"; }
}

// === PUSH ===
self.addEventListener("push", (event) => {
  if (!event.data) return;

  // 1) дістаємо payload
  let payload = {};
  try {
    payload = event.data.json();
  } catch {
    payload = { title: "Повідомлення", body: event.data.text() };
  }

  const title = payload.title || "Нагадування";
  const body  = payload.message || payload.body || "";
  const url   = payload.url || "/";

  // 2) показуємо системну нотифікацію
  const options = {
    body,
    icon:  payload.icon  || "/static/favicon.ico",
    badge: payload.badge || "/static/favicon.ico",
    data: { url, ...(payload.data || {}) },

    // нижче — опційно (корисно для “оновлюваних” нотифікацій):
    tag: payload.tag,                // однаковий tag → нова нотифікація замінює попередню
    renotify: !!payload.tag,         // при заміні — дзвінок системного звуку
    silent: !!payload.silent,        // true → без системного звуку (звук відтворить вкладка)
    // vibrate: [100, 50, 100],      // за бажанням
    // actions: [{action:"open", title:"Відкрити"}],
  };

  const show = self.registration.showNotification(title, options);

  // 3) просимо вкладку програти звук (якщо відкрита)
  //    ключ sound: "chime" | "ping" | "success" | "alert" | "bell" (або свій)
  const askPlay = broadcastToPages({
    type:   "PLAY_SOUND",
    sound:  payload.sound || "chime",
    volume: typeof payload.volume === "number" ? payload.volume : 1.0, // 0..1
  });

  event.waitUntil(Promise.all([show, askPlay]));
});

// === КЛІК ПО НОТИФІКАЦІЇ ===
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || "/";
  const abs = toAbsUrl(target);

  event.waitUntil((async () => {
    const all = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of all) {
      // порівнюємо без фрагментів (#...)
      const cu = c.url.split("#")[0], au = abs.split("#")[0];
      if (cu === au && "focus" in c) return c.focus();
    }
    if (self.clients.openWindow) return self.clients.openWindow(abs);
  })());
});

// === ПІДПИСКА ЗМІНИЛАСЬ (рідко: міграція, очищення браузера тощо) ===
self.addEventListener("pushsubscriptionchange", (event) => {
  // просимо сторінку перевиставити підписку (у ній є логіка з CSRF/VAPID)
  event.waitUntil(broadcastToPages({ type: "REUPLOAD_SUBSCRIPTION" }));
});

// (не обов’язково) обробка повідомлень від сторінки → SW
self.addEventListener("message", (_event) => {
  // місце для майбутніх команд
});
