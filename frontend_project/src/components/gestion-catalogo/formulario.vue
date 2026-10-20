<script setup>
import { reactive, watch, ref, computed, nextTick, onBeforeUnmount } from 'vue';
import { GuardarRegistro } from '@/composables/gestion-tours/create-pack';
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

const props = defineProps(['abrir', 'actividades', 'paquete', 'errorDatos']);
const emit = defineEmits(['cerrar', 'guardadoExitoso']);

// --- COMPOSABLE ---
const { guardarDatos } = GuardarRegistro();

// --- ESTADOS ---
const isLoading = ref(false);
const errores = reactive({});
const isDragging = ref(false);
const fileInput = ref(null);
const mapContainer = ref(null);
let map = null;
let marker = null;
let bodyOverflowAnterior = '';
let bloqueoScrollActivo = false;

// --- NOTIFICACIÓN ---
const { mostrarNotificacion } = useNotificacion();

// --- ESTADO DEL MAPA/BÚSQUEDA ---
const searchQuery = ref('');
const suggestions = ref([]);
const isSearching = ref(false);
const isMapExpanded = ref(false);
let searchTimeout = null;
const estandar = ref(null);

// --- ESTADO DEL FORMULARIO ---
const newTour = reactive({
    id: null,
    activo: true,
    nombre: '',
    descripcion: '',
    precio: '',
    duracion: '',
    ubicacion: '',
    latitud: null,
    longitud: null,
    capacidad: '',
    actividades: [],
    itinerario: [{ time: '', activity: '' }],
    incluido: [{ item: '' }],
    imagen: [],   // nuevas imágenes locales { file, url, name }
    categoria_paquete: '',
    fecha_realizacion: '',
    modalidades_turismo: [],
    clasificacion_actividades: [],
    requisitos_participantes: '',
    condiciones_operacion: '',
    medidas_seguridad: '',
    informacion_sostenibilidad: '',
    certificacion_aventura: {
        estado: 'no_aplica',
        organismo: '',
        codigo: '',
        vigente_hasta: '',
    },
});

// Tipo calculado en tiempo real
const tipoPaqueteAuto = computed(() => newTour.fecha_realizacion ? 'fijo' : 'flexible');
const actividadesDisponibles = computed(() =>
    Array.isArray(props.actividades) ? props.actividades : []
);
const actividadesSeleccionadas = computed(() =>
    actividadesDisponibles.value.filter(actividad => newTour.actividades.includes(actividad.id))
);
const actividadesAventura = computed(() =>
    actividadesSeleccionadas.value.filter(actividad => actividad.es_turismo_aventura)
);
const requiereCertificacion = computed(() => actividadesAventura.value.length > 0);
const totalErrores = computed(() => Object.keys(errores).length);
const camposOperacionCompletos = computed(() => [
    newTour.requisitos_participantes,
    newTour.condiciones_operacion,
    newTour.medidas_seguridad,
    newTour.informacion_sostenibilidad,
].filter(valor => String(valor || '').trim()).length);
const erroresCarga = reactive({ categorias: '', estandar: '' });
const mensajesCarga = computed(() =>
    [props.errorDatos, erroresCarga.categorias, erroresCarga.estandar].filter(Boolean)
);

const categorias = ref([]);
const fetchCategorias = async () => {
    erroresCarga.categorias = '';
    try {
        const { data } = await clienteAxios.get('api/categorias-paquetes/');
        if (!Array.isArray(data)) throw new Error('Respuesta inválida');
        categorias.value = data;
    } catch (error) {
        categorias.value = [];
        erroresCarga.categorias = 'No fue posible cargar las categorías de paquetes.';
        console.error("Error al cargar categorías", error);
    }
};

const fetchEstandar = async () => {
    if (estandar.value) return;
    erroresCarga.estandar = '';
    try {
        const { data } = await clienteAxios.get('api/estandar-paquetes/');
        if (!data || !Array.isArray(data.modalidades)) throw new Error('Respuesta inválida');
        estandar.value = data;
    } catch (error) {
        estandar.value = null;
        erroresCarga.estandar = 'No fue posible cargar la configuración del estándar turístico.';
        console.error('Error al cargar el estándar de paquetes', error);
    }
};

// Imágenes ya guardadas en BD (solo edición)
const imagenesExistentes = ref([]);   // { id, url, es_portada }
// IDs de imágenes a eliminar al guardar
const imagenesAEliminar = ref([]);

// Conteo total para el badge
const totalImageCount = computed(() =>
    imagenesExistentes.value.length + newTour.imagen.length
);

const inicial = JSON.parse(JSON.stringify(newTour));

// --- WATCH DE PROP PAQUETE ---
watch(() => props.paquete, (paqueteAEditar) => {
    if (paqueteAEditar) {
        Object.assign(newTour, JSON.parse(JSON.stringify(paqueteAEditar)));
        if (paqueteAEditar.ubicacion) searchQuery.value = paqueteAEditar.ubicacion;

        // Garantizar que itinerario sea un Arreglo
        if (typeof newTour.itinerario === 'string') {
            try { newTour.itinerario = JSON.parse(newTour.itinerario); } catch { newTour.itinerario = []; }
        }
        if (!Array.isArray(newTour.itinerario) || newTour.itinerario.length === 0) {
            newTour.itinerario = [{ time: '', activity: '' }];
        }

        // Garantizar que incluido sea un Arreglo
        if (typeof newTour.incluido === 'string') {
            try { newTour.incluido = JSON.parse(newTour.incluido); } catch { newTour.incluido = []; }
        }
        if (!Array.isArray(newTour.incluido) || newTour.incluido.length === 0) {
            newTour.incluido = [{ item: '' }];
        }

        newTour.imagen = [];
        newTour.fecha_realizacion = paqueteAEditar.fecha_realizacion || '';
        newTour.modalidades_turismo = Array.isArray(paqueteAEditar.modalidades_turismo)
            ? [...paqueteAEditar.modalidades_turismo]
            : [];
        newTour.clasificacion_actividades = Array.isArray(paqueteAEditar.clasificacion_actividades)
            ? JSON.parse(JSON.stringify(paqueteAEditar.clasificacion_actividades))
            : [];
        newTour.certificacion_aventura = {
            estado: 'no_aplica', organismo: '', codigo: '', vigente_hasta: '',
            ...(paqueteAEditar.certificacion_aventura || {}),
        };
        // Cargar imágenes existentes
        imagenesExistentes.value = paqueteAEditar.imagen_paquete
            ? paqueteAEditar.imagen_paquete.map(i => ({ ...i }))
            : [];
    } else {
        Object.assign(newTour, JSON.parse(JSON.stringify(inicial)));
        newTour.itinerario = [{ time: '', activity: '' }];
        newTour.incluido = [{ item: '' }];
        newTour.imagen = [];
        newTour.fecha_realizacion = '';
        newTour.modalidades_turismo = [];
        newTour.clasificacion_actividades = [];
        newTour.certificacion_aventura = { estado: 'no_aplica', organismo: '', codigo: '', vigente_hasta: '' };
        imagenesExistentes.value = [];
    }
    imagenesAEliminar.value = [];
    Object.keys(errores).forEach(key => delete errores[key]);
}, { immediate: true });

// --- LIMPIEZA ---
const limpiarFormulario = () => {
    newTour.imagen.forEach(img => {
        if (img.url?.startsWith('blob:')) URL.revokeObjectURL(img.url);
    });
    Object.assign(newTour, JSON.parse(JSON.stringify(inicial)));
    newTour.itinerario = [{ time: '', activity: '' }];
    newTour.incluido = [{ item: '' }];
    newTour.imagen = [];
    newTour.actividades = [];
    newTour.fecha_realizacion = '';
    imagenesExistentes.value = [];
    imagenesAEliminar.value = [];
    searchQuery.value = '';
    suggestions.value = [];
    if (fileInput.value) fileInput.value.value = '';
    if (marker) marker.setOpacity(0);
    Object.keys(errores).forEach(key => delete errores[key]);
};

