const C='kalifai-v13', M='kalifai-mapas-v1';
const CORE=['./','index.html','herramientas.html','zona.html','mapa.html','qrcode.js','kalifai-sonido.mp3','manifest.webmanifest','icon-192.png','icon-512.png','lib/maplibre-gl.js','lib/maplibre-gl.css'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(CORE)).catch(()=>{}));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C&&x!==M).map(x=>caches.delete(x)))));self.clients.claim()});
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET')return; const u=new URL(r.url);
  if(u.pathname.endsWith('.mp4'))return;
  // Mapas: teselas, estilos, fuentes y librería -> primero la copia guardada (funciona sin datos)
  if(u.hostname==='tiles.openfreemap.org'||u.pathname.indexOf('/lib/')>-1){
    e.respondWith(caches.open(M).then(c=>c.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok)c.put(r,res.clone());return res}))));return}
  // Resto (incluidos datos de ciudades): primero internet, si no hay, la copia guardada
  const store=u.pathname.indexOf('/mapas/')>-1?M:C;
  e.respondWith(fetch(r).then(res=>{if(res.ok&&(u.origin===location.origin||res.type==='cors')){const cp=res.clone();caches.open(store).then(c=>c.put(r,cp))}return res}).catch(()=>caches.match(r,{ignoreSearch:u.pathname.endsWith('.json')})))
});
