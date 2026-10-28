// Service worker de Amazonia Viva (MEJ-001).
// Solo guarda lo que no depende de la sesión: la carcasa de la aplicación, sus recursos
// estáticos y los mosaicos del mapa visitados. Nunca intercepta la API ni guarda
// respuestas autenticadas. Los puntos GPS se conservan en IndexedDB, no aquí.
const VERSION = 'v1'
const CACHE_APP = `amazonia-app-${VERSION}`
const CACHE_MAPA = 'amazonia-mapa-v1'
const MAX_MOSAICOS = 400

self.addEventListener('install', (evento) => {
  evento.waitUntil(caches.open(CACHE_APP).then(cache => cache.addAll(['/', '/manifest.webmanifest'])))
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
  const guardado = await cache.match(peticion)
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
    else if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/icons/')) evento.respondWith(recursoEstatico(peticion))
  }
})
