import axios from '@/api/axios'
import { guardarMosaicos, mosaicosDeLaZona } from './mosaicos'

// Mapa del recorrido de una reserva guardado en el dispositivo para usarlo sin conexión el día de la experiencia.
// Hay que prepararlo ANTES, con internet (al abrir «Mis reservas»): ese día puede no haber señal.
//
// En localStorage, bajo CLAVE, un objeto por paquete:
// { paquete, nombre, fecha 'AAAA-MM-DD', disponible, puntos [[lat, lng]], distancia_km,
//   ubicacion_paquete { latitud, longitud, lugar } | null, guardado_en (ISO), mosaicos }
const CLAVE = 'recorridos_offline_v1'
const MAX_PAQUETES = 10

// El día de la experiencia es un día de Colombia, no el del huso horario del dispositivo.
export const hoyEnColombia = () => new Date().toLocaleDateString('en-CA', { timeZone: 'America/Bogota' })

const leer = () => {
    try {
        return JSON.parse(localStorage.getItem(CLAVE) || '{}')
    } catch {
        return {}
    }
}

export const obtenerGuardado = (paquete) => leer()[paquete] || null

// Paquetes guardados cuya experiencia es hoy. Sin conexión no se puede validar la compra en el servidor, así que
// solo se usa lo que se guardó con una reserva confirmada.
export const guardadosParaHoy = () => Object.values(leer()).filter(item => item.fecha === hoyEnColombia())

export function guardarPaquete(item) {
    const datos = leer()
    datos[item.paquete] = item
    // Se descartan las experiencias pasadas y, si hay demasiadas, las más lejanas.
    const hoy = hoyEnColombia()
    const vigentes = Object.values(datos)
        .filter(guardado => guardado.fecha >= hoy)
        .sort((a, b) => a.fecha.localeCompare(b.fecha))
        .slice(0, MAX_PAQUETES)
    try {
        localStorage.setItem(CLAVE, JSON.stringify(Object.fromEntries(vigentes.map(guardado => [guardado.paquete, guardado]))))
        return true
    } catch {
        return false // almacenamiento lleno o bloqueado
    }
}

// Guarda para una reserva confirmada: el recorrido publicado (es público) y el punto de encuentro, los mosaicos
// de su zona y la pantalla del mapa, que se carga bajo demanda y de otro modo no abriría sin conexión.
export async function prepararMapaOffline(reserva, alProgreso) {
    const { data } = await axios.get(`api/paquetes/${reserva.paquete_id}/recorrido/`)
    const ubicacion = reserva.latitud != null && reserva.longitud != null
        ? { latitud: reserva.latitud, longitud: reserva.longitud, lugar: reserva.ubicacion }
        : null
    const puntos = data.disponible ? data.puntos : []

    // Primero lo esencial (recorrido y punto de encuentro): si la persona cierra la app o se corta la conexión
    // mientras bajan los mosaicos, ya puede ver el recorrido sin conexión, aunque sea sobre un fondo vacío.
    const item = {
        paquete: reserva.paquete_id,
        nombre: reserva.nombre,
        fecha: reserva.fecha_actividad,
        disponible: data.disponible,
        puntos,
        distancia_km: data.distancia_km ?? 0,
        ubicacion_paquete: ubicacion,
        guardado_en: new Date().toISOString(),
        mosaicos: 0,
    }
    let guardado = guardarPaquete(item)
    // La pantalla del mapa se carga bajo demanda y de otro modo no abriría sin conexión.
    await import('@/views/mi-recorrido.vue').catch(() => {})

    const zona = [...puntos]
    if (ubicacion) zona.push([ubicacion.latitud, ubicacion.longitud])
    const resultado = await guardarMosaicos(mosaicosDeLaZona(zona), alProgreso)
    guardado = guardarPaquete({ ...item, mosaicos: resultado.guardados }) && guardado
    return { ...resultado, disponible: data.disponible, guardado }
}
