import { onBeforeUnmount, ref } from 'vue'
import clienteAxios from '@/api/axios'

// Ver en el mapa a las demás personas que hacen hoy el mismo paquete (solo si cada una lo decide).
// Compartir es voluntario y recíproco: quien no comparte tampoco ve a los demás. La posición viaja al servidor,
// por lo que requiere internet; el servidor la borra al dejar de compartir o pasados 5 minutos sin actualizarse.
const INTERVALO_MS = 10000
const CLAVE = 'grupo_compartir_v1'

const leerElegido = (clave) => {
    try {
        return JSON.parse(localStorage.getItem(CLAVE) || '{}')[clave] === true
    } catch {
        return false
    }
}

const recordarElegido = (clave, valor) => {
    try {
        const datos = JSON.parse(localStorage.getItem(CLAVE) || '{}')
        // Solo se conserva lo de hoy: cada día la persona vuelve a decidir.
        const hoy = clave.split(':')[1]
        const vigentes = Object.fromEntries(Object.entries(datos).filter(([k]) => k.endsWith(`:${hoy}`)))
        vigentes[clave] = valor
        localStorage.setItem(CLAVE, JSON.stringify(vigentes))
    } catch { /* almacenamiento bloqueado: se decide de nuevo la próxima vez */ }
}

export function useGrupo(obtenerPosicion) {
    const compartiendo = ref(false)
    const personas = ref([])
    const error = ref('')
    let paquete = null
    let clave = ''
    let temporizador = null

    const enviar = async () => {
        const posicion = obtenerPosicion()
        if (!compartiendo.value || !posicion || paquete === null) return
        try {
            const { data } = await clienteAxios.post(`api/turista/paquetes/${paquete}/grupo/`, {
                latitud: posicion.lat, longitud: posicion.lng, precision_m: posicion.precision,
            })
            personas.value = data.personas
            error.value = ''
        } catch (fallo) {
            if (fallo.response?.status === 403) {
                error.value = 'Solo puedes compartir tu ubicación el día de tu experiencia.'
                detenerLocal()
            } else if (!fallo.response) {
                error.value = 'Sin conexión: no se puede ver a las demás personas hasta recuperar internet.'
            }
        }
    }

    const detenerLocal = () => {
        compartiendo.value = false
        clearInterval(temporizador)
        temporizador = null
        personas.value = []
    }

    const empezar = () => {
        compartiendo.value = true
        enviar()
        temporizador = setInterval(enviar, INTERVALO_MS)
    }

    const dejar = async () => {
        const habiaCompartido = compartiendo.value
        detenerLocal()
        if (habiaCompartido && paquete !== null) await clienteAxios.delete(`api/turista/paquetes/${paquete}/grupo/`).catch(() => {})
    }

    // Se llama al elegir paquete. Lo que la persona decidió hoy para ese paquete se respeta.
    const preparar = (idPaquete, fecha) => {
        dejar()
        paquete = idPaquete
        clave = `${idPaquete}:${fecha}`
        error.value = ''
        if (leerElegido(clave)) empezar()
    }

    const alternar = async (activo) => {
        if (activo) {
            if (!compartiendo.value) empezar()
        } else {
            await dejar()
        }
        if (clave) recordarElegido(clave, activo)
    }

    onBeforeUnmount(dejar)

    return { compartiendo, personas, error, preparar, alternar, enviarAhora: enviar }
}
