// Configuración común de los mapas.
//
// Los mosaicos se piden a una única dirección, sin los subdominios a/b/c: así cada imagen tiene una sola URL
// y la copia guardada para uso sin conexión se reutiliza siempre. `crossOrigin` hace que el navegador las pida
// con CORS, y solo así el service worker puede guardarlas (las respuestas «opacas» no se pueden almacenar).
export const URL_MOSAICOS = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'

export const OPCIONES_MOSAICOS = {
    attribution: '&copy; OpenStreetMap contributors',
    crossOrigin: true,
    maxZoom: 19,
}

// Misma caché que lee el service worker (public/sw.js).
export const CACHE_MOSAICOS = 'amazonia-mapa-v1'
