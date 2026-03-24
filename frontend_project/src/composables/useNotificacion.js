import { reactive } from 'vue';

const notificacionState = reactive({
    mostrar: false,
    mensaje: '',
    tipo: 'exito' // 'exito' o 'error'
});

let timeoutId = null;

export function useNotificacion() {
    const mostrarNotificacion = (mensaje, tipo = 'exito') => {
        notificacionState.mensaje = mensaje;
        notificacionState.tipo = tipo;
        notificacionState.mostrar = true;
        
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        
        timeoutId = setTimeout(() => {
            notificacionState.mostrar = false;
        }, 4000);
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
