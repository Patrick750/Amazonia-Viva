// Explica por qué falló la lectura de la ubicación. El código 1 («denegado») puede venir de tres sitios
// distintos —el permiso del navegador para este sitio, el sistema operativo o un origen distinto al
// que se autorizó— y cada uno se arregla de forma diferente.

export async function estadoPermisoUbicacion() {
    try {
        return (await navigator.permissions.query({ name: 'geolocation' })).state // granted | denied | prompt
    } catch {
        return 'desconocido'
    }
}

const AYUDA_SISTEMA = 'Windows: Configuración › Privacidad › Ubicación. macOS: Ajustes › Privacidad › Servicios de localización. Linux (GNOME): Configuración › Privacidad › Servicios de ubicación.'

export async function explicarErrorUbicacion(error) {
    const sitio = window.location.origin
    const permiso = await estadoPermisoUbicacion()
    const detalle = error?.message ? ` (detalle del navegador: «${error.message}»)` : ''
    console.warn('No se pudo leer la ubicación', { codigo: error?.code, mensaje: error?.message, permiso, sitio })

    if (error?.code === 1) {
        if (permiso === 'granted') {
            return `El navegador sí permite la ubicación para ${sitio}, pero el sistema operativo la está bloqueando para el navegador. Activa los servicios de ubicación del sistema y permite el acceso al navegador. ${AYUDA_SISTEMA}${detalle}`
        }
        if (permiso === 'denied') {
            return `El navegador tiene bloqueada la ubicación para ${sitio}. Pulsa el candado de la barra de direcciones › Ubicación › Permitir, recarga la página y vuelve a pulsar el botón. Los permisos valen por dirección exacta: si diste permiso en otra (por ejemplo localhost y 127.0.0.1 cuentan como sitios distintos), tienes que darlo también aquí.${detalle}`
        }
        return `El navegador no concedió el permiso de ubicación para ${sitio}. Cuando pulses el botón aparecerá un aviso del navegador: elige «Permitir».${detalle}`
    }
    if (error?.code === 2) {
        return `No se pudo determinar tu posición. Comprueba que el GPS o los servicios de ubicación del dispositivo estén activados y que tengas conexión a internet.${detalle}`
    }
    if (error?.code === 3) {
        return `La ubicación tardó demasiado en responder. Sal a un lugar abierto y vuelve a intentarlo.${detalle}`
    }
    return `No se pudo obtener tu ubicación. Inténtalo de nuevo.${detalle}`
}
