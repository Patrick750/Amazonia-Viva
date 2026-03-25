import { ref } from 'vue';
import axios from '@/api/axios';

export function useCatalogo() {
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

    return { tours, productos, cargandoTours, cargandoProductos, errorTours, errorProductos, cargarTours, cargarProductos };
}
