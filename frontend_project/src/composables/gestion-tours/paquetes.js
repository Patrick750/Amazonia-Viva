import clienteAxios from "@/api/axios";

export const paquetes = async () => {
    try{
        const response = await clienteAxios.get('api/pack/')
        return response.data
    }catch (error){
        console.error('Hubo un error al traer lo datos: '+ error)
    }
}

export const eliminarPaquete = async (id) => {
    try {
        const response = await clienteAxios.delete(`api/deletepack/${id}/`);
        return response.data;
    } catch (error) {
        console.error('Hubo un error al eliminar: ' + error);
        throw error;
    }
}

