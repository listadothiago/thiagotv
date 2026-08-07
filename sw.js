/* ThiagoTV service worker.
 *
 * This exists to make the set installable, not to make it work offline -- the
 * programmes are streamed from YouTube, so an offline ThiagoTV has nothing to
 * show. What it can usefully do is start instantly and fail gracefully.
 *
 * The caching strategy follows from that. The schedule and the page change on
 * every publish, so they are fetched from the network first and only fall back
 * to a cached copy when the network is unavailable; serving a stale schedule
 * from cache would silently hide newly added programmes. Icons never change
 * without a new filename, so they come from the cache.
 */

const VERSION = 'thiagotv-v1';
const SHELL = [
  '/',
  '/index.html',
  '/playlist.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(VERSION)
      // Individually, so one missing file doesn't fail the whole install.
      .then((cache) => Promise.allSettled(SHELL.map((url) => cache.add(url))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Anything not ours -- above all the YouTube player -- goes straight to the
  // network. Caching a third party's streaming endpoints would break playback
  // in ways that are miserable to debug.
  if (url.origin !== self.location.origin) return;

  // Icons and stylesheet: cache first, they're immutable in practice.
  if (url.pathname.startsWith('/icons/') || url.pathname.endsWith('.css')) {
    event.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(VERSION).then((c) => c.put(req, copy));
        return res;
      }))
    );
    return;
  }

  // Everything else -- the page, the schedule, the programme pages -- network
  // first so a publish is seen immediately, cache only as a safety net.
  event.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(VERSION).then((c) => c.put(req, copy));
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match('/index.html')))
  );
});
