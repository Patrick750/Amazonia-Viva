import { ref } from 'vue';
import axios from '@/api/axios';
import { useNotificacion } from './useNotificacion';
import { useCarrito } from './useCarrito';

// Estado Global para uso como Singleton
const tours = ref([]);
const productos = ref([]);
const categoriasTours = ref([]);

const cargandoTours = ref(false);
const cargandoProductos = ref(false);
const cargandoCategorias = ref(false);

const errorTours = ref(null);
const errorProductos = ref(null);

export function useCatalogo() {
    const { mostrarNotificacion } = useNotificacion();
    const { agregarItem } = useCarrito();

    const cargarTours = async () => {
        if (tours.value.length > 0) return; // Evitar recargar
        cargandoTours.value = true;
        errorTours.value = null;
        try {
            const res = await axios.get('api/catalogo/tours/');
            tours.value = res.data;
        } catch (e) {
            errorTours.value = 'No se pudieron cargar los tours.';
        } finally {
            cargandoTours.value = false;
        }
    };

    const cargarProductos = async (tipo = null) => {
        cargandoProductos.value = true;
        errorProductos.value = null;
        try {
            const params = tipo ? { tipo } : {};
            const res = await axios.get('api/catalogo/productos/', { params });
            productos.value = res.data;
        } catch (e) {
            errorProductos.value = 'No se pudieron cargar los productos.';
        } finally {
            cargandoProductos.value = false;
        }
    };

    const cargarCategorias = async () => {
        if (categoriasTours.value.length > 0) return; // Evitar recargar
        cargandoCategorias.value = true;
        try {
            const res = await axios.get('api/categorias-paquetes/');
            categoriasTours.value = res.data;
        } catch (e) {
            console.error('Error al cargar categorias de tours:', e);
        } finally {
            cargandoCategorias.value = false;
        }
    };

    const obtenerTourPorId = async (id) => {
        try {
            const res = await axios.get(`api/catalogo/tours/${id}/`);
            return res.data;
        } catch (e) {
            console.error('Error al obtener tour:', e);
            return null;
        }
    };

    const obtenerProductoPorId = async (id) => {
        try {
            const res = await axios.get(`api/catalogo/productos/${id}/`);
            return res.data;
        } catch (e) {
            console.error('Error al obtener producto:', e);
            return null;
        }
    };

    const toggleFavorito = async (id, tipo = 'paquete') => {
        try {
            const data = tipo === 'producto' ? { producto: id } : { paquetes: id };
            await axios.post('api/favoritos/', data);
            mostrarNotificacion('Agregado a favoritos', 'exito');
            return true;
        } catch (e) {
            console.error('Error al toggle favorito:', e);
            return false;
        }
    };

    /**
     * Agrega un ítem al carrito local (localStorage via useCarrito).
     * @param {number} id - ID del item
     * @param {number} precio - Precio unitario
     * @param {'paquete'|'producto'} tipo
     * @param {Object} extra - Datos adicionales { nombre, imagen, subtitulo, fecha_reserva }
     */
    const agregarAlCarrito = (id, precio, tipo = 'paquete', extra = {}) => {
        // 1. Agregar localmente para feedback inmediato
        agregarItem({
            id,
            precio,
            tipo,
            nombre: extra.nombre || 'Ítem',
            imagen: extra.imagen || null,
            subtitulo: extra.subtitulo || '',
            fecha_reserva: extra.fecha_reserva || null,
            tipo_paquete: extra.tipo_paquete || null,
            fecha_realizacion: extra.fecha_realizacion || null,
        });

        // 2. Sincronizar con el backend si está autenticado
        const token = localStorage.getItem('token');
        if (token) {
            const data = tipo === 'producto' 
                ? { producto: id, precio } 
                : { paquetes: id, precio, fecha_reserva: extra.fecha_reserva || null };
            
            axios.post('api/carrito/', data).then(res => {
                // Actualizar con el ID de la base de datos para permitir borrado posterior
                const itemLocal = itemsCarrito.value.find(i => i.id === id && i.tipo === tipo);
                if (itemLocal && res.data.id) {
                    itemLocal.db_id = res.data.id;
                }
            }).catch(err => {
                console.error('Error al sincronizar ítem con el servidor:', err);
            });

        }

        mostrarNotificacion('¡Agregado al carrito!', 'exito');
        return true;
    };

    /**
     * Consulta cupos disponibles para un paquete en una fecha dada.
     * @param {number} paqueteId
     * @param {string} fecha - Formato YYYY-MM-DD
     */
    const obtenerCuposDisponibles = async (paqueteId, fecha = null) => {
        try {
            const params = fecha ? `?fecha=${fecha}` : '';
            const res = await axios.get(`api/cupos/${paqueteId}/${params}`);
            return res.data;
        } catch (e) {
            console.error('Error al obtener cupos:', e);
            return null;
        }
    };


    return { 
        tours, productos, categoriasTours,
        cargandoTours, cargandoProductos, cargandoCategorias,
        errorTours, errorProductos, 
        cargarTours, cargarProductos, cargarCategorias,
        obtenerTourPorId, obtenerProductoPorId, toggleFavorito,
        agregarAlCarrito, obtenerCuposDisponibles
    };
}
