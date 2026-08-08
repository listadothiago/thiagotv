/* ThiagoTV service worker.
 *
 * This exists to make the set installable, and for nothing else. The programmes
 * are streamed from YouTube, so an offline ThiagoTV has nothing to show, and
 * there is no version of this site worth having without a network.
 *
 * That matters, because an earlier version of this file cached the page and the
 * schedule and served them network-first with a cache fallback. The intent was
 * a safety net; the effect was that a browser -- above all an installed app --
 * could keep showing a stale television long after the site had changed, with
 * no way for the viewer to tell. Caching something that has no offline value in
 * the first place bought nothing and cost correctness.
 *
 * So: nothing but the icons is cached. Every page, script and schedule request
 * goes to the network exactly as it would without a service worker.
 */

const VERSION = 'thiagotv-v3';

// Only the icons, which never change without a new filename.
const PRECACHE = [
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(VERSION)
      // Individually, so one missing file doesn't fail the whole install.
      .then((cache) => Promise.allSettled(PRECACHE.map((url) => cache.add(url))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      // Drops the old versions, and with them every stale page they were holding.
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

  // Anything not ours -- above all the YouTube player -- is left entirely alone.
  if (url.origin !== self.location.origin) return;

  // Icons: cache first, they are immutable in practice.
  if (url.pathname.startsWith('/icons/')) {
    event.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(VERSION).then((c) => c.put(req, copy));
        return res;
      }))
    );
    return;
  }

  // Everything else: no interception at all. The network is the only source of
  // truth for what the station is showing.
});