// --- VALIDACIÓN ---
const validarFormulario = () => {
    Object.keys(errores).forEach(key => delete errores[key]);
    let valido = true;
    if (!newTour.nombre?.trim()) { errores.nombre = "El nombre es obligatorio."; valido = false; }
    if (!newTour.descripcion?.trim()) { errores.descripcion = "La descripción es obligatoria."; valido = false; }
    if (!newTour.precio || newTour.precio <= 0) { errores.precio = "Precio inválido."; valido = false; }
    if (!newTour.duracion?.trim()) { errores.duracion = "La duración es obligatoria."; valido = false; }
    if (!newTour.capacidad || newTour.capacidad <= 0) { errores.capacidad = "Capacidad inválida."; valido = false; }
    if (!newTour.categoria_paquete) { errores.categoria_paquete = "Selecciona una categoría."; valido = false; }
    if (newTour.actividades.length === 0) { errores.actividades = "Selecciona al menos una actividad."; valido = false; }
    if (newTour.modalidades_turismo.length === 0) { errores.modalidades_turismo = "Selecciona al menos una modalidad."; valido = false; }

    if (requiereCertificacion.value) {
        if (!newTour.modalidades_turismo.includes('aventura')) {
            errores.modalidades_turismo = 'Incluye Turismo de aventura para las actividades seleccionadas.';
            valido = false;
        }
        const fichasIncompletas = actividadesAventura.value.filter(actividad => {
            const ficha = newTour.clasificacion_actividades.find(item => Number(item.actividad_id) === actividad.id);
            return !ficha || (!ficha.nivel && !ficha.descripcion?.trim());
        });
        if (fichasIncompletas.length) {
            errores.clasificacion_actividades = `Completa la ficha técnica de ${fichasIncompletas.map(item => item.nombre).join(', ')}.`;
            valido = false;
        }
        if (!newTour.requisitos_participantes.trim()) { errores.requisitos_participantes = 'Indica requisitos y restricciones.'; valido = false; }
        if (!newTour.condiciones_operacion.trim()) { errores.condiciones_operacion = 'Describe las condiciones de operación.'; valido = false; }
        if (!newTour.medidas_seguridad.trim()) { errores.medidas_seguridad = 'Describe las medidas de seguridad.'; valido = false; }
        if (newTour.activo && newTour.certificacion_aventura.estado !== 'vigente') {
            errores.certificacion_aventura = 'Un tour de aventura activo requiere certificación vigente.';
            valido = false;
        } else if (newTour.activo && ['organismo', 'codigo', 'vigente_hasta'].some(campo => !newTour.certificacion_aventura[campo]?.trim())) {
            errores.certificacion_aventura = 'Completa organismo, código y fecha de vigencia.';
            valido = false;
        }
    }
    
    // Validación de mapa y ubicación
    if (!searchQuery.value?.trim()) {
        errores.ubicacion = "Debes escribir o buscar una ubicación principal.";
        valido = false;
    }
    if (!newTour.latitud || !newTour.longitud) {
        errores.ubicacion = "Debes seleccionar un punto en el mapa (puedes buscarlo o hacer clic).";
        valido = false;
    }
    if (!valido) {
        nextTick(() => document.querySelector('[data-form-error="true"]')?.scrollIntoView({ behavior: 'smooth', block: 'center' }));
    }
    return valido;
};

const fichaActividad = (actividad) => {
    let ficha = newTour.clasificacion_actividades.find(item => Number(item.actividad_id) === actividad.id);
    if (!ficha) {
        ficha = {
            actividad_id: actividad.id,
            sistema: actividad.sistema_dificultad || '',
            nivel: '',
            descripcion: '',
        };
        newTour.clasificacion_actividades.push(ficha);
    }
    return ficha;
};

watch(() => [...newTour.actividades], (ids) => {
    const seleccionadas = new Set(ids.map(Number));
    newTour.clasificacion_actividades = newTour.clasificacion_actividades
        .filter(item => seleccionadas.has(Number(item.actividad_id)));
    actividadesSeleccionadas.value.forEach(actividad => fichaActividad(actividad));
    if (actividadesAventura.value.length && !newTour.modalidades_turismo.includes('aventura')) {
        newTour.modalidades_turismo.push('aventura');
    }
    if (!actividadesAventura.value.length) {
        newTour.certificacion_aventura.estado = 'no_aplica';
    }
}, { deep: true });

// --- ITINERARIO E INCLUIDO ---
const addItineraryItem = () => {
    if (!Array.isArray(newTour.itinerario)) newTour.itinerario = [];
    newTour.itinerario.push({ time: '', activity: '' });
};
const removeItineraryItem = (index) => {
    if (Array.isArray(newTour.itinerario) && newTour.itinerario.length > 1) {
        newTour.itinerario.splice(index, 1);
    }
};
const addIncludedItem = () => {
    if (!Array.isArray(newTour.incluido)) newTour.incluido = [];
    newTour.incluido.push({ item: '' });
};
const removeIncludedItem = (index) => {
    if (Array.isArray(newTour.incluido) && newTour.incluido.length > 1) {
        newTour.incluido.splice(index, 1);
    }
};

// --- IMÁGENES LOCALES (nuevas) ---
const handleDrop = (e) => {
    isDragging.value = false;
    if (e.dataTransfer.files) procesarArchivos(e.dataTransfer.files);
};
const procesarArchivos = (archivos) => {
    Array.from(archivos).filter(f => f.type.startsWith('image/')).forEach(file => {
        newTour.imagen.push({ file, url: URL.createObjectURL(file), name: file.name });
    });
};
const handleSelect = (event) => procesarArchivos(event.target.files);
const removeImage = (index) => {
    if (newTour.imagen[index].url?.startsWith('blob:')) URL.revokeObjectURL(newTour.imagen[index].url);
    newTour.imagen.splice(index, 1);
};

// --- IMÁGENES EXISTENTES ---
const removeExistingImage = (imgId, index) => {
    imagenesAEliminar.value.push(imgId);
    imagenesExistentes.value.splice(index, 1);
};

