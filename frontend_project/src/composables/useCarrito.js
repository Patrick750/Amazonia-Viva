import { ref, computed, watch } from 'vue';
import axios from '@/api/axios';

// ── Estado Global Singleton ──────────────────────────────────────────────────
const itemsCarrito = ref([]);

/**
 * Obtiene la clave de localStorage específica para el usuario.
 * Si no hay usuario, usa una clave de invitado.
 */
const getStorageKey = () => {
    const email = localStorage.getItem('email');
    return email ? `carrito_amazonia_${email}` : 'carrito_amazonia_invitado';
};

// Cargamos el carrito inicial
const initLocal = () => {
    const key = getStorageKey();
    const saved = localStorage.getItem(key);
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            itemsCarrito.value = parsed.map(i => ({ seleccionado: true, ...i }));
        } catch { itemsCarrito.value = []; }
    } else {
        itemsCarrito.value = [];
    }
};

// Inicialización inmediata (para cuando el módulo se carga)
initLocal();

// Persistimos en localStorage cada vez que el estado cambia
watch(itemsCarrito, (nuevo) => {
    localStorage.setItem(getStorageKey(), JSON.stringify(nuevo));
}, { deep: true });

// ── Composable ───────────────────────────────────────────────────────────────
export function useCarrito() {

    // ── Getters computados ────────────────────────────────────────────
    const tours = computed(() => itemsCarrito.value.filter(i => i.tipo === 'paquete'));
    const productos = computed(() => itemsCarrito.value.filter(i => i.tipo === 'producto'));

    const itemsSeleccionados = computed(() => itemsCarrito.value.filter(i => i.seleccionado));
    const toursSeleccionados = computed(() => itemsSeleccionados.value.filter(i => i.tipo === 'paquete'));
    const productosSeleccionados = computed(() => itemsSeleccionados.value.filter(i => i.tipo === 'producto'));

    const todoSeleccionado = computed(() =>
        itemsCarrito.value.length > 0 && itemsCarrito.value.every(i => i.seleccionado)
    );

    const cartCount = computed(() => itemsCarrito.value.length);

    const subtotalTours = computed(() =>
        toursSeleccionados.value.reduce((sum, i) => sum + (Number(i.precio) * i.cantidad), 0)
    );
    const subtotalProductos = computed(() =>
        productosSeleccionados.value.reduce((sum, i) => sum + (Number(i.precio) * i.cantidad), 0)
    );
    
    const tarifaEcologica = computed(() => Math.round(subtotalTours.value * 0.01));
    const totalFinal = computed(() => subtotalTours.value + subtotalProductos.value + tarifaEcologica.value);

    // ── Acciones ──────────────────────────────────────────────────────────

    /** Sincroniza el carrito local con el del usuario autenticado */
    const cargarDesdeBackend = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const res = await axios.get('api/carrito/');
            if (res.data && Array.isArray(res.data)) {
                itemsCarrito.value = res.data.map(item => ({
                    id: item.item_id, // ID del producto o paquete
                    db_id: item.id,   // ID único de la fila en la tabla Items
                    tipo: item.tipo,
                    nombre: item.nombre,
                    precio: item.precio,
                    imagen: item.imagen,
                    subtitulo: item.subtitulo,
                    cantidad: 1,
                    seleccionado: true
                }));
            }
        } catch (e) {

            console.error('Error al cargar carrito:', e);
        }
    };

    /** Reinicia el estado del carrito (útil al cambiar de cuenta) */
    const resetearCarrito = () => {
        initLocal();
    };

    const agregarItem = (item) => {
        const yaExiste = itemsCarrito.value.find(
            i => i.id === item.id && i.tipo === item.tipo
        );
        if (yaExiste) {
            yaExiste.cantidad = (yaExiste.cantidad || 1) + 1;
        } else {
            itemsCarrito.value = [
                ...itemsCarrito.value,
                { ...item, cantidad: 1, seleccionado: true }
            ];
        }
    };

    const eliminarItem = (id, tipo) => {
        // 1. Sincronizar con backend si existe db_id
        const item = itemsCarrito.value.find(i => i.id === id && i.tipo === tipo);
        if (item && item.db_id) {
            axios.delete(`api/carrito/${item.db_id}/`).catch(err => {
                console.error('Error al eliminar ítem del servidor:', err);
            });
        }

        // 2. Eliminar localmente
        itemsCarrito.value = itemsCarrito.value.filter(
            i => !(i.id === id && i.tipo === tipo)
        );
    };


    const actualizarCantidad = (id, tipo, nuevaCantidad) => {
        const item = itemsCarrito.value.find(i => i.id === id && i.tipo === tipo);
        if (item) {
            item.cantidad = Math.max(1, Number(nuevaCantidad));
        }
    };

    const vaciarCarrito = () => {
        itemsCarrito.value = [];
    };

    const toggleSeleccion = (id, tipo) => {
        const item = itemsCarrito.value.find(i => i.id === id && i.tipo === tipo);
        if (item) item.seleccionado = !item.seleccionado;
    };

    const seleccionarTodos = () => {
        itemsCarrito.value.forEach(i => { i.seleccionado = true; });
    };

    const deseleccionarTodos = () => {
        itemsCarrito.value.forEach(i => { i.seleccionado = false; });
    };

    const estaEnCarrito = (id, tipo) => {
        return itemsCarrito.value.some(i => i.id === id && i.tipo === tipo);
    };

    return {
        itemsCarrito,
        tours,
        productos,
        itemsSeleccionados,
        toursSeleccionados,
        productosSeleccionados,
        todoSeleccionado,
        cartCount,
        subtotalTours,
        subtotalProductos,
        tarifaEcologica,
        totalFinal,
        agregarItem,
        eliminarItem,
        actualizarCantidad,
        vaciarCarrito,
        estaEnCarrito,
        toggleSeleccion,
        seleccionarTodos,
        deseleccionarTodos,
        cargarDesdeBackend,
        resetearCarrito
    };
}
