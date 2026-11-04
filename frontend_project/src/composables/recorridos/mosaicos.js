import { CACHE_MOSAICOS, URL_MOSAICOS } from '@/config/mapa'

// Guardado de los mosaicos de una zona pequeña para ver el mapa sin conexión.
//
// Se limita a lo imprescindible a propósito: los servidores públicos de OpenStreetMap desaconsejan la descarga
// masiva de mosaicos, así que solo se guarda el entorno del recorrido de una reserva real (unos cientos de
// imágenes como máximo). Si el uso crece, conviene un proveedor propio o de pago.
const ZOOMS = [12, 13, 14, 15, 16, 17]
export const MAX_MOSAICOS_POR_ZONA = 150

export const mosaicoDe = (lat, lng, z) => {
    const n = 2 ** z
    const radianes = (lat * Math.PI) / 180
    const x = Math.floor(((lng + 180) / 360) * n)
    const y = Math.floor(((1 - Math.log(Math.tan(radianes) + 1 / Math.cos(radianes)) / Math.PI) / 2) * n)
    return { x: Math.min(Math.max(x, 0), n - 1), y: Math.min(Math.max(y, 0), n - 1), z }
}

export const urlDeMosaico = ({ z, x, y }) => URL_MOSAICOS.replace('{z}', z).replace('{x}', x).replace('{y}', y)

// Mosaicos que cubren los puntos dados más un margen. Se prefiere el mayor detalle posible: si la zona no cabe
// en el máximo, se quita el zoom más alto hasta que quepa.
export function mosaicosDeLaZona(puntos, { margenM = 400, maximo = MAX_MOSAICOS_POR_ZONA } = {}) {
    if (!puntos.length) return []
    const latitudes = puntos.map(punto => punto[0])
    const longitudes = puntos.map(punto => punto[1])
    const grados = margenM / 111320
    const sur = Math.min(...latitudes) - grados
    const norte = Math.max(...latitudes) + grados
    const gradosLng = grados / Math.max(Math.cos((((sur + norte) / 2) * Math.PI) / 180), 0.2)
    const oeste = Math.min(...longitudes) - gradosLng
    const este = Math.max(...longitudes) + gradosLng

    const cubrir = (zooms) => {
        const lista = []
        zooms.forEach((z) => {
            const noroeste = mosaicoDe(norte, oeste, z)
            const sureste = mosaicoDe(sur, este, z)
            for (let x = noroeste.x; x <= sureste.x; x++) {
                for (let y = noroeste.y; y <= sureste.y; y++) lista.push({ x, y, z })
            }
        })
        return lista
    }

    const zooms = [...ZOOMS]
    let lista = cubrir(zooms)
    while (lista.length > maximo && zooms.length > 1) {
        zooms.pop()
        lista = cubrir(zooms)
    }
    return lista.slice(0, maximo)
}

const pausa = (ms) => new Promise(resolver => setTimeout(resolver, ms))

// Descarga los mosaicos que falten y los guarda en la caché del service worker. Pocas peticiones a la vez y con
// una pausa entre ellas, para no saturar el servicio de mosaicos.
export async function guardarMosaicos(lista, alProgreso) {
    if (!lista.length || !('caches' in window)) return { guardados: 0, fallidos: lista.length, total: lista.length }
    const cache = await caches.open(CACHE_MOSAICOS)
    const cola = [...lista]
    let guardados = 0
    let fallidos = 0
    let hechos = 0

    const trabajador = async () => {
        while (cola.length) {
            const url = urlDeMosaico(cola.shift())
            try {
                if (await cache.match(url, { ignoreVary: true })) {
                    guardados++
                } else {
                    const respuesta = await fetch(url, { mode: 'cors' })
                    if (respuesta.ok) {
                        await cache.put(url, respuesta)
                        guardados++
                    } else {
                        fallidos++
                    }
                    await pausa(120)
                }
            } catch {
                fallidos++
            }
            hechos++
            alProgreso?.(hechos, lista.length)
        }
    }
    await Promise.all(Array.from({ length: 3 }, trabajador))
    // Pide al navegador que no borre estos datos cuando necesite espacio.
    try { await navigator.storage?.persist?.() } catch { /* sin soporte */ }
    return { guardados, fallidos, total: lista.length }
}