// --- LEAFLET MAPS ---
const initMap = () => {
    // Usar DOM nativo para evitar problemas de ref() con Teleport en Vue 3
    const mapEl = document.getElementById('map');
    if (!mapEl) {
        setTimeout(initMap, 100);
        return;
    }
    
    // Si ya existe el mapa lo destruimos para volver a crearlo
    if (map) {
        map.off();
        map.remove();
        map = null;
    }

    const hasCoords = newTour.latitud !== null && newTour.latitud !== undefined && newTour.latitud !== '' &&
                      newTour.longitud !== null && newTour.longitud !== undefined && newTour.longitud !== '';

    const defaultPos = hasCoords
        ? [Number(newTour.latitud), Number(newTour.longitud)]
        : [4.6097, -74.0817];

    // Asegurarse de que el contenedor esté limpio antes de inicializar
    mapEl.innerHTML = '';
    
    map = L.map(mapEl).setView(defaultPos, hasCoords ? 15 : 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    marker = L.marker(defaultPos, { draggable: true }).addTo(map);
    
    if (!hasCoords) {
        marker.setOpacity(0);
    }

    marker.on('dragend', function () {
        const posicion = marker.getLatLng();
        newTour.latitud = posicion.lat;
        newTour.longitud = posicion.lng;
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        marker.setOpacity(1);
        newTour.latitud = e.latlng.lat;
        newTour.longitud = e.latlng.lng;
    });
    
    // Resize map forcefully after modal layout and CSS animations finish
    setTimeout(() => {
        if(map) {
            map.invalidateSize();
            if (hasCoords) map.setView(defaultPos, 15);
        }
    }, 450);
};

// --- AUTOCOMPLETADO Y BÚSQUEDA ---
watch(searchQuery, (newVal) => {
    if (!newVal || newVal.trim().length < 3) {
        suggestions.value = [];
        return;
    }
    
    // Si la selección fue directa (el texto es igual a la ubicación guardada), ignoramos
    if (newVal === newTour.ubicacion) return;

    if (searchTimeout) clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(async () => {
        isSearching.value = true;
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(newVal)}&limit=5`);
            const data = await res.json();
            suggestions.value = data || [];
        } catch (e) {
            console.error("Nominatim input error:", e);
        } finally {
            isSearching.value = false;
        }
    }, 600);
});

const selectSuggestion = async (place) => {
    suggestions.value = [];
    searchQuery.value = place.display_name;
    
    if (!map) {
        await nextTick();
        initMap();
    }
    
    const lat = parseFloat(place.lat);
    const lon = parseFloat(place.lon);
    
    if (map) {
        map.setView([lat, lon], 15);
        if (marker) {
            marker.setLatLng([lat, lon]);
            marker.setOpacity(1);
        }
    }
    
    newTour.latitud = lat;
    newTour.longitud = lon;
    newTour.ubicacion = place.display_name;
    mostrarNotificacion('Ubicación seleccionada', 'exito');
};

const buscarUbicacionManual = async () => {
    if (!searchQuery.value) return;
    suggestions.value = []; 
    
    if (!map) {
        await nextTick();
        initMap();
    }
    
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&limit=1`);
        const data = await res.json();
        if (data && data.length > 0) {
            selectSuggestion(data[0]);
        } else {
            mostrarNotificacion('No se encontró la ubicación', 'error');
        }
    } catch (e) {
        console.error("Leaflet Search Error:", e);
        mostrarNotificacion('Error al buscar la ubicación', 'error');
    }
};

const toggleMapSize = async () => {
    isMapExpanded.value = !isMapExpanded.value;
    await nextTick();
    setTimeout(() => {
        if (map) map.invalidateSize();
    }, 300);
};

const irASeleccionActividades = () => {
    document.getElementById('tipos-actividad')?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
    });
};

watch(() => props.abrir, async (estaAbierto) => {
    if (estaAbierto) {
        if (!bloqueoScrollActivo) {
            bodyOverflowAnterior = document.body.style.overflow;
            document.body.style.overflow = 'hidden';
            bloqueoScrollActivo = true;
        }
        fetchCategorias();
        fetchEstandar();
        await nextTick();
        setTimeout(() => {
            initMap();
        }, 150);
    } else if (bloqueoScrollActivo) {
        document.body.style.overflow = bodyOverflowAnterior;
        bloqueoScrollActivo = false;
    }
}, { immediate: true });

onBeforeUnmount(() => {
    if (bloqueoScrollActivo) document.body.style.overflow = bodyOverflowAnterior;
});

