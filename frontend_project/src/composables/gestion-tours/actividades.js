import clienteAxios from '@/api/axios'

export const pedirActividades = async () => {
    try{
        const response = await clienteAxios.get('api/actividades/')
        return response.data
        
    }catch (error){
        console.error('Hubo un error '+error)
    }
}