import { onBeforeUnmount, ref } from 'vue'
import {
    actualizarRecorrido, guardarPunto, guardarRecorrido, listarRecorridos, puntosDelRecorrido,
} from './almacenLocal'
import { sincronizarPendientes } from './sincronizacion'

const DISTANCIA_MINIMA_M = 5
const INTERVALO_MAXIMO_MS = 30000
// Los puntos con una precisión peor que este valor (en metros) se descartan para no ensuciar el trazo.
export const PRECISION_MAXIMA_M = 50
const SINCRONIZAR_CADA_PUNTOS = 15

const distancia = (a, b) => {
    const rad = grados => (grados * Math.PI) / 180
    const h = Math.sin(rad(b[0] - a[0]) / 2) ** 2
        + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(rad(b[1] - a[1]) / 2) ** 2
    return 2 * 6371000 * Math.asin(Math.sqrt(h))
}

// Estado de una grabación GPS. Cada punto se guarda en el dispositivo antes de enviarse,
// de modo que la conexión puede faltar durante todo el recorrido.
export function useGrabacion({ alSincronizar } = {}) {
    const estado = ref('inactivo') // inactivo | grabando | pausado
    const recorrido = ref(null)
    const trazado = ref([])
    const total = ref(0)
    const pendientes = ref(0)
    const precision = ref(null)
    const aviso = ref('')
    const enLinea = ref(navigator.onLine)
    const sincronizando = ref(false)

    let idVigilancia = null
    let ultimo = null
    let secuencia = 0
    let bloqueoPantalla = null

    const sincronizar = async () => {
        if (!enLinea.value || sincronizando.value) return
        sincronizando.value = true
        try {
            await sincronizarPendientes()
            if (recorrido.value) {
                const puntos = await puntosDelRecorrido(recorrido.value.id_cliente)
                pendientes.value = puntos.filter(punto => !punto.sincronizado).length
            }
            alSincronizar?.()
        } finally {
            sincronizando.value = false
        }
    }

    const pedirBloqueoPantalla = async () => {
        if (!('wakeLock' in navigator) || bloqueoPantalla) return
        try {
            bloqueoPantalla = await navigator.wakeLock.request('screen')
            bloqueoPantalla.addEventListener('release', () => { bloqueoPantalla = null })
        } catch {
            // Sin permiso o sin soporte: la grabación sigue, pero la pantalla puede apagarse.
        }
    }

    const soltarBloqueoPantalla = async () => {
        await bloqueoPantalla?.release().catch(() => {})
        bloqueoPantalla = null
    }

    const registrarPosicion = async (posicion) => {
        const { latitude, longitude, accuracy } = posicion.coords
        precision.value = Math.round(accuracy)
        if (accuracy > PRECISION_MAXIMA_M) {
            aviso.value = 'Señal GPS débil: se omiten los puntos poco precisos.'
            return
        }
        aviso.value = ''
        const actual = [latitude, longitude]
        if (ultimo && distancia(ultimo.par, actual) < DISTANCIA_MINIMA_M && posicion.timestamp - ultimo.t < INTERVALO_MAXIMO_MS) return
        ultimo = { par: actual, t: posicion.timestamp }
        await guardarPunto({
            id_cliente: recorrido.value.id_cliente,
            secuencia: secuencia++,
            latitud: latitude,
            longitud: longitude,
            precision_m: accuracy,
            capturado_en: new Date(posicion.timestamp).toISOString(),
        })
        trazado.value = [...trazado.value, actual]
        total.value += 1
        pendientes.value += 1
        if (total.value % SINCRONIZAR_CADA_PUNTOS === 0) sincronizar()
    }

    const manejarErrorGPS = (error) => {
        if (error.code === 1) {
            aviso.value = 'Permiso de ubicación denegado. Actívalo en el navegador para grabar el recorrido.'
            pausar()
        } else if (error.code === 2) {
            aviso.value = 'No se pudo obtener la ubicación. Comprueba que el GPS esté activado.'
        } else {
            aviso.value = 'La señal GPS tarda en responder. Sigue intentándolo.'
        }
    }

    const comenzar = async () => {
        if (!('geolocation' in navigator)) {
            aviso.value = 'Este dispositivo no permite usar el GPS desde el navegador.'
            return
        }
        aviso.value = ''
        idVigilancia = navigator.geolocation.watchPosition(registrarPosicion, manejarErrorGPS, {
            enableHighAccuracy: true, maximumAge: 0, timeout: 20000,
        })
        estado.value = 'grabando'
        await pedirBloqueoPantalla()
    }

    const detenerVigilancia = async () => {
        if (idVigilancia !== null) navigator.geolocation.clearWatch(idVigilancia)
        idVigilancia = null
        await soltarBloqueoPantalla()
    }

    const iniciar = async (paquete, nombre = '') => {
        const nuevo = {
            id_cliente: crypto.randomUUID(),
            paquete,
            nombre: nombre.trim(),
            iniciado_en: new Date().toISOString(),
            finalizado_en: null,
            creado_sync: false,
            finalizado_sync: false,
            completo: false,
            error: '',
        }
        await guardarRecorrido(nuevo)
        recorrido.value = nuevo
        trazado.value = []
        total.value = 0
        pendientes.value = 0
        precision.value = null
        secuencia = 0
        ultimo = null
        await comenzar()
    }

    async function pausar() {
        await detenerVigilancia()
        if (estado.value === 'grabando') estado.value = 'pausado'
    }

    const reanudar = () => comenzar()

    const finalizar = async () => {
        await detenerVigilancia()
        await actualizarRecorrido(recorrido.value.id_cliente, { finalizado_en: new Date().toISOString() })
        estado.value = 'inactivo'
        recorrido.value = null
        await sincronizar()
    }

    // Tras cerrar la app o recargar, devuelve una grabación sin terminar al estado de pausa.
    const recuperarPendiente = async () => {
        const abierto = (await listarRecorridos()).find(item => !item.finalizado_en)
        if (!abierto) return false
        const puntos = (await puntosDelRecorrido(abierto.id_cliente)).sort((a, b) => a.secuencia - b.secuencia)
        recorrido.value = abierto
        trazado.value = puntos.map(punto => [punto.latitud, punto.longitud])
        total.value = puntos.length
        pendientes.value = puntos.filter(punto => !punto.sincronizado).length
        secuencia = puntos.length ? puntos.at(-1).secuencia + 1 : 0
        const ultimoPunto = puntos.at(-1)
        ultimo = ultimoPunto ? { par: [ultimoPunto.latitud, ultimoPunto.longitud], t: Date.parse(ultimoPunto.capturado_en) } : null
        estado.value = 'pausado'
        return true
    }

    const alConectar = () => { enLinea.value = true; sincronizar() }
    const alDesconectar = () => { enLinea.value = false }
    const alCambiarVisibilidad = () => {
        if (document.visibilityState === 'visible' && estado.value === 'grabando') pedirBloqueoPantalla()
    }
    window.addEventListener('online', alConectar)
    window.addEventListener('offline', alDesconectar)
    document.addEventListener('visibilitychange', alCambiarVisibilidad)

    onBeforeUnmount(() => {
        window.removeEventListener('online', alConectar)
        window.removeEventListener('offline', alDesconectar)
        document.removeEventListener('visibilitychange', alCambiarVisibilidad)
        detenerVigilancia()
    })

    return {
        estado, recorrido, trazado, total, pendientes, precision, aviso, enLinea, sincronizando,
        iniciar, pausar, reanudar, finalizar, recuperarPendiente, sincronizar,
    }
}
