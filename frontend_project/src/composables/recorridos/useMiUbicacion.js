import { onBeforeUnmount, ref } from 'vue'

// Posición actual del dispositivo para mostrarla en el mapa, independiente de la grabación:
// se ve antes de empezar, mientras se graba y aunque un punto se descarte por poca precisión.
// No guarda nada: solo alimenta lo que se dibuja en pantalla.
export function useMiUbicacion() {
    const posicion = ref(null) // { lat, lng, precision }
    const estado = ref('buscando') // buscando | activa | denegada | sin_gps | no_disponible
    let idVigilancia = null

    const alPosicion = ({ coords }) => {
        posicion.value = { lat: coords.latitude, lng: coords.longitude, precision: Math.round(coords.accuracy) }
        estado.value = 'activa'
    }

    const alError = (error) => {
        if (error.code === 1) estado.value = 'denegada'
        else if (error.code === 2) estado.value = 'sin_gps'
        // Código 3 (tiempo agotado): se sigue esperando el siguiente aviso del GPS.
    }

    const detener = () => {
        if (idVigilancia !== null) navigator.geolocation.clearWatch(idVigilancia)
        idVigilancia = null
    }

    const iniciar = () => {
        detener()
        if (!('geolocation' in navigator) || !window.isSecureContext) {
            estado.value = 'no_disponible'
            return
        }
        estado.value = 'buscando'
        idVigilancia = navigator.geolocation.watchPosition(alPosicion, alError, {
            enableHighAccuracy: true, maximumAge: 2000, timeout: 20000,
        })
    }

    onBeforeUnmount(detener)

    return { posicion, estado, iniciar, detener }
}
