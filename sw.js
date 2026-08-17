const CACHE='tax-lien-guide-v4';
const ASSETS=[
  './',
  './index.html',
  './tax-lien-properties.html',
  './tax-deed.html',
  './property-screener.html',
  './calendar.html',
  './project-management.html',
  './source-registry.html',
  './manifest.webmanifest',
  './app-icon.svg',
  './data/properties.json',
  './data/tax-lien-properties.json',
  './data/project-management.json',
  './data/source-registry.json'
];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  event.respondWith(
    fetch(event.request).then(response=>{
      const copy=response.clone();
      caches.open(CACHE).then(cache=>cache.put(event.request,copy));
      return response;
    }).catch(()=>caches.match(event.request).then(cached=>cached||caches.match('./index.html')))
  );
});
