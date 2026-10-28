import clienteAxios from '@/api/axios'
import {
    actualizarRecorrido, listarRecorridos, marcarSincronizados, obtenerRecorrido, puntosPendientes,
} from './almacenLocal'

const TAMANO_LOTE = 200
let enCurso = null

// Fallos que se resuelven solos: sin red, servidor caído o límite de intentos.
const esTemporal = (error) => !error.response || error.response.status >= 500 || error.response.status === 429

// Envía un recorrido en orden: crearlo, sus puntos por lotes y, si ya terminó, finalizarlo.
// Todos los envíos son idempotentes en el servidor, por lo que repetirlos tras un corte no duplica datos.
export async function sincronizarRecorrido(id) {
    let recorrido = await obtenerRecorrido(id)
    if (!recorrido) return { estado: 'inexistente' }
    try {
        if (!recorrido.creado_sync) {
            await clienteAxios.post('api/recorridos/', {
                id_cliente: id,
                paquete: recorrido.paquete,
                nombre: recorrido.nombre,
                iniciado_en: recorrido.iniciado_en,
            })
            recorrido = await actualizarRecorrido(id, { creado_sync: true, error: '' })
        }
        for (;;) {
            const lote = await puntosPendientes(id, TAMANO_LOTE)
            if (!lote.length) break
            await clienteAxios.post(`api/recorridos/${id}/puntos/`, {
                puntos: lote.map(({ secuencia, latitud, longitud, precision_m, capturado_en }) => ({
                    secuencia, latitud, longitud, precision_m, capturado_en,
                })),
            })
            await marcarSincronizados(id, lote.map(punto => punto.secuencia))
        }
        if (recorrido.finalizado_en && !recorrido.finalizado_sync) {
            await clienteAxios.post(`api/recorridos/${id}/finalizar/`, { finalizado_en: recorrido.finalizado_en })
            await actualizarRecorrido(id, { finalizado_sync: true, completo: true })
        }
        return { estado: 'ok' }
    } catch (error) {
        if (esTemporal(error)) return { estado: 'sin_conexion' }
        const mensaje = error.response?.data?.detail || 'El servidor rechazó los datos de este recorrido.'
        await actualizarRecorrido(id, { error: mensaje })
        return { estado: 'error', mensaje }
    }
}

// Sincroniza todo lo pendiente. Si ya hay una sincronización en curso, comparte su resultado.
export function sincronizarPendientes() {
    if (!enCurso) {
        enCurso = (async () => {
            const resultados = []
            for (const recorrido of await listarRecorridos()) {
                if (recorrido.completo || recorrido.error) continue
                resultados.push(await sincronizarRecorrido(recorrido.id_cliente))
                if (resultados.at(-1).estado === 'sin_conexion') break
            }
            return resultados
        })().finally(() => { enCurso = null })
    }
    return enCurso
}

// Permite volver a intentar un recorrido que el servidor había rechazado.
export const reintentarRecorrido = async (id) => {
    await actualizarRecorrido(id, { error: '' })
    return sincronizarRecorrido(id)
}
