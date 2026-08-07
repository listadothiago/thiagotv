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

const VERSION = 'thiagotv-v2';
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
      // Fall back only to a cached copy of *this* page. An earlier version fell
      // back to index.html for anything that missed, which meant a hiccup while
      // opening the programme guide silently delivered the television instead --
      // a wrong page that looks deliberate is worse than an honest failure.
      .catch(() => caches.match(req).then((hit) => hit || new Response(
        '<!doctype html><meta charset="utf-8">' +
        '<title>ThiagoTV — offline</title>' +
        '<body style="background:#0b1a33;color:#c9a961;font:14px monospace;' +
        'display:flex;align-items:center;justify-content:center;height:100vh;' +
        'margin:0;text-align:center">' +
        '<p>No signal.<br><br><a style="color:#7fd4ff" href="/">Back to ThiagoTV</a></p>',
        { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
      )))
  );
});
