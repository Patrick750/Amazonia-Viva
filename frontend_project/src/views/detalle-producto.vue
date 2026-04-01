<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCatalogo } from '@/composables/useCatalogo';
import { useNotificacion } from '@/composables/useNotificacion';

const route = useRoute();
const router = useRouter();
const { obtenerProductoPorId, toggleFavorito, agregarAlCarrito } = useCatalogo();
const { mostrarNotificacion } = useNotificacion();

const producto = ref(null);
const cargando = ref(true);
const id = route.params.id;
const imagenSeleccionadaIdx = ref(0);
const rol = ref(localStorage.getItem('rol'));
const mostrarTooltip = ref(false);
const tooltipPos = ref({ x: 0, y: 0 });
let tooltipTimeout = null;

onMounted(async () => {
    producto.value = await obtenerProductoPorId(id);
    cargando.value = false;
});

const estrellas = (rating) => {
    const r = Math.min(5, Math.max(0, Number(rating || 0)));
    const llenas = Math.floor(r);
    const media = r - llenas >= 0.5 ? 1 : 0;
    const vacias = 5 - llenas - media;
    return [
        ...Array(llenas).fill('full'),
        ...Array(media).fill('half'),
        ...Array(vacias).fill('empty'),
    ];
};

const handleAccion = async (tipo, event) => {
    if (rol.value === 'proveedor') {
        const rect = event.currentTarget.getBoundingClientRect();
        tooltipPos.value = { 
            x: rect.left + rect.width / 2, 
            y: rect.top - 10 
        };
        mostrarTooltip.value = true;
        
        if (tooltipTimeout) clearTimeout(tooltipTimeout);
        tooltipTimeout = setTimeout(() => {
            mostrarTooltip.value = false;
        }, 3000);
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        mostrarNotificacion('Inicia sesión para realizar esta acción.', 'warning');
        router.push('/auth/login');
        return;
    }

    if (tipo === 'carrito') {
        agregarAlCarrito(
            producto.value.id,
            producto.value.precio,
            'producto',
            {
                nombre: producto.value.nombre,
                imagen: imagenPrincipal.value || null,
                subtitulo: producto.value.nombre_categoria || '',
            }
        );
    } else if (tipo === 'favorito') {
        await toggleFavorito(producto.value.id, 'producto');
    }
};

const imagenesObj = computed(() => {
    // Si no hay imágenes en la relación ProductoImagen, formamos un array con la de portada si existe
    if (producto.value && producto.value.imagen_producto && producto.value.imagen_producto.length > 0) {
        return producto.value.imagen_producto.map(img => img.url || img.imagen).filter(Boolean);
    }
    // Backward compatibility por si solo tiene imagen_portada principal
    if (producto.value?.imagen_portada) return [producto.value.imagen_portada];
    return [];
});

const imagenPrincipal = computed(() => {
    if (imagenesObj.value.length > 0) {
        return imagenesObj.value[imagenSeleccionadaIdx.value];
    }
    return null;
});

const siguienteImagen = () => {
    if (imagenesObj.value.length > 1) {
        imagenSeleccionadaIdx.value = (imagenSeleccionadaIdx.value + 1) % imagenesObj.value.length;
    }
};

const anteriorImagen = () => {
    if (imagenesObj.value.length > 1) {
        imagenSeleccionadaIdx.value = (imagenSeleccionadaIdx.value - 1 + imagenesObj.value.length) % imagenesObj.value.length;
    }
};

// Mapeo seguro de características JSON
const caracteristicasList = computed(() => {
    if (!producto.value?.caracteristicas) return [];
    try {
        const chars = typeof producto.value.caracteristicas === 'string' 
            ? JSON.parse(producto.value.caracteristicas) 
            : producto.value.caracteristicas;
            
        // Convertir diccionario a array de {key, value}
        if (typeof chars === 'object' && !Array.isArray(chars)) {
            return Object.entries(chars).map(([k, v]) => ({ key: k, value: v }));
        }
        return Array.isArray(chars) ? chars : [];
    } catch {
        return [];
    }
});

const getCaracteristica = (claveBuscada) => {
    if (!producto.value?.caracteristicas) return null;
    try {
        const chars = typeof producto.value.caracteristicas === 'string'
            ? JSON.parse(producto.value.caracteristicas)
            : producto.value.caracteristicas;
            
        if (Array.isArray(chars)) {
            const item = chars.find(c => {
                const k = c.key || c.clave || c.nombre || '';
                return k.toLowerCase() === claveBuscada.toLowerCase();
            });
            return item ? (item.value || item.valor || null) : null;
        } else if (typeof chars === 'object') {
            return chars[claveBuscada] || chars[claveBuscada.toLowerCase()] || chars[claveBuscada.toUpperCase()] || null;
        }
    } catch {
        return null;
    }
    return null;
};
</script>

