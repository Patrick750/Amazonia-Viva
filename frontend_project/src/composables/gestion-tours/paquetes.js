import clienteAxios from "@/api/axios";

export const paquetes = async () => {
    try{
        const response = await clienteAxios.get('api/pack/')
        return response.data
    }catch (error){
        console.error('Hubo un error al traer lo datos: '+ error)
    }
}

