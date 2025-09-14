// Версія кешу (за бажанням)
const CACHE_VERSION = "v1";

// Встановлення SW
self.addEventListener("install", (event) => {
  self.skipWaiting();
});

// Активація SW
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

// Push-повідомлення
self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    // інколи приходить як текст
    data = { title: "Notification", body: event.data && event.data.text() };
  }

  const title = data.title || "Нагадування";
  const body = data.message || data.body || "";
  const url = data.url || "/";

  event.waitUntil(
    self.registration.showNotification(title, {
      body,
      data, // сюди можна передати url, note_id тощо
    })
  );
});

// Клік по нотифікації
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";

  event.waitUntil((async () => {
    const allClients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of allClients) {
      // якщо вкладка вже є — фокусуємо та оновлюємо
      if (client.url === url && "focus" in client) {
        client.focus();
        return;
      }
    }
    // інакше — відкриваємо нову
    if (self.clients.openWindow) {
      return self.clients.openWindow(url);
    }
  })());
});

// (опційно) fetch-кешування контенту
// self.addEventListener("fetch", (event) => { /* ... */ });
