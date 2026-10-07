// 離線使用：網頁採「網路優先、離線用快取」。書籍資料匯入後存在 IndexedDB，不經過這裡。
const CACHE = 'caregiver-guide-v1';
const CORE = [
  './', 'index.html', 'manifest.webmanifest', 'favicon.ico',
  'icons/favicon-32.png', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  // 公開網站上沒有 data.js，直接回空內容，避免離線時報錯
  if (url.pathname.endsWith('/data.js')) {
    e.respondWith(fetch(req).then(res => res.ok ? res : new Response('', {headers: {'Content-Type': 'text/javascript'}}))
      .catch(() => new Response('', {headers: {'Content-Type': 'text/javascript'}})));
    return;
  }
  e.respondWith(fetch(req).then(res => {
    if (res.status === 200) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  }).catch(() => caches.match(req, {ignoreSearch: true}).then(hit => hit || caches.match('index.html'))));
});
