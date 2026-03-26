import { ref } from 'vue';
import axios from '@/api/axios';
import { useUserStats } from './useUserStats';
import { useNotificacion } from './useNotificacion';

export function useCatalogo() {
    const { mostrarNotificacion } = useNotificacion();
    const { updateStats } = useUserStats();
    const tours = ref([]);
    const productos = ref([]);
    const cargandoTours = ref(false);
    const cargandoProductos = ref(false);
    const errorTours = ref(null);
    const errorProductos = ref(null);

    const cargarTours = async () => {
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

    const categoriasTours = ref([]);
    const cargandoCategorias = ref(false);

    const cargarCategorias = async () => {
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
            updateStats(); // Actualizar contadores globalmente
            return true;
        } catch (e) {
            console.error('Error al toggle favorito:', e);
            return false;
        }
    };

    const agregarAlCarrito = async (id, precio, tipo = 'paquete') => {
        try {
            const data = tipo === 'producto' ? { producto: id, precio: precio } : { paquetes: id, precio: precio };
            await axios.post('api/carrito/', data);
            mostrarNotificacion('Agregado al carrito', 'exito');
            updateStats(); // Actualizar contadores globalmente
            return true;
        } catch (e) {
            console.error('Error al agregar al carrito:', e);
            return false;
        }
    };

    return { 
        tours, productos, categoriasTours,
        cargandoTours, cargandoProductos, cargandoCategorias,
        errorTours, errorProductos, 
        cargarTours, cargarProductos, cargarCategorias,
        obtenerTourPorId, obtenerProductoPorId, toggleFavorito, agregarAlCarrito
    };
}