// --- ENVÍO ---
const Enviar = async () => {
    if (searchQuery.value) newTour.ubicacion = searchQuery.value;
    if (!validarFormulario()) return;
    isLoading.value = true;
    try {
        const formData = new FormData();
        for (const key in newTour) {
            if (!['itinerario', 'incluido', 'actividades', 'archivos_subidos', 'imagen', 'imagen_paquete', 'modalidades_turismo', 'clasificacion_actividades', 'certificacion_aventura'].includes(key)) {
                if (newTour[key] !== null && newTour[key] !== undefined) {
                    if (key === 'latitud' || key === 'longitud') {
                        formData.append(key, Number(newTour[key]).toFixed(6));
                    } else if (key === 'fecha_realizacion') {
                        // Solo enviar si tiene valor; si está vacío, enviar string vacío para limpiarla
                        formData.append(key, newTour[key] || '');
                    } else {
                        formData.append(key, newTour[key]);
                    }
                }
            }
        }
        // Si fecha_realizacion está vacía, enviarla explícitamente para que el backend la limpie
        if (!newTour.fecha_realizacion) {
            formData.set('fecha_realizacion', '');
        }
        const itFiltrado = newTour.itinerario.filter(i => i.time.trim() || i.activity.trim());
        formData.append('itinerario', JSON.stringify(itFiltrado));
        const incFiltrado = newTour.incluido.filter(i => i.item.trim());
        formData.append('incluido', JSON.stringify(incFiltrado));
        formData.append('modalidades_turismo', JSON.stringify(newTour.modalidades_turismo));
        formData.append('clasificacion_actividades', JSON.stringify(newTour.clasificacion_actividades));
        formData.append('certificacion_aventura', JSON.stringify(newTour.certificacion_aventura));
        if (newTour.actividades?.length > 0) {
            newTour.actividades.forEach(id => formData.append('actividades', id));
        }
        newTour.imagen.forEach(imgObj => {
            if (imgObj.file) formData.append('archivos_subidos', imgObj.file);
        });
        // IDs de imágenes a eliminar (solo en edición)
        if (imagenesAEliminar.value.length > 0) {
            imagenesAEliminar.value.forEach(id => formData.append('imagenes_eliminar', id));
        }
        const resultado = await guardarDatos(formData, newTour.id);
        mostrarNotificacion(newTour.id ? '¡Tour actualizado correctamente!' : '¡Tour creado correctamente!', 'exito');
        limpiarFormulario();
        emit('guardadoExitoso', resultado);
        setTimeout(() => emit('cerrar'), 1500);
    } catch (error) {
        console.error("Error al enviar", error);
        const respuesta = error.response?.data;
        if (respuesta && typeof respuesta === 'object') {
            Object.entries(respuesta).forEach(([campo, mensajes]) => {
                errores[campo] = Array.isArray(mensajes) ? mensajes.join(' ') : String(mensajes);
            });
        }
        mostrarNotificacion('Revisa los campos señalados antes de guardar.', 'error');
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
  <Teleport to="body">
    <!-- Overlay + Modal -->
    <div v-if="abrir"
      class="fixed inset-0 z-[60] flex items-center justify-center overflow-hidden p-2 sm:p-4"
      @click.self="emit('cerrar')">

      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/85 backdrop-blur-md"></div>

      <!-- Modal Card -->
      <div class="relative flex max-h-[96dvh] w-full max-w-6xl flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#0d2114] shadow-2xl animate-fade-in-up sm:max-h-[94vh] sm:rounded-[2rem]">

        <!-- === HEADER GRADIENTE === -->
        <div class="relative flex-shrink-0 overflow-hidden bg-gradient-to-br from-emerald-600 to-emerald-900 px-5 py-6 sm:px-8 sm:py-7">
          <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/leaf.png')] opacity-10"></div>
          <div class="relative z-10 flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-3">
                <span class="inline-flex items-center gap-1.5 text-[10px] font-black tracking-[0.2em] uppercase text-emerald-200/70">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                  {{ paquete ? 'Editando Tour' : 'Nuevo Tour' }}
                </span>
              </div>
              <h2 class="text-2xl font-black leading-tight text-white sm:text-3xl">
                {{ paquete ? paquete.nombre : 'Configurar Experiencia' }}
              </h2>
              <p class="text-emerald-100/60 text-sm mt-1.5 font-medium italic">
                {{ paquete ? 'Actualiza los datos de esta experiencia premium' : 'Diseña una aventura única para tus viajeros' }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <router-link to="/estandar-paquetes"
                class="hidden sm:inline-flex min-h-11 items-center rounded-xl border border-white/15 bg-black/15 px-4 text-xs font-bold text-white/80 transition hover:bg-black/25 focus:outline-none focus:ring-2 focus:ring-white/70">
                Información del estándar
              </router-link>
            <button @click="emit('cerrar')" type="button" aria-label="Cerrar formulario"
              class="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-2xl bg-white/10 hover:bg-white/20 text-white transition-all hover:rotate-90 duration-300 border border-white/5">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
            </div>
          </div>
        </div>

        <!-- === LOADING OVERLAY === -->
        <div v-if="isLoading"
          class="absolute inset-0 bg-[#0d2114]/90 backdrop-blur-md z-20 flex flex-col items-center justify-center rounded-[2.5rem]">
          <div class="w-16 h-16 border-4 border-emerald-500/10 border-t-emerald-500 rounded-full animate-spin mb-6"></div>
          <p class="text-white font-black text-xl tracking-tight">{{ paquete ? 'Actualizando...' : 'Guardando tour...' }}</p>
          <p class="text-emerald-500/50 text-sm mt-2 font-medium">Esto tomará solo un momento</p>
        </div>

        <!-- === CUERPO DEL FORMULARIO === -->
        <div class="form-scroll flex-1 overflow-x-hidden overflow-y-auto bg-[#0a1a0f]">
          <form @submit.prevent="Enviar" class="space-y-8 p-5 sm:space-y-12 sm:p-10">

            <div v-if="totalErrores" data-form-error="true" role="alert" class="rounded-2xl border border-rose-400/30 bg-rose-400/10 p-5 text-sm text-rose-100">
              <p class="font-black">Faltan {{ totalErrores }} campos o secciones por revisar.</p>
              <p class="mt-1 text-rose-100/70">Los mensajes aparecen junto a la información que debes corregir.</p>
            </div>

            <div v-if="mensajesCarga.length" role="alert" class="rounded-2xl border border-amber-300/30 bg-amber-300/10 p-5 text-sm text-amber-100">
              <p class="font-black">No se pudieron cargar todos los datos del formulario.</p>
              <ul class="mt-2 list-disc space-y-1 pl-5 text-amber-100/75">
                <li v-for="mensaje in mensajesCarga" :key="mensaje">{{ mensaje }}</li>
              </ul>
            </div>

            <div class="rounded-2xl border border-sky-300/20 bg-sky-300/[0.07] p-5 sm:flex sm:items-center sm:justify-between sm:gap-6">
              <div>
                <p class="text-xs font-black uppercase tracking-[0.15em] text-sky-200">Ficha técnica MEJ-003</p>
                <p class="mt-2 text-sm leading-6 text-white/60">La dificultad se registra por actividad. La escala de riesgo 1–10 es una referencia interna y no reemplaza la norma técnica.</p>
              </div>
              <router-link to="/estandar-paquetes" class="mt-4 inline-flex min-h-11 flex-none items-center rounded-xl border border-sky-200/20 px-4 text-xs font-bold text-sky-100 hover:bg-sky-100/10 focus:outline-none focus:ring-2 focus:ring-sky-300 sm:mt-0">
                Ver base y fuentes
              </router-link>
            </div>

            <!-- ─── SECCIÓN 1: INFO BÁSICA ─── -->
            <section>
              <div class="flex items-center gap-4 mb-8">
                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">1</div>
                <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Información Básica</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
              </div>

              <!-- Estado Activo -->
              <div class="mb-8 flex items-center justify-between bg-white/5 border border-white/10 rounded-[1.5rem] px-6 py-5">
                <div>
                  <h4 class="text-sm font-black text-white tracking-tight">Estado del Tour</h4>
                  <p class="text-xs text-white/30 mt-1 font-medium italic">Define si el tour está visible y activo para los clientes.</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="newTour.activo" class="sr-only peer">
                  <div class="w-12 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-6 peer-checked:after:border-emerald-500 after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white/20 after:rounded-full after:h-[16px] after:w-[16px] after:transition-all peer-checked:bg-emerald-600/40 border border-white/5"></div>
                  <span class="ml-4 text-[10px] font-black uppercase tracking-[0.1em] w-16" :class="newTour.activo ? 'text-emerald-400' : 'text-white/20'">
                    {{ newTour.activo ? 'Activo' : 'Inactivo' }}
                  </span>
                </label>
              </div>

              <!-- Nombre -->
              <div class="mb-6">
                <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Nombre del Tour <span class="text-emerald-500">*</span></label>
                <input v-model="newTour.nombre" type="text" placeholder="Ej: Aventura en el Corazón del Amazonas"
                  :class="['w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50',
                  errores.nombre ? 'border-rose-500/50' : '']">
                <p v-if="errores.nombre" class="text-[10px] text-rose-400 mt-2 font-bold italic flex items-center gap-1 px-1">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                  {{ errores.nombre }}
                </p>
              </div>

              <!-- Categoría -->
              <div class="mb-6 relative">
                <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Categoría del Tour <span class="text-emerald-500">*</span></label>
                <select v-model="newTour.categoria_paquete"
                  :class="['w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold focus:outline-none focus:bg-white/10 transition-all appearance-none cursor-pointer focus:border-emerald-500/50',
                  errores.categoria_paquete ? 'border-rose-500/50' : '']">
                  <option value="" disabled selected class="bg-[#0d2114]">Selecciona una categoría...</option>
                  <optgroup v-for="grupo in [...new Set(categorias.map(c => c.grupo))]" :key="grupo" :label="grupo" class="bg-[#0d2114]">
                    <option v-for="cat in categorias.filter(c => c.grupo === grupo)" :key="cat.id" :value="cat.id" class="bg-[#0d2114]">
                      {{ cat.nombre }}
                    </option>
                  </optgroup>
                </select>
                <div class="pointer-events-none absolute bottom-4.5 right-6 flex items-center text-emerald-500/50">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"></path></svg>
                </div>
                <p v-if="errores.categoria_paquete" class="text-[10px] text-rose-400 mt-2 font-bold px-1">{{ errores.categoria_paquete }}</p>
              </div>

              <!-- Descripción -->
              <div class="mb-8">
                <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Descripción <span class="text-emerald-500">*</span></label>
                <textarea v-model="newTour.descripcion" rows="4"
                  placeholder="Describe qué hace única esta experiencia..."
                  :class="['w-full bg-white/5 border border-white/10 rounded-[1.5rem] px-6 py-4 text-white font-medium focus:outline-none focus:bg-white/10 transition-all resize-none placeholder:text-white/10 focus:border-emerald-500/50',
                  errores.descripcion ? 'border-rose-500/50' : '']"></textarea>
                <p v-if="errores.descripcion" class="text-[10px] text-rose-400 mt-2 font-bold px-1">{{ errores.descripcion }}</p>
              </div>

              <!-- Grid: Precio + Duración + Capacidad -->
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Precio (COP) <span class="text-emerald-500">*</span></label>
                  <div class="relative">
                    <span class="absolute left-6 top-1/2 -translate-y-1/2 text-white/20 font-black text-lg">$</span>
                    <input v-model="newTour.precio" type="number" placeholder="0"
                      :class="['w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-6 py-4 text-white font-black tabular-nums focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50 text-xl',
                      errores.precio ? 'border-rose-500/50' : '']">
                  </div>
                  <p v-if="errores.precio" class="text-[10px] text-rose-400 mt-2 font-bold px-1">{{ errores.precio }}</p>
                </div>
                <div>
                  <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Duración <span class="text-emerald-500">*</span></label>
                  <input v-model="newTour.duracion" type="text" placeholder="Ej: 8 horas"
                    :class="['w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50 text-center',
                    errores.duracion ? 'border-rose-500/50' : '']">
                  <p v-if="errores.duracion" class="text-[10px] text-rose-400 mt-2 font-bold px-1">{{ errores.duracion }}</p>
                </div>
                <div>
                  <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Capacidad Máx. <span class="text-emerald-500">*</span></label>
                  <input v-model="newTour.capacidad" type="number" placeholder="20"
                    :class="['w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-black focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50 text-center text-xl',
                    errores.capacidad ? 'border-rose-500/50' : '']">
                  <p v-if="errores.capacidad" class="text-[10px] text-rose-400 mt-2 font-bold px-1">{{ errores.capacidad }}</p>
                </div>
              </div>

              <!-- ─── FECHA DE REALIZACIÓN ─── -->
              <div class="mt-8 p-6 rounded-[2rem] border-2 transition-all"
                :class="tipoPaqueteAuto === 'fijo' ? 'border-emerald-500/30 bg-emerald-500/5 shadow-2xl shadow-emerald-500/10' : 'border-white/5 bg-white/3'">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-5 gap-3">
                  <div>
                    <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">Personalización Temporal</label>
                    <p class="text-[10px] text-white/20 mt-1 font-bold italic">Si estableces una fecha, el tour será <strong class="text-emerald-500/50">Fijo</strong> (una sola salida). Si no, será <strong class="text-emerald-500/50">Flexible</strong>.</p>
                  </div>
                  <!-- Badge dinámico -->
                  <span :class="['inline-flex items-center gap-2 px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all shadow-xl',
                    tipoPaqueteAuto === 'fijo'
                      ? 'bg-emerald-500 text-black'
                      : 'bg-white/10 text-white/40 border border-white/5'
                  ]">
                    <svg v-if="tipoPaqueteAuto === 'fijo'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    {{ tipoPaqueteAuto === 'fijo' ? 'Tour Fijo' : 'Tour Flexible' }}
                  </span>
                </div>
                <div class="flex items-center gap-4">
                  <input v-model="newTour.fecha_realizacion" type="date"
                    class="flex-1 bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-black focus:outline-none focus:border-emerald-500/50 transition-all uppercase tracking-widest text-sm"
                  >
                  <button v-if="newTour.fecha_realizacion" @click.prevent="newTour.fecha_realizacion = ''"
                    class="h-[56px] px-6 rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500 hover:text-white transition-all text-[10px] font-black uppercase tracking-widest flex items-center gap-2 shadow-xl shadow-rose-900/20">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                    Reset
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 2: UBICACIÓN Y MAPA ─── -->
            <section>
              <div class="flex items-center gap-4 mb-8">
                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">2</div>
                <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Ubicación Geográfica</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
              </div>

              <!-- Input Búsqueda Ubicación -->
              <div class="mb-6 relative group">
                <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Punto de Encuentro <span class="text-emerald-500">*</span></label>
                <div class="relative">
                  <div class="absolute left-6 top-1/2 -translate-y-1/2 text-emerald-500/50">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                  </div>
                  <input v-model="searchQuery"
                    type="text" placeholder="Busca una ciudad, parque o coordenadas..."
                    class="w-full bg-white/5 border border-white/10 rounded-2xl pl-14 pr-6 py-4 text-white font-bold focus:outline-none focus:bg-white/10 focus:border-emerald-500/50 transition-all placeholder:text-white/10">
                </div>

                <!-- Lista de Sugerencias -->
                <div v-if="suggestions.length > 0"
                  class="absolute z-30 left-0 right-0 mt-3 bg-[#0d2114] border border-white/10 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-xl animate-fade-in">
                  <ul class="divide-y divide-white/5">
                    <li v-for="s in suggestions" :key="s.place_id"
                        @click="selectSuggestion(s)"
                        class="px-6 py-4 hover:bg-emerald-50/10 cursor-pointer transition-all group flex items-start gap-3">
                      <svg class="w-4 h-4 text-emerald-500 mt-0.5 group-hover:scale-125 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                      <div>
                        <p class="text-sm font-black text-white group-hover:text-emerald-400 transition-colors">{{ s.display_name.split(',')[0] }}</p>
                        <p class="text-[10px] text-white/30 font-bold italic truncate max-w-[400px]">{{ s.display_name.split(',').slice(1).join(',') }}</p>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- MAPA -->
              <div class="space-y-4">
                <div class="relative bg-black/20 rounded-[2rem] border border-white/10 overflow-hidden shadow-inner group">
                  <div id="map" ref="mapContainer" class="w-full h-80 z-10 brightness-90 contrast-110"></div>
                  <!-- Overlay informativo -->
                  <div class="absolute bottom-6 left-6 right-6 z-20 pointer-events-none">
                    <div class="inline-flex items-center gap-3 bg-black/60 backdrop-blur-md px-5 py-3 rounded-2xl border border-white/10 text-white shadow-2xl">
                      <div class="w-8 h-8 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                      </div>
                      <div>
                        <p class="text-[9px] font-black text-emerald-500 uppercase tracking-widest leading-none mb-1">Coordenadas del Pin</p>
                        <p class="text-xs font-black font-mono tracking-tight">{{ newTour.latitud || '0.0000' }} , {{ newTour.longitud || '0.0000' }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <p v-if="errores.ubicacion" class="text-[10px] text-rose-400 font-bold px-1 flex items-center gap-1">
                   <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                   {{ errores.ubicacion }}
                </p>
              </div>
            </section>

            <!-- ─── SECCIÓN 3: ATRIBUTOS EXTRA ─── -->
            <section>
              <div class="flex items-center gap-4 mb-8">
                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">3</div>
                <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Atributos Adicionales</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
              </div>

              <div class="bg-white/5 border border-white/10 rounded-[2rem] p-6 sm:p-8 space-y-8">
                <div>
                  <label class="block text-[10px] font-black text-white/40 uppercase tracking-[0.15em] mb-4">Modalidades del paquete <span class="text-emerald-400">*</span></label>
                  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    <label v-for="modalidad in estandar?.modalidades || []" :key="modalidad.value"
                      class="flex min-h-12 cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 transition"
                      :class="newTour.modalidades_turismo.includes(modalidad.value) ? 'border-emerald-400/40 bg-emerald-400/10 text-white' : 'border-white/10 bg-black/10 text-white/55 hover:border-white/20'">
                      <input v-model="newTour.modalidades_turismo" type="checkbox" :value="modalidad.value" class="h-4 w-4 accent-emerald-500">
                      <span class="text-xs font-bold">{{ modalidad.label }}</span>
                    </label>
                  </div>
                  <p v-if="errores.modalidades_turismo" class="mt-3 text-xs font-semibold text-rose-300">{{ errores.modalidades_turismo }}</p>
                </div>

                <!-- Checkboxes Actividades -->
                <div id="tipos-actividad" class="scroll-mt-6">
                  <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-6 px-1">Tipos de Actividad <span class="text-emerald-500">*</span></label>
                  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    <label v-for="actividad in actividadesDisponibles" :key="actividad.id"
                      class="relative flex items-center gap-3 p-4 rounded-2xl border transition-all cursor-pointer group overflow-hidden"
                      :class="newTour.actividades.includes(actividad.id)
                        ? 'bg-emerald-500/10 border-emerald-500/30'
                        : 'bg-white/3 border-white/5 hover:border-white/10 hover:bg-white/5'">

                      <input type="checkbox" :value="actividad.id" v-model="newTour.actividades" class="sr-only">
                      <div class="w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all flex-shrink-0 z-10"
                        :class="newTour.actividades.includes(actividad.id) ? 'bg-emerald-50 border-emerald-500' : 'border-white/10 bg-black/20'">
                        <svg v-if="newTour.actividades.includes(actividad.id)" class="w-4 h-4 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><polyline points="20 6 9 17 4 12"></polyline></svg>
                      </div>
                      <span class="text-xs font-black tracking-tight z-10 transition-colors"
                        :class="newTour.actividades.includes(actividad.id) ? 'text-white' : 'text-white/40 group-hover:text-white/60'">
                        {{ actividad.nombre }}
                      </span>
                      <span v-if="actividad.norma_tecnica" class="ml-auto rounded-md bg-sky-300/10 px-2 py-1 text-[9px] font-bold text-sky-200">{{ actividad.norma_tecnica }}</span>
                    </label>
                  </div>
                  <p v-if="errores.actividades" class="text-[10px] text-rose-400 mt-4 font-bold px-1">{{ errores.actividades }}</p>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 4: FICHA TÉCNICA Y SEGURIDAD ─── -->
            <section aria-labelledby="titulo-seguridad" class="rounded-[1.75rem] border border-white/10 bg-white/[0.025] p-5 sm:p-7">
              <div class="flex flex-col gap-5 border-b border-white/10 pb-6 sm:flex-row sm:items-start sm:justify-between">
                <div class="flex items-start gap-4">
                  <div class="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl border border-sky-300/25 bg-sky-300/10 text-sm font-black text-sky-200">4</div>
                  <div>
                    <h3 id="titulo-seguridad" class="text-lg font-black tracking-tight text-white">Dificultad, requisitos y seguridad</h3>
                    <p class="mt-1 max-w-2xl text-sm leading-6 text-white/55">Describe cómo se realiza el tour, quién puede participar y qué medidas protegen al viajero.</p>
                  </div>
                </div>
                <div class="flex flex-wrap items-center gap-2 sm:justify-end">
                  <span class="rounded-full border border-white/10 bg-black/15 px-3 py-1.5 text-[11px] font-bold text-white/60">
                    {{ actividadesSeleccionadas.length }} {{ actividadesSeleccionadas.length === 1 ? 'actividad' : 'actividades' }}
                  </span>
                  <span class="rounded-full border border-emerald-300/15 bg-emerald-300/[0.08] px-3 py-1.5 text-[11px] font-bold text-emerald-200">
                    {{ camposOperacionCompletos }}/4 campos completos
                  </span>
                </div>
              </div>

              <div class="pt-7">
                <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
                  <div>
                    <h4 class="text-sm font-black text-white">Dificultad por actividad</h4>
                    <p class="mt-1 text-xs leading-5 text-white/45">Usa la escala propia de cada actividad seleccionada.</p>
                  </div>
                  <router-link to="/estandar-paquetes" class="text-xs font-bold text-sky-200 underline decoration-sky-200/30 underline-offset-4 hover:text-sky-100 focus:outline-none focus:ring-2 focus:ring-sky-300/50">
                    Consultar cómo se clasifica
                  </router-link>
                </div>

                <div v-if="!actividadesSeleccionadas.length" class="flex flex-col items-center rounded-2xl border border-dashed border-white/15 bg-black/10 px-5 py-7 text-center sm:flex-row sm:justify-between sm:text-left">
                  <div class="flex flex-col items-center gap-3 sm:flex-row">
                    <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-white/45">
                      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
                    </div>
                    <div>
                      <p class="text-sm font-bold text-white/75">Primero selecciona las actividades del tour</p>
                      <p class="mt-1 text-xs text-white/40">Aquí aparecerá una ficha técnica para cada actividad.</p>
                    </div>
                  </div>
                  <button type="button" @click="irASeleccionActividades" class="mt-5 min-h-11 rounded-xl border border-white/15 bg-white/5 px-4 text-xs font-bold text-white/75 transition hover:border-emerald-300/30 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-300/50 sm:mt-0">
                    Elegir actividades
                  </button>
                </div>

                <div v-else class="space-y-4">
                  <article v-for="actividad in actividadesSeleccionadas" :key="`ficha-${actividad.id}`" class="rounded-2xl border border-white/10 bg-black/10 p-5 sm:p-6">
                    <div class="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <h5 class="font-black text-white">{{ actividad.nombre }}</h5>
                        <p class="mt-1 text-xs text-white/45">Riesgo interno {{ actividad.nivel_riesgo }}/10<span v-if="actividad.sistema_dificultad"> · {{ actividad.sistema_dificultad }}</span></p>
                      </div>
                      <span v-if="actividad.norma_tecnica" class="rounded-full bg-sky-300/10 px-3 py-1.5 text-[10px] font-black text-sky-200">{{ actividad.norma_tecnica }}</span>
                      <span v-else class="rounded-full bg-white/5 px-3 py-1.5 text-[10px] font-bold text-white/40">Descripción técnica libre</span>
                    </div>

                    <div class="mt-5 grid gap-4" :class="actividad.opciones_dificultad?.length ? 'md:grid-cols-2' : ''">
                      <div v-if="actividad.opciones_dificultad?.length">
                        <label :for="`nivel-${actividad.id}`" class="mb-2 block text-xs font-bold text-white/70">Nivel técnico</label>
                        <select :id="`nivel-${actividad.id}`" v-model="fichaActividad(actividad).nivel" class="min-h-12 w-full rounded-xl border border-white/10 bg-[#102219] px-4 text-sm font-semibold text-white focus:border-sky-300/50 focus:outline-none focus:ring-2 focus:ring-sky-300/20">
                          <option value="">Selecciona un nivel…</option>
                          <option v-for="opcion in actividad.opciones_dificultad" :key="opcion.value" :value="opcion.value">{{ opcion.label }}</option>
                        </select>
                      </div>
                      <div>
                        <label :for="`descripcion-actividad-${actividad.id}`" class="mb-2 block text-xs font-bold text-white/70">¿Qué encontrará el viajero?</label>
                        <textarea :id="`descripcion-actividad-${actividad.id}`" v-model="fichaActividad(actividad).descripcion" rows="3" placeholder="Ej.: altura, caudal, terreno, experiencia necesaria…" class="w-full rounded-xl border border-white/10 bg-[#102219] px-4 py-3 text-sm leading-6 text-white placeholder:text-white/30 focus:border-sky-300/50 focus:outline-none focus:ring-2 focus:ring-sky-300/20"></textarea>
                      </div>
                    </div>
                  </article>
                  <p v-if="errores.clasificacion_actividades" class="rounded-xl bg-rose-400/10 px-4 py-3 text-xs font-semibold text-rose-200">{{ errores.clasificacion_actividades }}</p>
                </div>
              </div>

              <fieldset class="mt-8 border-t border-white/10 pt-7">
                <legend class="sr-only">Información operativa del tour</legend>
                <div class="mb-5 flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h4 class="text-sm font-black text-white">Información operativa del tour</h4>
                    <p class="mt-1 text-xs leading-5 text-white/45">Responde cada pregunta con información concreta que la agencia pueda cumplir.</p>
                  </div>
                  <span v-if="requiereCertificacion" class="rounded-lg bg-amber-300/10 px-3 py-1.5 text-[10px] font-black uppercase tracking-wider text-amber-200">3 campos obligatorios por aventura</span>
                </div>

                <div class="grid gap-4 md:grid-cols-2">
                  <article class="rounded-2xl border bg-black/10 p-4 sm:p-5" :class="errores.requisitos_participantes ? 'border-rose-400/40' : 'border-white/10'">
                    <div class="flex items-start gap-3">
                      <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-emerald-300/10 text-emerald-200">
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372A9.337 9.337 0 0 0 21 18.9v-3.75M15 19.128v-.003c0-1.113-.285-2.161-.786-3.073M15 19.128v.106A12.318 12.318 0 0 1 8.624 21C6.33 21 4.18 20.38 2.332 19.295a6.92 6.92 0 0 1 3.04-4.343M9 6.75a3.75 3.75 0 1 1 0 7.5 3.75 3.75 0 0 1 0-7.5Z"/></svg>
                      </div>
                      <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-2">
                          <label for="requisitos-participantes" class="text-sm font-black text-white">¿Quién puede participar?</label>
                          <span class="text-[10px] font-bold" :class="requiereCertificacion ? 'text-amber-200' : 'text-white/35'">{{ requiereCertificacion ? 'Obligatorio' : 'Opcional' }}</span>
                        </div>
                        <p class="mt-1 text-xs leading-5 text-white/40">Edad, salud, condición física o experiencia necesaria.</p>
                      </div>
                    </div>
                    <textarea id="requisitos-participantes" v-model="newTour.requisitos_participantes" rows="4" placeholder="Ej.: mayores de 14 años, saber nadar y no tener restricciones cardíacas." class="mt-4 w-full rounded-xl border border-white/10 bg-[#102219] px-4 py-3 text-sm leading-6 text-white placeholder:text-white/30 focus:border-emerald-300/50 focus:outline-none focus:ring-2 focus:ring-emerald-300/15"></textarea>
                    <p v-if="errores.requisitos_participantes" class="mt-2 text-xs font-semibold text-rose-300">{{ errores.requisitos_participantes }}</p>
                  </article>

                  <article class="rounded-2xl border bg-black/10 p-4 sm:p-5" :class="errores.condiciones_operacion ? 'border-rose-400/40' : 'border-white/10'">
                    <div class="flex items-start gap-3">
                      <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-sky-300/10 text-sky-200">
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
                      </div>
                      <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-2">
                          <label for="condiciones-operacion" class="text-sm font-black text-white">¿Cuándo puede realizarse?</label>
                          <span class="text-[10px] font-bold" :class="requiereCertificacion ? 'text-amber-200' : 'text-white/35'">{{ requiereCertificacion ? 'Obligatorio' : 'Opcional' }}</span>
                        </div>
                        <p class="mt-1 text-xs leading-5 text-white/40">Clima, horarios, cupos y motivos para suspender.</p>
                      </div>
                    </div>
                    <textarea id="condiciones-operacion" v-model="newTour.condiciones_operacion" rows="4" placeholder="Ej.: sujeto al caudal del río; se suspende durante tormentas eléctricas." class="mt-4 w-full rounded-xl border border-white/10 bg-[#102219] px-4 py-3 text-sm leading-6 text-white placeholder:text-white/30 focus:border-sky-300/50 focus:outline-none focus:ring-2 focus:ring-sky-300/15"></textarea>
                    <p v-if="errores.condiciones_operacion" class="mt-2 text-xs font-semibold text-rose-300">{{ errores.condiciones_operacion }}</p>
                  </article>

                  <article class="rounded-2xl border bg-black/10 p-4 sm:p-5" :class="errores.medidas_seguridad ? 'border-rose-400/40' : 'border-white/10'">
                    <div class="flex items-start gap-3">
                      <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-rose-300/10 text-rose-200">
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75m5.25-4.5c0 6.75-3.75 12-8.25 13.5C7.5 17.25 3.75 12 3.75 5.25 6.25 5.25 9 4 12 2.25c3 1.75 5.75 3 8.25 3Z"/></svg>
                      </div>
                      <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-2">
                          <label for="medidas-seguridad" class="text-sm font-black text-white">¿Cómo se protege al viajero?</label>
                          <span class="text-[10px] font-bold" :class="requiereCertificacion ? 'text-amber-200' : 'text-white/35'">{{ requiereCertificacion ? 'Obligatorio' : 'Opcional' }}</span>
                        </div>
                        <p class="mt-1 text-xs leading-5 text-white/40">Equipos, inducción, comunicación y respuesta a emergencias.</p>
                      </div>
                    </div>
                    <textarea id="medidas-seguridad" v-model="newTour.medidas_seguridad" rows="4" placeholder="Ej.: casco y chaleco certificados, guía líder, botiquín y protocolo de evacuación." class="mt-4 w-full rounded-xl border border-white/10 bg-[#102219] px-4 py-3 text-sm leading-6 text-white placeholder:text-white/30 focus:border-rose-300/50 focus:outline-none focus:ring-2 focus:ring-rose-300/15"></textarea>
                    <p v-if="errores.medidas_seguridad" class="mt-2 text-xs font-semibold text-rose-300">{{ errores.medidas_seguridad }}</p>
                  </article>

                  <article class="rounded-2xl border border-white/10 bg-black/10 p-4 sm:p-5">
                    <div class="flex items-start gap-3">
                      <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-lime-300/10 text-lime-200">
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582"/></svg>
                      </div>
                      <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-2">
                          <label for="informacion-sostenibilidad" class="text-sm font-black text-white">¿Cómo se cuida el destino?</label>
                          <span class="text-[10px] font-bold text-white/35">Opcional</span>
                        </div>
                        <p class="mt-1 text-xs leading-5 text-white/40">Compromisos ambientales, culturales y con la comunidad.</p>
                      </div>
                    </div>
                    <textarea id="informacion-sostenibilidad" v-model="newTour.informacion_sostenibilidad" rows="4" placeholder="Ej.: no dejar residuos, respetar la fauna y comprar a emprendimientos locales." class="mt-4 w-full rounded-xl border border-white/10 bg-[#102219] px-4 py-3 text-sm leading-6 text-white placeholder:text-white/30 focus:border-lime-300/50 focus:outline-none focus:ring-2 focus:ring-lime-300/15"></textarea>
                  </article>
                </div>
              </fieldset>

              <div v-if="requiereCertificacion" class="mt-6 rounded-2xl border border-amber-300/20 bg-amber-300/[0.06] p-5 sm:p-6">
                <div class="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p class="text-xs font-black uppercase tracking-widest text-amber-200">Certificación de turismo de aventura</p>
                    <p class="mt-2 max-w-2xl text-xs leading-5 text-amber-50/60">Para publicar el tour como activo, registra una certificación vigente emitida por un organismo acreditado. El sistema conserva la referencia; no sustituye la verificación oficial.</p>
                  </div>
                  <select v-model="newTour.certificacion_aventura.estado" class="min-h-11 rounded-xl border border-amber-200/20 bg-[#2a2816] px-4 text-sm font-bold text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-300">
                    <option value="pendiente">En trámite / pendiente</option>
                    <option value="vigente">Vigente</option>
                    <option value="vencida">Vencida</option>
                  </select>
                </div>
                <div class="mt-5 grid gap-4 md:grid-cols-3">
                  <div>
                    <label class="mb-2 block text-[10px] font-bold uppercase tracking-wider text-amber-100/50">Organismo evaluador</label>
                    <input v-model="newTour.certificacion_aventura.organismo" type="text" placeholder="Nombre del OEC" class="min-h-12 w-full rounded-xl border border-amber-100/15 bg-black/15 px-4 text-sm text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-amber-300/40">
                  </div>
                  <div>
                    <label class="mb-2 block text-[10px] font-bold uppercase tracking-wider text-amber-100/50">Código o certificado</label>
                    <input v-model="newTour.certificacion_aventura.codigo" type="text" placeholder="Código verificable" class="min-h-12 w-full rounded-xl border border-amber-100/15 bg-black/15 px-4 text-sm text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-amber-300/40">
                  </div>
                  <div>
                    <label class="mb-2 block text-[10px] font-bold uppercase tracking-wider text-amber-100/50">Vigente hasta</label>
                    <input v-model="newTour.certificacion_aventura.vigente_hasta" type="date" class="min-h-12 w-full rounded-xl border border-amber-100/15 bg-black/15 px-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-300/40">
                  </div>
                </div>
                <p v-if="errores.certificacion_aventura" class="mt-3 text-xs font-semibold text-rose-300">{{ errores.certificacion_aventura }}</p>
              </div>
            </section>

            <!-- ─── SECCIÓN 5: ITINERARIO ─── -->
            <section>
              <div class="flex items-center gap-4 mb-8">
                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">5</div>
                <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Crónica del Viaje</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                <button @click.prevent="addItineraryItem" type="button"
                  class="flex-shrink-0 flex items-center gap-2 text-[10px] text-emerald-400 font-black bg-emerald-500/10 hover:bg-emerald-500/20 px-4 py-2 rounded-xl transition-all border border-emerald-500/10 uppercase tracking-widest shadow-xl">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                  Agregar
                </button>
              </div>
              
              <div class="space-y-4">
                <div v-for="(item, index) in newTour.itinerario" :key="'iti-'+index"
                  class="flex gap-4 items-center group bg-white/3 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-all">
                  <span class="text-[10px] text-white/20 font-black w-6 text-center flex-shrink-0 italic">{{ (index + 1).toString().padStart(2, '0') }}</span>
                  <div class="w-28 flex-shrink-0 relative">
                    <input v-model="item.time" type="time"
                      class="w-full bg-black/20 border border-white/5 rounded-xl px-3 py-2.5 text-xs text-white font-bold focus:outline-none focus:border-emerald-500/50 transition-all appearance-none cursor-pointer">
                  </div>
                  <input v-model="item.activity" type="text" :placeholder="`Actividad ${index + 1}...`"
                    class="flex-1 bg-black/20 border border-white/5 rounded-xl px-5 py-2.5 text-xs text-white font-medium focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-white/10">
                  <button v-if="newTour.itinerario.length > 1" @click.prevent="removeItineraryItem(index)" type="button"
                    class="w-8 h-8 flex items-center justify-center rounded-xl text-white/10 hover:text-rose-400 hover:bg-rose-500/10 transition-all opacity-0 group-hover:opacity-100 flex-shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 6: QUÉ INCLUYE ─── -->
            <section>
              <div class="flex items-center gap-4 mb-8">
                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">6</div>
                <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Beneficios Incluidos</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                <button @click.prevent="addIncludedItem" type="button"
                  class="flex-shrink-0 flex items-center gap-2 text-[10px] text-emerald-400 font-black bg-emerald-500/10 hover:bg-emerald-500/20 px-4 py-2 rounded-xl transition-all border border-emerald-500/10 uppercase tracking-widest shadow-xl">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                  Agregar
                </button>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-for="(inc, index) in newTour.incluido" :key="'inc-'+index"
                  class="flex gap-3 items-center group bg-white/3 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-all">
                  <div class="w-6 h-6 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0 shadow-lg shadow-emerald-500/10">
                    <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                  </div>
                  <input v-model="inc.item" type="text" :placeholder="`Item ${index + 1}...`"
                    class="flex-1 bg-transparent border-none p-0 text-xs text-white font-medium focus:ring-0 placeholder:text-white/10">
                  <button v-if="newTour.incluido.length > 1" @click.prevent="removeIncludedItem(index)" type="button"
                    class="w-7 h-7 flex items-center justify-center rounded-lg text-white/10 hover:text-rose-400 hover:bg-rose-500/10 transition-all opacity-0 group-hover:opacity-100 flex-shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 7: GALERÍA ─── -->
            <section>
              <div class="flex items-center gap-4 mb-8">
                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">7</div>
                <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Galería Visual</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
              </div>

              <div class="bg-white/5 border border-white/10 rounded-[2rem] p-8">
                <!-- Imágenes existentes (modo edición) -->
                <div v-if="imagenesExistentes.length > 0" class="mb-10">
                  <p class="text-[10px] font-black text-white/20 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500/50"></span>
                    Colección Actual
                  </p>
                  <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4">
                    <div v-for="(img, index) in imagenesExistentes" :key="'existing-'+img.id"
                      class="relative group rounded-2xl overflow-hidden aspect-square bg-white/5 border border-white/10">
                      <img :src="img.url" class="w-full h-full object-cover">
                      <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                        <button @click.prevent="removeExistingImage(img.id, index)" type="button"
                          class="w-10 h-10 rounded-xl bg-rose-500 text-white flex items-center justify-center hover:bg-rose-600 transition-all shadow-xl">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                      </div>
                      <div v-if="img.es_portada" class="absolute top-2 left-2 bg-emerald-500 text-black text-[8px] font-black px-2 py-0.5 rounded shadow-xl uppercase tracking-tighter">Principal</div>
                    </div>
                  </div>
                </div>

                <!-- Aviso de imágenes a eliminar -->
                <div v-if="imagenesAEliminar.length > 0" class="mb-10 p-5 bg-rose-500/5 border border-rose-500/20 rounded-2xl animate-pulse">
                  <p class="text-[10px] text-rose-400 font-black uppercase tracking-widest flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    Pendiente de eliminación: {{ imagenesAEliminar.length }} elemento(s)
                  </p>
                </div>

                <!-- Drop Zone -->
                <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                  @click="$refs.fileInput.click()"
                  class="flex flex-col items-center justify-center border-2 border-dashed border-white/10 rounded-3xl p-10 hover:bg-white/5 hover:border-emerald-500/30 transition-all group cursor-pointer relative overflow-hidden">
                  <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect">
                  <div class="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-all duration-500 shadow-2xl">
                    <svg class="w-10 h-10 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  </div>
                  <p class="text-xs font-black text-white/60 uppercase tracking-widest">Añadir Nuevas Imágenes</p>
                  <p class="text-[9px] text-white/20 mt-2 font-bold italic">Arrastra o haz clic para subir fotos</p>
                </div>

                <!-- Preview Nuevas -->
                <div v-if="newTour.imagen.length > 0" class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-5 mt-10">
                  <div v-for="(img, idx) in newTour.imagen" :key="'new-'+idx"
                    class="relative aspect-square rounded-2xl overflow-hidden border border-emerald-500/30 group shadow-2xl shadow-emerald-500/10">
                    <img :src="img.url" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                      <button @click.prevent="removeImage(idx)" type="button"
                        class="w-10 h-10 rounded-xl bg-rose-500 text-white flex items-center justify-center hover:bg-rose-600 transition-all shadow-xl">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                      </button>
                    </div>
                    <div class="absolute top-2 left-2 bg-emerald-500 text-black text-[8px] font-black px-2 py-0.5 rounded shadow-xl uppercase tracking-tighter">Nuevo</div>
                  </div>
                </div>
              </div>
            </section>
          </form>
        </div>

        <!-- === FOOTER ACCIONES === -->
        <div class="flex flex-shrink-0 flex-col-reverse items-stretch justify-end gap-3 border-t border-white/10 bg-[#0d2114] p-4 sm:flex-row sm:items-center sm:gap-5 sm:px-8 sm:py-8">
          <button @click="emit('cerrar')" type="button" :disabled="isLoading"
            class="min-h-12 w-full rounded-2xl px-5 py-3 text-[10px] font-black uppercase tracking-widest text-white/50 transition-all hover:bg-white/5 hover:text-white disabled:opacity-50 sm:w-auto sm:px-8 sm:py-4">
            Descartar Cambios
          </button>
          <button @click="Enviar" type="button" :disabled="isLoading"
            class="group flex min-h-12 w-full items-center justify-center gap-3 rounded-2xl bg-emerald-600 px-6 py-3 text-[11px] font-black uppercase tracking-[0.16em] text-black shadow-xl shadow-emerald-900/20 transition-all hover:bg-emerald-500 disabled:opacity-50 sm:w-auto sm:px-10 sm:py-4 sm:tracking-[0.2em]">
            <svg v-if="isLoading" class="animate-spin h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-else>{{ paquete ? 'Guardar Cambios' : 'Confirmar Registro' }}</span>
            <svg v-if="!isLoading" class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3.5"><path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.animate-slide-in {
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to   { opacity: 1; transform: translateX(0); }
}
.form-scroll::-webkit-scrollbar { width: 5px; }
.form-scroll::-webkit-scrollbar-track { background: transparent; }
.form-scroll::-webkit-scrollbar-thumb { background-color: #d1d5db; border-radius: 20px; }
</style>
