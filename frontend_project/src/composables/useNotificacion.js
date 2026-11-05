import { reactive } from 'vue';

const notificacionState = reactive({
    mostrar: false,
    mensaje: '',
    tipo: 'exito' // 'exito', 'aviso' (o 'warning') o 'error'
});

let timeoutId = null;

export function useNotificacion() {
    const mostrarNotificacion = (mensaje, tipo = 'exito', duracion = 4000) => {
        notificacionState.mensaje = mensaje;
        notificacionState.tipo = tipo;
        notificacionState.mostrar = true;
        
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        
        timeoutId = setTimeout(() => {
            notificacionState.mostrar = false;
        }, duracion);
    };

    const cerrarNotificacion = () => {
        notificacionState.mostrar = false;
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
    };

    return {
        notificacion: notificacionState,
        mostrarNotificacion,
        cerrarNotificacion
    };
}
