import clienteAxios from '@/api/axios'

export const pedirActividades = async () => {
    const response = await clienteAxios.get('api/actividades/')
    if (!Array.isArray(response.data)) {
        throw new Error('La API de actividades no devolvió una lista válida.')
    }
    return response.data
}
