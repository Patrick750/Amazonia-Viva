// Guarda la sesión con las mismas claves que ya lee el resto de la aplicación.
// El login y el registro comparten esta función para que ambos conserven también el refresh_token.
export function guardarSesion(datos) {
    const { usuario } = datos
    localStorage.setItem('token', datos.access)
    localStorage.setItem('refresh_token', datos.refresh)
    localStorage.setItem('nombre', usuario.nombre)
    localStorage.setItem('apellido', usuario.apellido)
    localStorage.setItem('nombre_usuario', usuario.username)
    localStorage.setItem('nombre_empresa', usuario.nombre_empresa)
    localStorage.setItem('nombre_agencia', usuario.nombre_agencia)
    localStorage.setItem('rol', usuario.group)
}

// Traduce un fallo de red o de la API al mensaje que se muestra en pantalla.
// Devuelve una cadena vacía cuando el error depende del formulario y debe resolverlo cada pantalla.
export function mensajeDeConexion(error) {
    if (!error.response) return 'No pudimos conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.'
    if (error.response.status === 429) return 'Hiciste demasiados intentos seguidos. Espera un minuto y vuelve a intentarlo.'
    if (error.response.status >= 500) return 'El servicio no está disponible por ahora. Inténtalo de nuevo en unos minutos.'
    return ''
}
