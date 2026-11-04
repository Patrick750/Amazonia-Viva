import { ref } from 'vue'
import clienteAxios from '@/api/axios'

// Foto de perfil y portada de la cuenta: agregar, reemplazar y eliminar.
// El servidor vuelve a validar formato y tamaño; aquí solo se evita subir un archivo que será rechazado.
const FORMATOS = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
const MAX_BYTES = 20 * 1024 * 1024

// El encabezado de la aplicación muestra la foto de perfil y se entera por este evento.
const avisarEncabezado = (url) => {
    try {
        if (url) localStorage.setItem('foto_url', url)
        else localStorage.removeItem('foto_url')
    } catch { /* almacenamiento bloqueado: el encabezado se actualiza igual con el evento */ }
    window.dispatchEvent(new CustomEvent('perfil:foto-actualizada', { detail: { foto_url: url } }))
}

const mensajeDeError = (fallo, porDefecto) => {
    if (!fallo.response) return 'No pudimos conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.'
    return fallo.response.data?.error || porDefecto
}

export function useImagenPerfil() {
    const ocupado = ref(false)

    // tipo: 'perfil' | 'portada'. Devuelve { url } si salió bien o { error } con el motivo.
    const subir = async (tipo, archivo) => {
        if (!FORMATOS.includes(archivo.type)) return { error: 'Solo se permiten imágenes JPG, PNG, WEBP o GIF.' }
        if (archivo.size > MAX_BYTES) return { error: `La imagen no puede superar los ${MAX_BYTES / (1024 * 1024)} MB.` }
        ocupado.value = true
        try {
            const datos = new FormData()
            datos.append('foto', archivo)
            const { data } = await clienteAxios.post(`api/perfil/foto/?tipo=${tipo}`, datos, { headers: { 'Content-Type': 'multipart/form-data' } })
            if (tipo === 'perfil') avisarEncabezado(data.foto_url)
            return { url: data.foto_url }
        } catch (fallo) {
            return { error: mensajeDeError(fallo, 'No se pudo guardar la imagen. Inténtalo de nuevo.') }
        } finally {
            ocupado.value = false
        }
    }

    const eliminar = async (tipo) => {
        ocupado.value = true
        try {
            await clienteAxios.delete(`api/perfil/foto/?tipo=${tipo}`)
            if (tipo === 'perfil') avisarEncabezado(null)
            return { url: null }
        } catch (fallo) {
            return { error: mensajeDeError(fallo, 'No se pudo eliminar la imagen. Inténtalo de nuevo.') }
        } finally {
            ocupado.value = false
        }
    }

    return { ocupado, subir, eliminar }
}
