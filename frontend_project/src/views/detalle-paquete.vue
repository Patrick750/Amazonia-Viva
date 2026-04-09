<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCatalogo } from '@/composables/useCatalogo';
import { useNotificacion } from '@/composables/useNotificacion';
import clienteAxios from '@/api/axios';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const route = useRoute();
const router = useRouter();
const { obtenerTourPorId, toggleFavorito, agregarAlCarrito } = useCatalogo();
const { mostrarNotificacion } = useNotificacion();

const tour = ref(null);
const cargando = ref(true);
const id = route.params.id;
const imagenSeleccionadaIdx = ref(0);
const rol = ref(localStorage.getItem('rol'));
const mostrarTooltip = ref(false);
const tooltipPos = ref({ x: 0, y: 0 });
let tooltipTimeout = null;

// --- FECHAS Y CUPOS ---
const fechaElegida = ref('');
const cuposDisponibles = ref(null);
const cargandoCupos = ref(false);

const hoy = new Date().toISOString().split('T')[0];

const consultarCupos = async (fecha) => {
    if (!tour.value) return;
    cargandoCupos.value = true;
    try {
        const params = fecha ? `?fecha=${fecha}` : '';
        const { data } = await clienteAxios.get(`api/cupos/${tour.value.id}/${params}`);
        cuposDisponibles.value = data.cupos_disponibles;
    } catch (e) {
        cuposDisponibles.value = null;
    } finally {
        cargandoCupos.value = false;
    }
};

watch(fechaElegida, (nuevaFecha) => {
    if (nuevaFecha) consultarCupos(nuevaFecha);
    else cuposDisponibles.value = null;
});

const sinCupos = computed(() => cuposDisponibles.value !== null && cuposDisponibles.value === 0);
const pocoCupos = computed(() => cuposDisponibles.value !== null && cuposDisponibles.value > 0 && cuposDisponibles.value <= 5);

const formatFechaLarga = (fecha) => {
    if (!fecha) return '';
    const [y, m, d] = fecha.split('-');
    const meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
    return `${parseInt(d)} de ${meses[parseInt(m)-1]} de ${y}`;
};

// Variables del mapa
const mostrarMapaModal = ref(false);
const mapContainer = ref(null);
let map = null;
let marker = null;