<template>
    <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
            
            <!-- Botón de retroceso -->
            <button 
                @click="router.back()" 
                class="flex items-center text-gray-600 hover:text-teal-600 transition-colors mb-6 group"
            >
                <svg class="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Volver al catálogo
            </button>

            <div v-if="cargando" class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
            </div>

            <div v-else-if="producto" class="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
                
                <!-- COLUMNA IZQUIERDA (2/3) -->
                <div class="lg:col-span-2 space-y-6">
                    
                    <!-- Imagen Principal y Galería -->
                    <div class="space-y-4">
                        <div class="relative rounded-3xl overflow-hidden shadow-xl aspect-[16/9] bg-gray-200 group/carousel flex items-center justify-center">
                            <img v-if="imagenPrincipal"
                                :src="imagenPrincipal" 
                                :alt="producto.nombre"
                                class="w-full h-full object-contain bg-white transition-all duration-500"
                            >
                            <div v-else class="flex flex-col items-center justify-center text-gray-400">
                                <svg class="w-16 h-16 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <span>Sin Imagen</span>
                            </div>
                            
                            <!-- Controles del Carrusel -->
                            <template v-if="imagenesObj.length > 1">
                                <button 
                                    @click="anteriorImagen"
                                    class="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/80 hover:bg-white text-teal-600 shadow-lg opacity-0 group-hover/carousel:opacity-100 transition-all z-10"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                                    </svg>
                                </button>
                                <button 
                                    @click="siguienteImagen"
                                    class="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/80 hover:bg-white text-teal-600 shadow-lg opacity-0 group-hover/carousel:opacity-100 transition-all z-10"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                                    </svg>
                                </button>
                                
                                <!-- Indicadores de punto -->
                                <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5 px-3 py-1.5 rounded-full bg-black/20 backdrop-blur-sm">
                                    <div 
                                        v-for="(_, idx) in imagenesObj" :key="idx"
                                        class="w-1.5 h-1.5 rounded-full transition-all duration-300"
                                        :class="imagenSeleccionadaIdx === idx ? 'bg-white w-4' : 'bg-white/40'"
                                    ></div>
                                </div>
                            </template>
                        </div>
                        
                        <!-- Galería de Miniaturas -->
                        <div v-if="imagenesObj.length > 1" class="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                            <button 
                                v-for="(img, idx) in imagenesObj" :key="idx"
                                @click="imagenSeleccionadaIdx = idx"
                                :class="['relative flex-shrink-0 w-24 h-24 rounded-2xl overflow-hidden border-2 transition-all bg-white', 
                                    (imagenSeleccionadaIdx === idx || (!imagenSeleccionadaIdx && idx === 0)) ? 'border-teal-500 scale-105 shadow-md' : 'border-transparent opacity-70 hover:opacity-100']"
                            >
                                <img :src="img" class="w-full h-full object-cover">
                            </button>
                        </div>
                    </div>

                    <!-- Título y Favorito -->
                    <div class="flex items-start justify-between">
                        <div class="space-y-1">
                            <h1 class="text-3xl sm:text-4xl font-black text-gray-900 leading-tight">
                                {{ producto.nombre }}
                            </h1>
                            <p class="text-teal-700 font-semibold flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                </svg>
                                Distribuido por {{ producto.nombre_proveedor }}
                            </p>
                            <!-- Descripción Corta (Desde características o genérica) -->
                            <p class="text-gray-600 text-sm leading-relaxed mt-2 italic">
                                {{ getCaracteristica('descripcion') || getCaracteristica('Descripción') || 'Producto de alta calidad disponible en Amazonia Viva.' }}
                            </p>
                        </div>
                        <button 
                            @click="handleAccion('favorito', $event)"
                            class="p-3 rounded-2xl bg-white shadow-md hover:shadow-lg text-red-500 hover:scale-110 transition-all border border-gray-100"
                            :class="{ 'opacity-50 grayscale cursor-not-allowed': rol === 'proveedor' }"
                        >
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                            </svg>
                        </button>
                    </div>

                    <!-- Rating y Categoría -->
                    <div class="flex items-center gap-4 flex-wrap pt-2">
                        <div class="flex items-center gap-1.5 bg-teal-50 px-3 py-1.5 rounded-full border border-teal-100">
                            <div class="flex gap-0.5">
                                <template v-for="(tipo, i) in estrellas(producto.rating)" :key="i">
                                    <svg v-if="tipo === 'full'" class="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                                    </svg>
                                    <svg v-else-if="tipo === 'half'" class="w-4 h-4 text-amber-300" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                                    </svg>
                                    <svg v-else class="w-4 h-4 text-gray-200" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                                    </svg>
                                </template>
                            </div>
                            <span class="text-sm font-bold text-teal-800">{{ Number(producto.rating || 0).toFixed(1) }} ({{ producto.num_calificaciones || 0 }})</span>
                        </div>
                        <span class="px-4 py-1.5 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold uppercase tracking-wider">
                            {{ producto.nombre_categoria || 'Categoría no definida' }}
                        </span>
                    </div>

                    <!-- Cards de Información Clave -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                            <div class="p-3 bg-teal-100 text-teal-600 rounded-xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-xs text-gray-400 font-medium uppercase tracking-tighter">Stock Disponible</p>
                                <p class="text-sm font-bold text-gray-800 truncate" :class="{'text-red-500': producto.stock < 5}">
                                    {{ producto.stock > 0 ? `${producto.stock} unidades` : 'Agotado' }}
                                </p>
                            </div>
                        </div>

                        <!-- Solo Proveedores ven el SKU -->
                        <div v-if="rol === 'proveedor'" class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                            <div class="p-3 bg-blue-100 text-blue-600 rounded-xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-xs text-gray-400 font-medium uppercase tracking-tighter">Código SKU</p>
                                <p class="text-sm font-bold text-gray-800 line-clamp-1">
                                    {{ producto.sku || 'N/A' }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Descripción Larga / Resumen -->
                    <div v-if="getCaracteristica('descripcion') || getCaracteristica('Descripción')" class="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <svg class="w-5 h-5 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                            </svg>
                            Detalles del Producto
                        </h2>
                        <p class="text-gray-600 leading-relaxed whitespace-pre-line">
                            {{ getCaracteristica('descripcion') || getCaracteristica('Descripción') }}
                        </p>
                    </div>

                    <!-- Características Técnicas -->
                    <div v-if="caracteristicasList.length > 0" class="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                            <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                            </svg>
                            Especificaciones Técnicas
                        </h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8">
                            <div v-for="(char, idx) in caracteristicasList.filter(c => (c.key || c.clave || c.nombre || '').toLowerCase() !== 'descripcion')" :key="idx" class="flex justify-between items-center py-2 border-b border-gray-100 last:border-0 relative group">
                                <span class="text-sm font-medium text-gray-500 capitalize">{{ char.key || char.clave || char.nombre }}</span>
                                <span class="text-sm font-bold text-gray-900 text-right max-w-xs break-words px-1">{{ char.value || char.valor }}</span>
                            </div>
                        </div>
                    </div>

                </div>

                <!-- COLUMNA DERECHA (1/3) -->
                <div class="lg:col-span-1">
                    <div class="sticky top-24 space-y-6">
                        
                        <!-- Card de Compra -->
                        <div class="bg-white p-8 rounded-3xl border border-gray-200 shadow-xl ring-1 ring-gray-900/5">
                            <div class="mb-6">
                                <p class="text-sm text-gray-400 font-medium mb-1">Precio</p>
                                <div class="flex items-baseline gap-2">
                                    <span class="text-4xl font-black text-gray-900">${{ Number(producto.precio).toLocaleString('es-CO') }}</span>
                                    <span class="text-gray-500 text-sm font-semibold">COP</span>
                                </div>
                            </div>

                            <div class="space-y-3 mb-8">
                                <button 
                                    @click="handleAccion('carrito', $event)"
                                    :disabled="producto.stock <= 0"
                                    class="w-full flex items-center justify-center gap-2 px-8 py-4 bg-teal-600 hover:bg-teal-700 text-white rounded-2xl font-bold text-lg shadow-lg shadow-teal-200 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:grayscale disabled:cursor-not-allowed disabled:hover:scale-100"
                                    :class="{ 'opacity-50 grayscale cursor-not-allowed': rol === 'proveedor' }"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                    {{ producto.stock > 0 ? 'Agregar al carrito' : 'Agotado temporalmente' }}
                                </button>
                                
                                <button 
                                    @click="handleAccion('favorito', $event)"
                                    class="w-full flex items-center justify-center gap-2 px-8 py-4 bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-200 rounded-2xl font-bold text-lg hover:border-red-400 hover:text-red-500 transition-all"
                                    :class="{ 'opacity-50 grayscale cursor-not-allowed': rol === 'proveedor' }"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                    Añadir a favoritos
                                </button>
                            </div>

                            <!-- Beneficios Adicionales -->
                            <div class="space-y-4 pt-6 border-t border-gray-100">
                                <div class="flex items-center gap-3 text-sm text-gray-600">
                                    <div class="bg-teal-100 p-1.5 rounded-full text-teal-600">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <span class="font-medium">Pagos seguros online</span>
                                </div>
                                <div v-if="getCaracteristica('garantia') || getCaracteristica('Garantía')" class="flex items-center gap-3 text-sm text-gray-600">
                                    <div class="bg-teal-100 p-1.5 rounded-full text-teal-600">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <span class="font-medium">Garantía: {{ getCaracteristica('garantia') || getCaracteristica('Garantía') }}</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

            </div>

            <!-- Estado Error -->
            <div v-else class="text-center py-20">
                <h2 class="text-2xl font-bold text-gray-500">Producto no encontrado</h2>
                <button @click="router.push('/catalogo/productos')" class="mt-4 text-teal-600 font-medium hover:underline">
                    Ver otros productos en el catálogo
                </button>
            </div>

        </div>

        <!-- Tooltip para Proveedores/Agencias -->
        <div 
            v-if="mostrarTooltip"
            class="fixed z-[100] px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-lg shadow-xl animate-bounce-subtle -translate-x-1/2"
            :style="{ top: `${tooltipPos.y}px`, left: `${tooltipPos.x}px` }"
        >
            Los proveedores no pueden comprar productos
            <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
        </div>
    </div>
</template>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-bounce-subtle {
    animation: bounceSubtle 0.5s ease-out alternate infinite;
}
</style>
