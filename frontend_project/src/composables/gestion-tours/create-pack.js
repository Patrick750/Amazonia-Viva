import { ref } from 'vue'
import clienteAxios from '@/api/axios'

// composable.js
export function GuardarRegistro(){
    const guardarDatos = async (datos, id = null) => {
        if (id) {
            const response = await clienteAxios.put(`api/updatepack/${id}/`, datos)
            return response.data
        } else {
            const response = await clienteAxios.post('api/createnewpack/', datos)
            return response.data
        }
    }
    return { guardarDatos }
}