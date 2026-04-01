import { ref, computed, watch } from 'vue';

// ── Clave en localStorage ────────────────────────────────────────────────────
const STORAGE_KEY = 'carrito_amazonia';

// ── Estado Global Singleton ──────────────────────────────────────────────────
const itemsCarrito = ref([]);

// Cargamos desde localStorage una sola vez al importar el módulo
const saved = localStorage.getItem(STORAGE_KEY);
if (saved) {
    try {
        const parsed = JSON.parse(saved);
        // Garantizamos que todos los ítems tengan el campo seleccionado
        itemsCarrito.value = parsed.map(i => ({ seleccionado: true, ...i }));
    } catch { itemsCarrito.value = []; }
}

// Persistimos en localStorage cada vez que el estado cambia
watch(itemsCarrito, (nuevo) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nuevo));
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
    // Tarifa ecológica simbólica del 1% del subtotal de tours
    const tarifaEcologica = computed(() => Math.round(subtotalTours.value * 0.01));
    const totalFinal = computed(() => subtotalTours.value + subtotalProductos.value + tarifaEcologica.value);

    // ── Acciones ──────────────────────────────────────────────────────────

    /**
     * Agrega un ítem al carrito.
     * Si ya existe (mismo id y tipo), incrementa la cantidad.
     * @param {Object} item - { id, nombre, precio, imagen, tipo ('paquete'|'producto'), subtitulo }
     */
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

    /**
     * Elimina completamente un ítem del carrito.
     * @param {number|string} id
     * @param {string} tipo - 'paquete' o 'producto'
     */
    const eliminarItem = (id, tipo) => {
        itemsCarrito.value = itemsCarrito.value.filter(
            i => !(i.id === id && i.tipo === tipo)
        );
    };

    /**
     * Actualizar la cantidad de un ítem (mínimo 1).
     * @param {number|string} id
     * @param {string} tipo
     * @param {number} nuevaCantidad
     */
    const actualizarCantidad = (id, tipo, nuevaCantidad) => {
        const item = itemsCarrito.value.find(i => i.id === id && i.tipo === tipo);
        if (item) {
            item.cantidad = Math.max(1, Number(nuevaCantidad));
        }
    };

    /** Vacía todo el carrito */
    const vaciarCarrito = () => {
        itemsCarrito.value = [];
    };

    /** Verifica si un ítem ya está en el carrito */    /**
     * Alterna el estado seleccionado de un ítem.
     */
    const toggleSeleccion = (id, tipo) => {
        const item = itemsCarrito.value.find(i => i.id === id && i.tipo === tipo);
        if (item) item.seleccionado = !item.seleccionado;
    };

    /** Selecciona todos los ítems */
    const seleccionarTodos = () => {
        itemsCarrito.value.forEach(i => { i.seleccionado = true; });
    };

    /** Deselecciona todos los ítems */
    const deseleccionarTodos = () => {
        itemsCarrito.value.forEach(i => { i.seleccionado = false; });
    };

    const estaEnCarrito = (id, tipo) => {
        return itemsCarrito.value.some(i => i.id === id && i.tipo === tipo);
    };

    return {
        // Estado
        itemsCarrito,
        tours,
        productos,
        itemsSeleccionados,
        toursSeleccionados,
        productosSeleccionados,
        todoSeleccionado,
        // Contadores y totales
        cartCount,
        subtotalTours,
        subtotalProductos,
        tarifaEcologica,
        totalFinal,
        // Acciones
        agregarItem,
        eliminarItem,
        actualizarCantidad,
        vaciarCarrito,
        estaEnCarrito,
        toggleSeleccion,
        seleccionarTodos,
        deseleccionarTodos,
    };
}
