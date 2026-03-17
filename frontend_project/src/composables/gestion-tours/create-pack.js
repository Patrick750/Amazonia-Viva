import { ref } from 'vue'
import clienteAxios from '@/api/axios'

export function GuardarRegistro(){
    const guardarDatos = async (datos) => {
        const response = await clienteAxios.post('api/createnewpack/', datos)
        return response.data
    }
    return { guardarDatos }
}
