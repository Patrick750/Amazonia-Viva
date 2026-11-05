// Service worker de Amazonia Viva (MEJ-001).
// Solo guarda lo que no depende de la sesión: la carcasa de la aplicación, sus recursos
// estáticos y los mosaicos del mapa visitados. Nunca intercepta la API ni guarda
// respuestas autenticadas. Los puntos GPS se conservan en IndexedDB, no aquí.
const VERSION = 'v1'
const CACHE_APP = `amazonia-app-${VERSION}`
const CACHE_MAPA = 'amazonia-mapa-v1'
const MAX_MOSAICOS = 1200

self.addEventListener('install', (evento) => {
  evento.waitUntil((async () => {
    const cache = await caches.open(CACHE_APP)
    await cache.addAll(['/', '/manifest.webmanifest'])
    // En la primera visita el código principal ya se cargó antes de que existiera el worker y no pasó por él:
    // se descarga ahora lo que la carcasa necesita para arrancar (sale del propio index.html).
    const html = await (await cache.match('/')).text()
    const recursos = [...new Set([...html.matchAll(/(?:src|href)="(\/assets\/[^"]+)"/g)].map(coincidencia => coincidencia[1]))]
    await Promise.all(recursos.map(url => cache.add(url).catch(() => {})))
  })())
  self.skipWaiting()
})

self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    caches.keys()
      .then(claves => Promise.all(claves.filter(c => c.startsWith('amazonia-app-') && c !== CACHE_APP).map(c => caches.delete(c))))
      .then(() => self.clients.claim())
  )
})

async function recortar(cache) {
  const claves = await cache.keys()
  if (claves.length > MAX_MOSAICOS) {
    await Promise.all(claves.slice(0, claves.length - MAX_MOSAICOS).map(c => cache.delete(c)))
  }
}

async function mosaico(peticion) {
  const cache = await caches.open(CACHE_MAPA)
  // ignoreVary: el mosaico guardado debe servir aunque cambien las cabeceras de la petición.
  const guardado = await cache.match(peticion, { ignoreVary: true })
  if (guardado) return guardado
  try {
    const respuesta = await fetch(peticion)
    if (respuesta.ok) {
      cache.put(peticion, respuesta.clone())
      recortar(cache)
    }
    return respuesta
  } catch {
    return Response.error()
  }
}

async function recursoEstatico(peticion) {
  const cache = await caches.open(CACHE_APP)
  const guardado = await cache.match(peticion)
  if (guardado) return guardado
  const respuesta = await fetch(peticion)
  if (respuesta.ok) cache.put(peticion, respuesta.clone())
  return respuesta
}

async function navegacion(peticion) {
  const cache = await caches.open(CACHE_APP)
  try {
    const respuesta = await fetch(peticion)
    if (respuesta.ok) cache.put('/', respuesta.clone())
    return respuesta
  } catch {
    // Sin conexión: se entrega la carcasa y la aplicación resuelve la ruta en el navegador.
    return (await cache.match('/')) || Response.error()
  }
}

self.addEventListener('fetch', (evento) => {
  const peticion = evento.request
  if (peticion.method !== 'GET') return
  const url = new URL(peticion.url)

  if (url.hostname.endsWith('tile.openstreetmap.org')) {
    evento.respondWith(mosaico(peticion))
  } else if (url.origin === self.location.origin) {
    if (peticion.mode === 'navigate') evento.respondWith(navegacion(peticion))
    else if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/icons/') || url.pathname === '/manifest.webmanifest') evento.respondWith(recursoEstatico(peticion))
  }
})