onMounted(async () => {
    tour.value = await obtenerTourPorId(id);
    cargando.value = false;
    // Para paquetes fijos, consultar cupos de inmediato
    if (tour.value?.tipo_paquete === 'fijo' && tour.value?.fecha_realizacion) {
        consultarCupos(tour.value.fecha_realizacion);
    }
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

const abrirMapa = () => {
    if (tour.value?.latitud && tour.value?.longitud) {
        mostrarMapaModal.value = true;
    } else {
        mostrarNotificacion('La ubicación exacta no está disponible para este paquete.', 'warning');
    }
};

const initMap = () => {
    if (!mapContainer.value) return;
    
    if (map) {
        map.off();
        map.remove();
        map = null;
    }

    const position = [Number(tour.value.latitud), Number(tour.value.longitud)];
    
    map = L.map(mapContainer.value).setView(position, 15);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    
    marker = L.marker(position).addTo(map);
    
    setTimeout(() => {
        if(map) map.invalidateSize();
    }, 200);
};

watch(mostrarMapaModal, async (abierto) => {
    if (abierto) {
        await nextTick();
        setTimeout(() => initMap(), 100);
    }
});

const handleAccion = async (tipo, event) => {
    if (rol.value === 'proveedor' || rol.value === 'agencia') {
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
        // Validar fecha si el paquete es flexible
        if (tour.value.tipo_paquete === 'flexible' && !fechaElegida.value) {
            mostrarNotificacion('Debes elegir una fecha para este tour flexible.', 'warning');
            return;
        }
        // Validar cupos
        if (cuposDisponibles.value !== null && cuposDisponibles.value <= 0) {
            mostrarNotificacion('No hay cupos disponibles para la fecha seleccionada.', 'error');
            return;
        }
        const fechaParaCarrito = tour.value.tipo_paquete === 'fijo' 
            ? tour.value.fecha_realizacion 
            : fechaElegida.value;
        await agregarAlCarrito(
            tour.value.id,
            tour.value.precio,
            'paquete',
            {
                nombre: tour.value.nombre,
                imagen: imagenPrincipal.value || null,
                subtitulo: `${tour.value.duracion}h · ${tour.value.ubicacion}`,
                fecha_reserva: fechaParaCarrito || null,
            }
        );
    } else if (tipo === 'favorito') {
        await toggleFavorito(tour.value.id);
    }
};

const imagenes = computed(() => {
    if (!tour.value?.imagen_paquete) return [];
    return tour.value.imagen_paquete.map(img => img.url);
});

const imagenPrincipal = computed(() => {
    if (imagenes.value.length > 0) {
        return imagenes.value[imagenSeleccionadaIdx.value];
    }
    return null;
});

const siguienteImagen = () => {
    if (imagenes.value.length > 1) {
        imagenSeleccionadaIdx.value = (imagenSeleccionadaIdx.value + 1) % imagenes.value.length;
    }
};

const anteriorImagen = () => {
    if (imagenes.value.length > 1) {
        imagenSeleccionadaIdx.value = (imagenSeleccionadaIdx.value - 1 + imagenes.value.length) % imagenes.value.length;
    }
};

const formatTime = (timeStr) => {
    if (!timeStr) return 'HH:MM';
    // Si ya contiene AM/PM, lo dejamos igual
    if (timeStr.toLowerCase().includes('am') || timeStr.toLowerCase().includes('pm')) return timeStr;
    
    const parts = timeStr.split(':');
    if (parts.length < 2) return timeStr;
    
    let hrs = parseInt(parts[0]);
    const mins = parts[1].substring(0, 2);
    
    if (isNaN(hrs)) return timeStr;
    
    const period = hrs >= 12 ? 'PM' : 'AM';
    hrs = hrs % 12 || 12;
    return `${hrs}:${mins} ${period}`;
};
</script>

<template>
    <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
            
            <!-- Botón de retroceso -->
            <button 
                @click="router.back()" 
                class="flex items-center text-gray-600 hover:text-emerald-600 transition-colors mb-6 group"
            >
                <svg class="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Volver al catálogo
            </button>

            <div v-if="cargando" class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
            </div>

            <div v-else-if="tour" class="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
                
                <!-- COLUMNA IZQUIERDA (2/3) -->
                <div class="lg:col-span-2 space-y-6">
                    
                    <!-- Imagen Principal y Galería -->
                    <div class="space-y-4">
                        <div class="relative rounded-3xl overflow-hidden shadow-xl aspect-[16/9] bg-gray-200 group/carousel">
                            <img 
                                :src="imagenPrincipal || 'https://via.placeholder.com/800x450?text=Sin+Imagen'" 
                                :alt="tour.nombre"
                                class="w-full h-full object-cover transition-all duration-500"
                            >
                            
                            <!-- Controles del Carrusel -->
                            <template v-if="imagenes.length > 1">
                                <button 
                                    @click="anteriorImagen"
                                    class="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/80 hover:bg-white text-emerald-600 shadow-lg opacity-0 group-hover/carousel:opacity-100 transition-all z-10"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                                    </svg>
                                </button>
                                <button 
                                    @click="siguienteImagen"
                                    class="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/80 hover:bg-white text-emerald-600 shadow-lg opacity-0 group-hover/carousel:opacity-100 transition-all z-10"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                                    </svg>
                                </button>
                                
                                <!-- Indicadores de punto -->
                                <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5 px-3 py-1.5 rounded-full bg-black/20 backdrop-blur-sm">
                                    <div 
                                        v-for="(_, idx) in imagenes" :key="idx"
                                        class="w-1.5 h-1.5 rounded-full transition-all duration-300"
                                        :class="imagenSeleccionadaIdx === idx ? 'bg-white w-4' : 'bg-white/40'"
                                    ></div>
                                </div>
                            </template>
                        </div>
                        
                        <!-- Galería de Miniaturas -->
                        <div v-if="imagenes.length > 1" class="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                            <button 
                                v-for="(img, idx) in imagenes" :key="idx"
                                @click="imagenSeleccionadaIdx = idx"
                                :class="['relative flex-shrink-0 w-24 h-24 rounded-2xl overflow-hidden border-2 transition-all', 
                                    (imagenSeleccionadaIdx === idx || (!imagenSeleccionadaIdx && idx === 0)) ? 'border-emerald-500 scale-105 shadow-md' : 'border-transparent opacity-70 hover:opacity-100']"
                            >
                                <img :src="img" class="w-full h-full object-cover">
                            </button>
                        </div>
                    </div>

                    <!-- Título y Favorito -->
                    <div class="flex items-start justify-between">
                        <div class="space-y-1">
                            <h1 class="text-3xl sm:text-4xl font-black text-gray-900 leading-tight">
                                {{ tour.nombre }}
                            </h1>
                            <router-link :to="{ name: 'perfil_publico', params: { id: tour.agencia_id }, query: { tipo: 'agencia' } }" class="text-emerald-700 hover:text-emerald-800 transition-colors font-semibold flex items-center gap-2 w-max cursor-pointer decoration-2 underline-offset-4 hover:underline">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m4 0h1m-5 10h5m-5 4h5" />
                                </svg>
                                Organizado por {{ tour.nombre_agencia }}
                            </router-link>
                            <!-- Descripción Corta/Quick View -->
                            <p class="text-gray-600 text-sm leading-relaxed mt-2 italic">
                                {{ tour.descripcion }}
                            </p>
                        </div>
                        <button 
                            @click="handleAccion('favorito', $event)"
                            class="p-3 rounded-2xl bg-white shadow-md hover:shadow-lg text-red-500 hover:scale-110 transition-all border border-gray-100"
                            :class="{ 'opacity-50 grayscale cursor-not-allowed': rol === 'proveedor' || rol === 'agencia' }"
                        >
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                            </svg>
                        </button>
                    </div>

                    <!-- Rating y Categoría -->
                    <div class="flex items-center gap-4 flex-wrap pt-2">
                        <div class="flex items-center gap-1.5 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">
                            <div class="flex gap-0.5">
                                <template v-for="(tipo, i) in estrellas(tour.rating)" :key="i">
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
                            <span class="text-sm font-bold text-emerald-800">{{ Number(tour.rating || 0).toFixed(1) }}</span>
                        </div>
                        <span class="px-4 py-1.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-wider">
                            {{ tour.categoria_paquete_nombre || 'General' }}
                        </span>
                    </div>

                    <!-- Cards de Información Clave -->
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                            <div class="p-3 bg-emerald-100 text-emerald-600 rounded-xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-xs text-gray-400 font-medium uppercase tracking-tighter">Ubicación</p>
                                <div class="flex items-center gap-2">
                                    <p class="text-sm font-bold text-gray-800 truncate">{{ tour.ubicacion }}</p>
                                    <button 
                                        @click="abrirMapa"
                                        class="text-emerald-600 hover:text-emerald-700 font-bold text-[10px] uppercase underline decoration-2 underline-offset-4 whitespace-nowrap"
                                    >
                                        Abrir mapa
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                            <div class="p-3 bg-blue-100 text-blue-600 rounded-xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-xs text-gray-400 font-medium uppercase tracking-tighter">Duración</p>
                                <p class="text-sm font-bold text-gray-800">{{ tour.duracion }}h</p>
                            </div>
                        </div>

                        <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                            <div class="p-3 bg-purple-100 text-purple-600 rounded-xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-xs text-gray-400 font-medium uppercase tracking-tighter">Capacidad</p>
                                <p class="text-sm font-bold text-gray-800">{{ tour.capacidad }} personas</p>
                            </div>
                        </div>

                        <div class="bg-emerald-600 p-4 rounded-2xl shadow-lg shadow-emerald-100 flex items-center gap-4 text-white">
                            <div class="p-3 bg-white/20 rounded-xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-[10px] opacity-80 font-bold uppercase tracking-widest leading-none mb-1">Total Vendidos</p>
                                <p class="text-lg font-black">{{ tour.ventas_totales || 0 }}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Descripción -->
                    <div class="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                            </svg>
                            Acerca de este tour
                        </h2>
                        <p class="text-gray-600 leading-relaxed whitespace-pre-line">
                            {{ tour.descripcion }}
                        </p>
                    </div>

                    <!-- Qué incluye y Actividades -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                            <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                                Lo que incluye
                            </h2>
                            <ul class="space-y-3">
                                <li v-for="(item, idx) in tour.incluido" :key="idx" class="flex items-start gap-3 text-gray-600">
                                    <svg class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                    </svg>
                                    {{ item.valor || item.item || item }}
                                </li>
                                <li v-if="!tour.incluido || tour.incluido.length === 0" class="text-gray-400 italic">No especificado</li>
                            </ul>
                        </div>

                        <div class="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                            <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Actividades
                            </h2>
                            <div class="flex flex-wrap gap-2">
                                <span v-for="act in tour.actividades_detalle" :key="act.id" 
                                    class="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-xl text-sm font-medium border border-blue-100 flex items-center gap-2"
                                >
                                    {{ act.nombre }}
                                    <span class="text-[10px] bg-blue-200 px-1.5 rounded-full">Nivel {{ act.nivel_riesgo }}</span>
                                </span>
                                <span v-if="!tour.actividades_detalle || tour.actividades_detalle.length === 0" class="text-gray-400 italic">No hay actividades listadas</span>
                            </div>
                        </div>
                    </div>

                    <!-- Itinerario -->
                    <div v-if="tour.itinerario && tour.itinerario.length > 0" class="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                            <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Itinerario
                        </h2>
                        <div class="relative pl-8 space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-100">
                            <div v-for="(step, idx) in tour.itinerario" :key="idx" class="relative">
                                <div class="absolute -left-[30px] top-1 w-4 h-4 rounded-full bg-white border-4 border-purple-500 shadow-sm z-10"></div>
                                <div class="space-y-1">
                                    <span class="text-xs font-black text-purple-600 uppercase tracking-widest">{{ formatTime(step.time) }}</span>
                                    <h3 class="font-bold text-gray-800">{{ step.activity || step.actividad }}</h3>
                                    <p v-if="step.description || step.descripcion" class="text-sm text-gray-500 leading-relaxed">{{ step.description || step.descripcion }}</p>
                                </div>
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
                                <p class="text-sm text-gray-400 font-medium">Precio por persona</p>
                                <div class="flex items-baseline gap-2">
                                    <span class="text-4xl font-black text-gray-900">${{ Number(tour.precio).toLocaleString('es-CO') }}</span>
                                    <span class="text-gray-500 text-sm font-semibold">COP</span>
                                </div>
                            </div>

                            <!-- Badge tipo de paquete -->
                            <div class="mb-5">
                                <!-- PAQUETE FIJO -->
                                <div v-if="tour.tipo_paquete === 'fijo'" class="p-4 rounded-2xl bg-blue-50 border-2 border-blue-100 space-y-3">
                                    <div class="flex items-center gap-2">
                                        <div class="p-2 bg-blue-100 rounded-xl text-blue-600">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                                        </div>
                                        <div>
                                            <p class="text-[10px] text-blue-400 font-bold uppercase tracking-widest">Fecha del tour (Fijo)</p>
                                            <p class="text-sm font-bold text-blue-800">{{ formatFechaLarga(tour.fecha_realizacion) }}</p>
                                        </div>
                                    </div>
                                    <!-- Cupos fijo -->
                                    <div v-if="cuposDisponibles !== null" class="flex items-center gap-2">
                                        <div :class="['flex-1 flex items-center gap-2 px-3 py-2 rounded-xl font-semibold text-xs',
                                            sinCupos ? 'bg-red-100 text-red-700' : pocoCupos ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700']">
                                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                            <span v-if="sinCupos">¡No hay cupos disponibles!</span>
                                            <span v-else-if="pocoCupos">¡Últimos {{ cuposDisponibles }} cupos!</span>
                                            <span v-else>{{ cuposDisponibles }} cupos disponibles</span>
                                        </div>
                                    </div>
                                    <div v-else-if="cargandoCupos" class="text-xs text-blue-400 flex items-center gap-1.5">
                                        <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                                        Verificando cupos...
                                    </div>
                                </div>

                                <!-- PAQUETE FLEXIBLE -->
                                <div v-else-if="tour.tipo_paquete === 'flexible'" class="p-4 rounded-2xl bg-emerald-50 border-2 border-emerald-100 space-y-3">
                                    <div class="flex items-center gap-2 mb-1">
                                        <div class="p-2 bg-emerald-100 rounded-xl text-emerald-600">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                                        </div>
                                        <div>
                                            <p class="text-[10px] text-emerald-500 font-bold uppercase tracking-widest">Elige tu fecha</p>
                                            <p class="text-xs text-emerald-700 font-medium">Tú decides cuándo realizarlo</p>
                                        </div>
                                    </div>
                                    <input
                                        v-model="fechaElegida"
                                        type="date"
                                        :min="hoy"
                                        class="w-full bg-white border-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-800 focus:outline-none transition-all"
                                        :class="fechaElegida ? 'border-emerald-400 focus:border-emerald-500' : 'border-emerald-200 focus:border-emerald-400'"
                                    >
                                    <!-- Cupos flexíble -->
                                    <div v-if="cargandoCupos" class="text-xs text-emerald-500 flex items-center gap-1.5">
                                        <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                                        Verificando disponibilidad...
                                    </div>
                                    <div v-else-if="fechaElegida && cuposDisponibles !== null" 
                                        :class="['flex items-center gap-2 px-3 py-2 rounded-xl font-semibold text-xs',
                                            sinCupos ? 'bg-red-100 text-red-700' : pocoCupos ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700']">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                        <span v-if="sinCupos">¡No hay cupos para esta fecha!</span>
                                        <span v-else-if="pocoCupos">¡Últimos {{ cuposDisponibles }} cupos!</span>
                                        <span v-else>{{ cuposDisponibles }} cupos disponibles</span>
                                    </div>
                                    <p v-else-if="!fechaElegida" class="text-xs text-emerald-500 font-medium">↩ Selecciona una fecha para ver disponibilidad</p>
                                </div>
                            </div>

                            <div class="space-y-3 mb-8">
                                <button 
                                    @click="handleAccion('carrito', $event)"
                                    class="w-full flex items-center justify-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-bold text-lg shadow-lg shadow-emerald-200 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100"
                                    :class="{ 'opacity-50 grayscale cursor-not-allowed': rol === 'proveedor' || rol === 'agencia' }"
                                    :disabled="sinCupos || (tour.tipo_paquete === 'flexible' && !fechaElegida)"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                    <span v-if="sinCupos">Sin cupos disponibles</span>
                                    <span v-else-if="tour.tipo_paquete === 'flexible' && !fechaElegida">Elige una fecha primero</span>
                                    <span v-else>Agregar al carrito</span>
                                </button>
                                
                                <button 
                                    @click="handleAccion('favorito', $event)"
                                    class="w-full flex items-center justify-center gap-2 px-8 py-4 bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-200 rounded-2xl font-bold text-lg hover:border-red-400 hover:text-red-500 transition-all"
                                    :class="{ 'opacity-50 grayscale cursor-not-allowed': rol === 'proveedor' || rol === 'agencia' }"
                                >
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                    Añadir a favoritos
                                </button>
                            </div>

                            <!-- Beneficios -->
                            <div class="space-y-4 pt-6 border-t border-gray-100">
                                <div class="flex items-center gap-3 text-sm text-gray-600">
                                    <div class="bg-emerald-100 p-1 rounded-full text-emerald-600">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <span class="font-medium">Cancelación gratuita (24h)</span>
                                </div>
                                <div class="flex items-center gap-3 text-sm text-gray-600">
                                    <div class="bg-emerald-100 p-1 rounded-full text-emerald-600">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <span class="font-medium">Confirmación instantánea</span>
                                </div>
                                <div class="flex items-center gap-3 text-sm text-gray-600">
                                    <div class="bg-emerald-100 p-1 rounded-full text-emerald-600">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <span class="font-medium">Guía profesional bilingüe</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

            </div>

            <!-- Estado Error -->
            <div v-else class="text-center py-20">
                <h2 class="text-2xl font-bold text-gray-500">Paquete no encontrado</h2>
                <button @click="router.push('/catalogo/tours')" class="mt-4 text-emerald-600 hover:underline">
                    Ver otros paquetes
                </button>
            </div>

        </div>

        <!-- Tooltip para Proveedores -->
        <div 
            v-if="mostrarTooltip"
            class="fixed z-[100] px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-lg shadow-xl animate-bounce-subtle -translate-x-1/2"
            :style="{ top: `${tooltipPos.y}px`, left: `${tooltipPos.x}px` }"
        >
            Nesesitas inciar sesion como turista
            <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
        </div>
        <!-- Modal de Mapa -->
        <Teleport to="body">
            <div v-if="mostrarMapaModal"
                class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
                @click.self="mostrarMapaModal = false"
            >
                <!-- Backdrop oscuro -->
                <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"></div>
                
                <!-- Contenedor del Modal -->
                <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-4xl overflow-hidden animate-fade-in-up flex flex-col">
                    
                    <!-- Header del Modal -->
                    <div class="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-4 flex items-center justify-between z-10">
                        <div class="flex items-center gap-3">
                            <div class="p-2 bg-white/20 rounded-xl text-white">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </div>
                            <div>
                                <h3 class="text-white font-bold text-lg leading-tight">Ubicación del Tour</h3>
                                <p class="text-emerald-100 text-xs font-medium truncate max-w-md">{{ tour.ubicacion }}</p>
                            </div>
                        </div>
                        <button 
                            @click="mostrarMapaModal = false"
                            class="w-8 h-8 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/30 hover:rotate-90 transition-all duration-300"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Contenedor del Mapa -->
                    <div class="w-full h-[60vh] sm:h-[70vh] bg-slate-100 relative z-0">
                        <div ref="mapContainer" class="absolute inset-0 w-full h-full z-0" style="touch-action: none;"></div>
                        
                        <!-- Coordenadas overlay -->
                        <div class="absolute bottom-4 left-4 right-4 sm:right-auto bg-white/90 backdrop-blur-md px-4 py-3 rounded-2xl shadow-lg border border-slate-100/50 flex flex-col gap-1 z-10">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Coordenadas exactas</span>
                            <div class="flex items-center gap-2 text-emerald-700 font-mono text-xs sm:text-sm bg-emerald-50/50 px-3 py-1.5 rounded-xl border border-emerald-100">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>{{ Number(tour.latitud).toFixed(5) }}, {{ Number(tour.longitud).toFixed(5) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>
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

.animate-fade-in-up {
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

.animate-bounce-subtle {
    animation: bounceSubtle 0.5s ease-out alternate infinite;
}

@keyframes bounceSubtle {
    from { transform: translate(-50%, 0); }
    to { transform: translate(-50%, -4px); }
}
</style>
