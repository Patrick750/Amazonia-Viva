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

const esIOS = () => /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
const esAndroid = () => /android/i.test(navigator.userAgent)
const appInstalada = () => window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true

// Qué revisar en el dispositivo cuando el bloqueo no está en el permiso del sitio. En el teléfono casi siempre
// es la ubicación del sistema o el permiso del navegador (o de la app instalada) en los ajustes.
function ayudaDelSistema() {
    const instalada = appInstalada()
        ? ' Estás usando la app instalada: su permiso es independiente del navegador y se cambia en los ajustes de esa app.'
        : ''
    if (esAndroid()) {
        return `En tu teléfono Android: 1) activa «Ubicación» en el panel de ajustes rápidos; 2) Ajustes › Aplicaciones › ${appInstalada() ? 'Amazonia Viva' : 'Chrome'} › Permisos › Ubicación › «Permitir solo mientras se usa la app» y activa «Usar ubicación precisa»; 3) en Chrome: ⋮ › Configuración › Configuración de sitios › Ubicación, y permite este sitio.${instalada}`
    }
    if (esIOS()) {
        return `En tu iPhone/iPad: 1) Ajustes › Privacidad y seguridad › Localización, y actívala; 2) en esa lista, entra en «Safari (sitios web)» y elige «Al usar la app»; 3) en Safari: botón aA › Configuración del sitio web › Ubicación › Permitir.${instalada}`
    }
    return 'Windows: Configuración › Privacidad › Ubicación. macOS: Ajustes › Privacidad › Servicios de localización. Linux (GNOME): Configuración › Privacidad › Servicios de ubicación.'
}

export async function explicarErrorUbicacion(error) {
    const sitio = window.location.origin
    const permiso = await estadoPermisoUbicacion()
    const detalle = error?.message ? ` (detalle del navegador: «${error.message}»)` : ''
    console.warn('No se pudo leer la ubicación', { codigo: error?.code, mensaje: error?.message, permiso, sitio })

    if (error?.code === 1) {
        const ayuda = ayudaDelSistema()
        if (permiso === 'granted') {
            return `El navegador sí permite la ubicación para ${sitio}, pero el sistema del dispositivo la está bloqueando. ${ayuda}${detalle}`
        }
        if (permiso === 'denied') {
            return `La ubicación está bloqueada para ${sitio}. Cámbiala a «Permitir» en el candado o en la configuración del sitio, recarga la página y vuelve a pulsar el botón. Los permisos valen por dirección exacta: si diste permiso en otra dirección, hay que darlo también aquí. ${ayuda}${detalle}`
        }
        return `No se recibió permiso de ubicación para ${sitio}. Si al pulsar el botón no apareció ningún aviso de «Permitir», el bloqueo está en el dispositivo. ${ayuda}${detalle}`
    }
    if (error?.code === 2) {
        return `No se pudo determinar tu posición. Comprueba que el GPS o los servicios de ubicación del dispositivo estén activados y que tengas conexión a internet.${detalle}`
    }
    if (error?.code === 3) {
        return `La ubicación tardó demasiado en responder. Sal a un lugar abierto y vuelve a intentarlo.${detalle}`
    }
    return `No se pudo obtener tu ubicación. Inténtalo de nuevo.${detalle}`
}
