import { ref } from 'vue'
import clienteAxios from '@/api/axios'

// composable.js
export function GuardarRegistro(){
    const guardarDatos = async (datos) => {
        // ENVIAR DIRECTAMENTE EL DATOS (Que ya es un FormData)
        // SIN configuraciones extra de headers
        const response = await clienteAxios.post('api/createnewpack/', datos)
        return response.data
    }
    return { guardarDatos }
}