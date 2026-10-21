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
const modalidadBusqueda = ref('');
const actividadBusqueda = ref('');
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
const normalizarBusqueda = (valor) => String(valor || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

// Catálogo de modalidades entregado por la API del estándar.
const modalidadesDisponibles = computed(() => {
    if (!Array.isArray(estandar.value?.modalidades)) return [];
    return estandar.value.modalidades;
});

const modalidadesFiltradas = computed(() => {
    const consulta = normalizarBusqueda(modalidadBusqueda.value);
    const lista = modalidadesDisponibles.value;
    if (!consulta) return lista;
    return lista.filter(modalidad =>
        normalizarBusqueda(modalidad.label).includes(consulta) ||
        normalizarBusqueda(modalidad.description || '').includes(consulta) ||
        normalizarBusqueda(modalidad.value).includes(consulta)
    );
});

const actividadesFiltradas = computed(() => {
    const consulta = normalizarBusqueda(actividadBusqueda.value);
    if (!consulta) return actividadesDisponibles.value;
    return actividadesDisponibles.value.filter(actividad =>
        normalizarBusqueda(`${actividad.nombre} ${actividad.categoria_nombre || ''} ${actividad.norma_tecnica || ''}`).includes(consulta)
    );
});

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
    modalidadBusqueda.value = '';
    actividadBusqueda.value = '';
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
            sistema: actividad.sistema_dificultad || 'Nivel de exigencia del recorrido (referencia interna)',
            nivel: '',
            descripcion: '',
        };
        newTour.clasificacion_actividades.push(ficha);
    }
    return ficha;
};

// Opciones de dificultad serializadas desde la base de datos.
const obtenerOpcionesDificultad = (actividad) => {
    return Array.isArray(actividad?.opciones_dificultad)
        ? actividad.opciones_dificultad
        : [];
};

// Color visual según el valor exacto de cada escala.
const colorDificultad = (valor) => {
    const v = String(valor || '').toLowerCase();
    if (['baja', 'i', 'ii', '1', '2', 'iniciacion', 'horizontal', 'contemplativo'].includes(v)) {
        return {
            dot: 'bg-emerald-400',
            borderActive: 'border-emerald-400 ring-2 ring-emerald-400/30 bg-emerald-500/15 text-white shadow-lg shadow-emerald-950/40',
        };
    }
    if (['media', 'intermedio', 'intermedia', 'iii', '3', '4', 'termico'].includes(v)) {
        return {
            dot: 'bg-amber-400',
            borderActive: 'border-amber-400 ring-2 ring-amber-400/30 bg-amber-500/15 text-white shadow-lg shadow-amber-950/40',
        };
    }
    return {
        dot: 'bg-rose-400',
        borderActive: 'border-rose-400 ring-2 ring-rose-400/30 bg-rose-500/15 text-white shadow-lg shadow-rose-950/40',
    };
};

const colorRiesgo = (nivel) => {
    const n = Number(nivel) || 0;
    if (n <= 3) return { text: 'text-emerald-300', bg: 'bg-emerald-500/15 border-emerald-500/30', label: 'Riesgo bajo' };
    if (n <= 6) return { text: 'text-amber-300', bg: 'bg-amber-500/15 border-amber-500/30', label: 'Riesgo medio' };
    return { text: 'text-rose-300', bg: 'bg-rose-500/15 border-rose-500/30', label: 'Riesgo técnico' };
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
    const mapEl = document.getElementById('map');
    if (!mapEl) {
        setTimeout(initMap, 100);
        return;
    }
    
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
    
    setTimeout(() => {
        if(map) {
            map.invalidateSize();
            if (hasCoords) map.setView(defaultPos, 15);
        }
    }, 450);
};

// --- AUTOCOMPLETADO Y BÚSQUEDA UBICACIÓN ---
watch(searchQuery, (newVal) => {
    if (!newVal || newVal.trim().length < 3) {
        suggestions.value = [];
        return;
    }
    if (newVal === newTour.ubicacion) return;

    if (searchTimeout) clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(async () => {
        isSearching.value = true;
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(newVal)}&limit=5`);
            const data = await res.json();
            suggestions.value = data || [];
        } catch (e) {
            console.error("Nominatim error:", e);
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
    mostrarNotificacion('Ubicación seleccionada en el mapa', 'exito');
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
                        formData.append(key, newTour[key] || '');
                    } else {
                        formData.append(key, newTour[key]);
                    }
                }
            }
        }
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
      class="fixed inset-0 z-[60] flex items-center justify-center p-2 sm:p-4 md:p-6 overflow-hidden bg-black/85 backdrop-blur-xl animate-fade-in"
      @click.self="emit('cerrar')">

      <!-- Modal Card -->
      <div class="relative flex max-h-[96dvh] w-full max-w-6xl flex-col overflow-hidden rounded-3xl border border-emerald-500/20 bg-[#08150d] shadow-[0_25px_80px_rgba(0,0,0,0.9),0_0_60px_rgba(16,185,129,0.08)] animate-fade-in-up sm:max-h-[94vh]">

        <!-- === HEADER PREMIUM === -->
        <div class="relative flex-shrink-0 overflow-hidden bg-gradient-to-r from-[#064e3b] via-[#053c2e] to-[#022c22] px-6 py-6 border-b border-emerald-400/20 sm:px-8 sm:py-7">
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-400/15 via-transparent to-transparent pointer-events-none"></div>

          <div class="relative z-10 flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-2.5">
                <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-black tracking-[0.2em] uppercase bg-emerald-400/15 border border-emerald-400/30 text-emerald-300 shadow-sm">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  {{ paquete ? 'Editando Tour' : 'Nuevo Tour' }}
                </span>
                <span v-if="paquete?.categoria_paquete_nombre" class="hidden sm:inline-flex px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase bg-white/10 text-white/70">
                  {{ paquete.categoria_paquete_nombre }}
                </span>
              </div>
              <h2 class="text-2xl font-black text-white sm:text-3xl tracking-tight drop-shadow-md">
                {{ paquete ? paquete.nombre : 'Configurar Experiencia' }}
              </h2>
              <p class="text-emerald-100/75 text-xs sm:text-sm mt-1.5 font-medium">
                {{ paquete ? 'Actualiza los datos técnicos y operativos de esta experiencia' : 'Diseña una aventura única para tus viajeros con altos estándares de calidad' }}
              </p>
            </div>

            <div class="flex items-center gap-2.5">
              <router-link to="/estandar-paquetes"
                class="hidden sm:inline-flex min-h-11 items-center gap-2 rounded-xl border border-emerald-400/30 bg-emerald-950/60 px-4 text-xs font-bold text-emerald-200 transition-all hover:bg-emerald-900/60 hover:text-white hover:border-emerald-400/60 focus:outline-none focus:ring-2 focus:ring-emerald-400/50 shadow-md">
                <svg class="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                Información del estándar
              </router-link>
              <button @click="emit('cerrar')" type="button" aria-label="Cerrar formulario"
                class="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-2xl bg-white/10 hover:bg-rose-500/20 hover:text-rose-300 hover:border-rose-500/40 text-white transition-all hover:rotate-90 duration-300 border border-white/10 shadow-sm">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- === LOADING OVERLAY === -->
        <div v-if="isLoading"
          class="absolute inset-0 bg-[#06120a]/90 backdrop-blur-md z-30 flex flex-col items-center justify-center">
          <div class="relative w-16 h-16 mb-5">
            <div class="absolute inset-0 border-4 border-emerald-500/20 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p class="text-white font-black text-xl tracking-tight">{{ paquete ? 'Actualizando experiencia...' : 'Guardando nuevo tour...' }}</p>
          <p class="text-emerald-400/70 text-xs mt-2 font-medium">Sincronizando información técnica en la plataforma</p>
        </div>

        <!-- === STEP BAR NAVEGACIÓN === -->
        <div class="sticky top-0 z-20 bg-[#06130b]/95 border-b border-emerald-500/15 backdrop-blur-md px-4 py-2.5 sm:px-8">
          <nav aria-label="Secciones del formulario" class="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5">
            <a href="#seccion-informacion" class="step-pill"><span>1</span>Información</a>
            <a href="#seccion-ubicacion" class="step-pill"><span>2</span>Ubicación</a>
            <a href="#seccion-actividades" class="step-pill"><span>3</span>Modalidades & Actividades</a>
            <a href="#seccion-seguridad" class="step-pill"><span>4</span>Dificultad & Seguridad</a>
            <a href="#seccion-itinerario" class="step-pill"><span>5</span>Itinerario</a>
            <a href="#seccion-incluye" class="step-pill"><span>6</span>Incluye</a>
            <a href="#seccion-galeria" class="step-pill"><span>7</span>Galería</a>
          </nav>
        </div>

        <!-- === CUERPO DEL FORMULARIO === -->
        <div class="form-scroll flex-1 overflow-x-hidden overflow-y-auto bg-[#07140c] p-4 sm:p-8 space-y-8">
          <form @submit.prevent="Enviar" class="tour-form space-y-8">

            <!-- Banner Alertas de Error -->
            <div v-if="totalErrores" data-form-error="true" role="alert" class="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-5 text-sm text-rose-100 shadow-lg shadow-rose-950/20 flex items-start gap-3">
              <svg class="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              <div>
                <p class="font-black">Hay {{ totalErrores }} campo(s) o secciones que requieren tu atención.</p>
                <p class="mt-1 text-rose-200/70 text-xs">Revisa los campos resaltados en rojo a continuación antes de guardar.</p>
              </div>
            </div>

            <!-- ─── SECCIÓN 1: INFORMACIÓN PRINCIPAL ─── -->
            <section id="seccion-informacion" class="form-card">
              <div class="flex items-center justify-between mb-7 border-b border-white/5 pb-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black flex items-center justify-center">1</div>
                  <div>
                    <h3 class="text-sm font-black text-white uppercase tracking-wider">Información principal</h3>
                    <p class="text-xs text-white/40">Datos esenciales del paquete para el catálogo</p>
                  </div>
                </div>

                <!-- Switch Estado Activo -->
                <label class="flex items-center gap-3 cursor-pointer bg-black/30 border border-white/10 px-4 py-2 rounded-xl hover:border-emerald-500/40 transition-all">
                  <span class="text-xs font-bold" :class="newTour.activo ? 'text-emerald-400' : 'text-white/40'">
                    {{ newTour.activo ? 'Visible para clientes' : 'Oculto / Borrador' }}
                  </span>
                  <div class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="newTour.activo" class="sr-only peer">
                    <div class="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-5 peer-checked:after:border-emerald-500 after:content-[''] after:absolute after:top-[3px] after:left-[3px] after:bg-white after:rounded-full after:h-[18px] after:w-[18px] after:transition-all peer-checked:bg-emerald-500"></div>
                  </div>
                </label>
              </div>

              <div class="space-y-6">
                <!-- Nombre -->
                <div>
                  <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                    Nombre del Tour <span class="text-emerald-400">*</span>
                  </label>
                  <input v-model="newTour.nombre" type="text" placeholder="Ej: Safari Fotográfico en el Corazón de la Amazonía"
                    :class="['form-input text-base font-bold', errores.nombre ? 'border-rose-500/60 ring-2 ring-rose-500/20' : '']">
                  <p v-if="errores.nombre" class="error-msg">{{ errores.nombre }}</p>
                </div>

                <!-- Categoría del Tour -->
                <div>
                  <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                    Categoría del Tour <span class="text-emerald-400">*</span>
                  </label>
                  <div class="relative">
                    <select v-model="newTour.categoria_paquete"
                      :class="['form-input appearance-none cursor-pointer pr-10 font-medium', errores.categoria_paquete ? 'border-rose-500/60' : '']">
                      <option value="" disabled selected class="bg-[#0b1c12]">Selecciona una categoría...</option>
                      <optgroup v-for="grupo in [...new Set(categorias.map(c => c.grupo))]" :key="grupo" :label="grupo" class="bg-[#0b1c12] text-emerald-300 font-bold">
                        <option v-for="cat in categorias.filter(c => c.grupo === grupo)" :key="cat.id" :value="cat.id" class="bg-[#0b1c12] text-white">
                          {{ cat.nombre }}
                        </option>
                      </optgroup>
                    </select>
                    <div class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-emerald-400">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                  </div>
                  <p v-if="errores.categoria_paquete" class="error-msg">{{ errores.categoria_paquete }}</p>
                </div>

                <!-- Descripción -->
                <div>
                  <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                    Descripción Completa <span class="text-emerald-400">*</span>
                  </label>
                  <textarea v-model="newTour.descripcion" rows="4"
                    placeholder="Describe los aspectos destacados de la experiencia, el valor agregado, paisajes, gastronomía o contacto con la selva..."
                    :class="['form-input resize-none leading-relaxed', errores.descripcion ? 'border-rose-500/60' : '']"></textarea>
                  <p v-if="errores.descripcion" class="error-msg">{{ errores.descripcion }}</p>
                </div>

                <!-- Grid: Precio + Duración + Capacidad -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                  <div>
                    <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                      Precio (COP) <span class="text-emerald-400">*</span>
                    </label>
                    <div class="relative">
                      <span class="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-400/60 font-black text-base">$</span>
                      <input v-model="newTour.precio" type="number" placeholder="250000"
                        :class="['form-input pl-8 font-black tabular-nums text-lg', errores.precio ? 'border-rose-500/60' : '']">
                    </div>
                    <p v-if="errores.precio" class="error-msg">{{ errores.precio }}</p>
                  </div>

                  <div>
                    <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                      Duración <span class="text-emerald-400">*</span>
                    </label>
                    <input v-model="newTour.duracion" type="text" placeholder="Ej: 8 horas o 2 días"
                      :class="['form-input font-bold text-center', errores.duracion ? 'border-rose-500/60' : '']">
                    <p v-if="errores.duracion" class="error-msg">{{ errores.duracion }}</p>
                  </div>

                  <div>
                    <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                      Capacidad Máxima <span class="text-emerald-400">*</span>
                    </label>
                    <input v-model="newTour.capacidad" type="number" placeholder="15"
                      :class="['form-input font-black text-center text-lg', errores.capacidad ? 'border-rose-500/60' : '']">
                    <p v-if="errores.capacidad" class="error-msg">{{ errores.capacidad }}</p>
                  </div>
                </div>

                <!-- Personalización Temporal (Tour Fijo vs Flexible) -->
                <div class="rounded-2xl border p-5 transition-all"
                  :class="tipoPaqueteAuto === 'fijo' ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-white/10 bg-black/20'">
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div>
                      <span class="text-xs font-black uppercase tracking-wider text-white">Modalidad de Salida</span>
                      <p class="text-xs text-white/40 mt-0.5">Si fijas una fecha específica, será de salida única. De lo contrario, queda flexible.</p>
                    </div>
                    <span :class="['px-3 py-1.5 rounded-xl text-xs font-black uppercase tracking-wider flex items-center gap-1.5',
                      tipoPaqueteAuto === 'fijo' ? 'bg-emerald-400 text-black shadow-md' : 'bg-white/10 text-white/60']">
                      <svg v-if="tipoPaqueteAuto === 'fijo'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                      <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                      {{ tipoPaqueteAuto === 'fijo' ? 'Tour con Fecha Fija' : 'Tour Flexible' }}
                    </span>
                  </div>

                  <div class="flex flex-col sm:flex-row items-center gap-3">
                    <input v-model="newTour.fecha_realizacion" type="date"
                      class="form-input text-sm font-bold flex-1">
                    <button v-if="newTour.fecha_realizacion" @click.prevent="newTour.fecha_realizacion = ''" type="button"
                      class="px-4 py-3 rounded-xl border border-rose-500/30 bg-rose-500/15 text-rose-300 hover:bg-rose-500 hover:text-white text-xs font-bold transition-all w-full sm:w-auto">
                      Hacer Flexible
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 2: UBICACIÓN Y MAPA ─── -->
            <section id="seccion-ubicacion" class="form-card">
              <div class="flex items-center gap-3 mb-6 border-b border-white/5 pb-4">
                <div class="w-9 h-9 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black flex items-center justify-center">2</div>
                <div>
                  <h3 class="text-sm font-black text-white uppercase tracking-wider">Punto de encuentro y mapa</h3>
                  <p class="text-xs text-white/40">Busca el lugar o haz clic directamente sobre el mapa interactivo</p>
                </div>
              </div>

              <!-- Input con autocompletado -->
              <div class="relative mb-4">
                <label class="block text-xs font-black text-white/70 uppercase tracking-wider mb-2">
                  Buscar Lugar o Dirección <span class="text-emerald-400">*</span>
                </label>
                <div class="relative">
                  <div class="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-400">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                  </div>
                  <input v-model="searchQuery" type="text"
                    placeholder="Escribe el nombre de la reserva, muelle, parque o municipio..."
                    class="form-input pl-12 pr-12 text-sm font-medium">
                  <div v-if="isSearching" class="absolute right-4 top-1/2 -translate-y-1/2">
                    <div class="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                </div>

                <!-- Dropdown Sugerencias -->
                <div v-if="suggestions.length > 0"
                  class="absolute z-30 left-0 right-0 mt-2 bg-[#09180e] border border-emerald-500/30 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-xl">
                  <ul class="divide-y divide-white/5">
                    <li v-for="s in suggestions" :key="s.place_id"
                        @click="selectSuggestion(s)"
                        class="px-5 py-3 hover:bg-emerald-500/15 cursor-pointer transition-colors flex items-start gap-3 text-left">
                      <svg class="w-4 h-4 text-emerald-400 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                      <div class="min-w-0">
                        <p class="text-sm font-bold text-white truncate">{{ s.display_name.split(',')[0] }}</p>
                        <p class="text-[11px] text-white/50 truncate">{{ s.display_name.split(',').slice(1).join(',') }}</p>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Contenedor del Mapa -->
              <div class="relative rounded-2xl overflow-hidden border border-emerald-500/20 bg-black/40 shadow-inner">
                <div id="map" ref="mapContainer" class="w-full h-80 z-10 brightness-95"></div>

                <!-- Badge Coordenadas -->
                <div class="pointer-events-none absolute bottom-4 left-4 right-4 z-20 flex justify-between items-center">
                  <div class="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-black/80 px-3.5 py-2 text-white shadow-xl backdrop-blur-md">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
                    <span class="text-[11px] font-mono font-bold text-emerald-300">
                      {{ newTour.latitud ? `${Number(newTour.latitud).toFixed(4)}, ${Number(newTour.longitud).toFixed(4)}` : 'Haz clic en el mapa para ubicar' }}
                    </span>
                  </div>
                </div>
              </div>
              <p v-if="errores.ubicacion" class="error-msg mt-3">{{ errores.ubicacion }}</p>
            </section>

            <!-- ─── SECCIÓN 3: MODALIDADES Y ACTIVIDADES ─── -->
            <section id="seccion-actividades" class="form-card">
              <div class="flex items-center justify-between mb-7 border-b border-white/5 pb-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black flex items-center justify-center">3</div>
                  <div>
                    <h3 class="text-sm font-black text-white uppercase tracking-wider">Modalidades y Actividades del Recorrido</h3>
                    <p class="text-xs text-white/40">Selecciona el tipo de turismo y las experiencias que incluye tu paquete</p>
                  </div>
                </div>
              </div>

              <!-- 3.1: BUSCADOR DE MODALIDADES DEL PAQUETE -->
              <div class="mb-8 rounded-2xl border border-white/10 bg-black/20 p-5 sm:p-6">
                <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                  <div>
                    <label for="buscar-modalidad" class="text-sm font-black text-white flex items-center gap-2">
                      <span>Modalidades del paquete</span>
                      <span class="text-emerald-400">*</span>
                    </label>
                    <p class="text-xs text-white/50 mt-0.5">Usa el buscador para filtrar modalidades según el enfoque de tu viaje</p>
                  </div>
                  <span class="px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-400/15 border border-emerald-400/30 text-emerald-300">
                    {{ newTour.modalidades_turismo.length }} seleccionada(s)
                  </span>
                </div>

                <!-- Buscador de Modalidades -->
                <div class="relative mb-5">
                  <div class="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
                  </div>
                  <input id="buscar-modalidad" v-model="modalidadBusqueda" type="search" autocomplete="off"
                    placeholder="Buscar modalidad: naturaleza, aventura, cultural, rural, bienestar, náutico..."
                    class="form-input pl-11 pr-10 text-sm">
                  <button v-if="modalidadBusqueda" type="button" @click="modalidadBusqueda = ''"
                    class="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded-md text-white/40 hover:text-white hover:bg-white/10 transition-colors">
                    ×
                  </button>
                </div>

                <!-- Grid de Modalidades -->
                <div v-if="modalidadesFiltradas.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <label v-for="modalidad in modalidadesFiltradas" :key="modalidad.value"
                    class="group relative flex flex-col justify-between p-4 rounded-xl border transition-all cursor-pointer text-left select-none"
                    :class="newTour.modalidades_turismo.includes(modalidad.value)
                      ? 'border-emerald-400 bg-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.18)]'
                      : 'border-white/10 bg-white/[0.025] hover:border-emerald-500/30 hover:bg-white/[0.05]'">
                    <input v-model="newTour.modalidades_turismo" type="checkbox" :value="modalidad.value" class="sr-only">

                    <div class="flex items-start justify-between gap-2 mb-2">
                      <span class="text-xs font-black" :class="newTour.modalidades_turismo.includes(modalidad.value) ? 'text-white' : 'text-white/80 group-hover:text-white'">
                        {{ modalidad.label }}
                      </span>
                      <div class="w-5 h-5 rounded-md border flex items-center justify-center flex-shrink-0 transition-all"
                        :class="newTour.modalidades_turismo.includes(modalidad.value) ? 'bg-emerald-400 border-emerald-400 text-black' : 'border-white/20 bg-black/20'">
                        <svg v-if="newTour.modalidades_turismo.includes(modalidad.value)" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><polyline points="20 6 9 17 4 12"></polyline></svg>
                      </div>
                    </div>

                    <p class="text-[11px] leading-4 text-white/45 group-hover:text-white/60 transition-colors line-clamp-2">
                      {{ modalidad.description }}
                    </p>
                  </label>
                </div>
                <div v-else class="rounded-xl border border-dashed border-white/15 p-6 text-center text-xs text-white/40">
                  No se encontraron modalidades con el término “{{ modalidadBusqueda }}”.
                </div>
                <p v-if="errores.modalidades_turismo" class="error-msg mt-3">{{ errores.modalidades_turismo }}</p>
              </div>

              <!-- 3.2: ACTIVIDADES DEL RECORRIDO -->
              <div id="tipos-actividad" class="rounded-2xl border border-white/10 bg-black/20 p-5 sm:p-6">
                <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                  <div>
                    <label for="buscar-actividad" class="text-sm font-black text-white flex items-center gap-2">
                      <span>Actividades del recorrido</span>
                      <span class="text-emerald-400">*</span>
                    </label>
                    <p class="text-xs text-white/50 mt-0.5">Selecciona todas las actividades que componen el paquete turístico</p>
                  </div>
                  <span class="px-3 py-1.5 rounded-full text-xs font-bold bg-sky-400/15 border border-sky-400/30 text-sky-300">
                    {{ newTour.actividades.length }} seleccionada(s)
                  </span>
                </div>

                <!-- Buscador de Actividades -->
                <div class="relative mb-5">
                  <div class="absolute left-4 top-1/2 -translate-y-1/2 text-sky-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
                  </div>
                  <input id="buscar-actividad" v-model="actividadBusqueda" type="search" autocomplete="off"
                    placeholder="Buscar actividad por nombre o norma técnica (ej. senderismo, rafting, NTS-AV)..."
                    class="form-input pl-11 pr-10 text-sm">
                  <button v-if="actividadBusqueda" type="button" @click="actividadBusqueda = ''"
                    class="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded-md text-white/40 hover:text-white hover:bg-white/10 transition-colors">
                    ×
                  </button>
                </div>

                <!-- Grid de Actividades -->
                <div v-if="actividadesFiltradas.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  <label v-for="actividad in actividadesFiltradas" :key="actividad.id"
                    class="group relative flex items-center justify-between p-3.5 rounded-xl border transition-all cursor-pointer text-left select-none"
                    :class="newTour.actividades.includes(actividad.id)
                      ? 'border-sky-400/60 bg-sky-500/15 shadow-[0_0_20px_rgba(56,189,248,0.15)]'
                      : 'border-white/10 bg-white/[0.025] hover:border-sky-500/30 hover:bg-white/[0.05]'">
                    <input type="checkbox" :value="actividad.id" v-model="newTour.actividades" class="sr-only">

                    <div class="flex items-center gap-3 min-w-0 pr-2">
                      <div class="w-5 h-5 rounded-md border flex items-center justify-center flex-shrink-0 transition-all"
                        :class="newTour.actividades.includes(actividad.id) ? 'bg-sky-400 border-sky-400 text-black' : 'border-white/20 bg-black/20'">
                        <svg v-if="newTour.actividades.includes(actividad.id)" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><polyline points="20 6 9 17 4 12"></polyline></svg>
                      </div>
                      <div class="min-w-0">
                        <span class="text-xs font-bold block truncate" :class="newTour.actividades.includes(actividad.id) ? 'text-white' : 'text-white/80 group-hover:text-white'">
                          {{ actividad.nombre }}
                        </span>
                        <span class="text-[10px] text-white/40 block">
                          Riesgo: {{ actividad.nivel_riesgo }}/10
                        </span>
                      </div>
                    </div>

                    <span v-if="actividad.norma_tecnica" class="rounded-md bg-sky-400/15 px-2 py-0.5 text-[9px] font-black text-sky-200 border border-sky-400/30 flex-shrink-0">
                      {{ actividad.norma_tecnica }}
                    </span>
                  </label>
                </div>
                <div v-else class="rounded-xl border border-dashed border-white/15 p-6 text-center text-xs text-white/40">
                  No se encontraron actividades con el filtro “{{ actividadBusqueda }}”.
                </div>
                <p v-if="errores.actividades" class="error-msg mt-3">{{ errores.actividades }}</p>
              </div>
            </section>

            <!-- ─── SECCIÓN 4: DIFICULTAD Y SEGURIDAD (LA PERSPECTIVA SOLICITADA) ─── -->
            <section id="seccion-seguridad" class="form-card">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-7 border-b border-white/5 pb-5">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-400 text-xs font-black flex items-center justify-center">4</div>
                  <div>
                    <h3 class="text-sm font-black text-white uppercase tracking-wider">Dificultad, requisitos y seguridad</h3>
                    <p class="text-xs text-white/40">Define la exigencia técnica para cada actividad y la información de protección al turista</p>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <span class="px-3 py-1 rounded-full text-[11px] font-bold bg-white/5 border border-white/10 text-white/70">
                    {{ actividadesSeleccionadas.length }} actividad(es)
                  </span>
                  <span class="px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                    {{ camposOperacionCompletos }}/4 preguntas completas
                  </span>
                </div>
              </div>

              <!-- 4.1: DIFICULTAD POR ACTIVIDAD (ITEMS CLICKEABLES DESDE LA DB) -->
              <div class="mb-10">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="text-sm font-black text-white">Dificultad por actividad seleccionada</h4>
                    <p class="text-xs text-white/50">Selecciona el nivel haciendo clic en la opción técnica que mejor describa la experiencia</p>
                  </div>
                  <router-link to="/estandar-paquetes" class="text-xs font-bold text-sky-300 hover:text-sky-200 underline decoration-sky-400/40 underline-offset-4 hidden sm:block">
                    Ver norma del estándar
                  </router-link>
                </div>

                <!-- Estado sin actividades -->
                <div v-if="!actividadesSeleccionadas.length"
                  class="rounded-2xl border border-dashed border-white/15 bg-black/20 p-8 text-center flex flex-col items-center justify-center">
                  <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 mb-3">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                  </div>
                  <p class="text-sm font-bold text-white/80">Aún no has seleccionado actividades para el tour</p>
                  <p class="text-xs text-white/40 mt-1 max-w-md">Regresa al paso 3 para marcar las actividades que formarán parte de tu paquete y clasificar su dificultad.</p>
                  <button type="button" @click="irASeleccionActividades"
                    class="mt-4 px-4 py-2 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500 hover:text-black font-bold text-xs transition-all">
                    Seleccionar actividades ahora
                  </button>
                </div>

                <!-- Tarjetas de Actividades con ITEMS CLICKEABLES -->
                <div v-else class="space-y-6">
                  <article v-for="actividad in actividadesSeleccionadas" :key="`ficha-${actividad.id}`"
                    class="rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-5 sm:p-6 transition-all hover:border-emerald-500/30">

                    <!-- Header de la Actividad -->
                    <div class="flex flex-wrap items-start justify-between gap-3 mb-5 border-b border-white/5 pb-4">
                      <div>
                        <div class="flex items-center gap-2.5">
                          <h5 class="font-black text-white text-base tracking-tight">{{ actividad.nombre }}</h5>
                          <span v-if="actividad.norma_tecnica" class="rounded-md bg-sky-400/15 border border-sky-400/30 px-2.5 py-0.5 text-[10px] font-black text-sky-200">
                            {{ actividad.norma_tecnica }}
                          </span>
                        </div>
                        <p class="text-xs text-white/50 mt-1 flex items-center gap-2">
                          <span class="inline-flex items-center gap-1 font-semibold" :class="colorRiesgo(actividad.nivel_riesgo).text">
                            <span class="w-2 h-2 rounded-full" :class="colorRiesgo(actividad.nivel_riesgo).text.replace('text-', 'bg-')"></span>
                            Riesgo interno {{ actividad.nivel_riesgo }}/10 ({{ colorRiesgo(actividad.nivel_riesgo).label }})
                          </span>
                          <span class="text-white/20">·</span>
                          <span class="italic text-white/40">{{ actividad.sistema_dificultad || 'Escala operativa interna' }}</span>
                        </p>
                      </div>

                      <div class="flex items-center gap-2">
                        <span v-if="actividad.es_turismo_aventura" class="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-amber-400/15 border border-amber-400/30 text-amber-300">
                          Turismo de aventura
                        </span>
                        <span v-else class="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-emerald-400/15 border border-emerald-400/30 text-emerald-300">
                          Ecoturismo / Cultura
                        </span>
                      </div>
                    </div>

                    <!-- BOTONES/ITEMS CLICKEABLES DE DIFICULTAD (DESDE LA DB) -->
                    <div class="mb-5">
                      <div class="flex items-center justify-between mb-3">
                        <span class="text-xs font-black text-white/80 uppercase tracking-wider flex items-center gap-2">
                          <span>Nivel de dificultad</span>
                          <span class="text-emerald-400">*</span>
                        </span>
                        <span class="text-[11px] text-white/40">Haz clic para seleccionar</span>
                      </div>

                      <div v-if="obtenerOpcionesDificultad(actividad).length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        <button v-for="opcion in obtenerOpcionesDificultad(actividad)" :key="opcion.value"
                          type="button"
                          @click="fichaActividad(actividad).nivel = opcion.value"
                          class="group relative flex flex-col justify-between p-3.5 rounded-xl border text-left transition-all duration-200 cursor-pointer select-none"
                          :class="fichaActividad(actividad).nivel === opcion.value
                            ? colorDificultad(opcion.value).borderActive
                            : 'border-white/10 bg-white/[0.025] hover:border-emerald-400/40 hover:bg-white/[0.05]'">

                          <!-- Encabezado de la opción con radio visual y etiqueta -->
                          <div class="flex items-start justify-between gap-2 mb-1.5">
                            <div class="flex items-center gap-2.5">
                              <span class="w-2.5 h-2.5 rounded-full" :class="colorDificultad(opcion.value).dot"></span>
                              <span class="text-xs font-black" :class="fichaActividad(actividad).nivel === opcion.value ? 'text-white' : 'text-white/80 group-hover:text-white'">
                                {{ opcion.label }}
                              </span>
                            </div>

                            <!-- Indicador de Selección -->
                            <div class="w-5 h-5 rounded-full border flex items-center justify-center flex-shrink-0 transition-all"
                              :class="fichaActividad(actividad).nivel === opcion.value
                                ? 'bg-white text-black border-white shadow-sm'
                                : 'border-white/20 bg-black/20'">
                              <svg v-if="fichaActividad(actividad).nivel === opcion.value" class="w-3 h-3 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            </div>
                          </div>

                          <!-- Descripción de la opción -->
                          <p v-if="opcion.description" class="text-[11px] leading-4 text-white/50 group-hover:text-white/70 transition-colors">
                            {{ opcion.description }}
                          </p>
                        </button>
                      </div>
                      <div v-else class="rounded-xl border border-dashed border-amber-400/30 bg-amber-400/5 p-4 text-xs text-amber-100/70">
                        Esta actividad aún no tiene opciones de dificultad cargadas. Ejecuta
                        <code class="font-mono text-amber-200">python manage.py seed_dificultades_actividades</code>
                        y vuelve a cargar el formulario.
                      </div>
                    </div>

                    <!-- Detalles del terreno / Qué encontrará el viajero -->
                    <div>
                      <label :for="`desc-act-${actividad.id}`" class="block text-xs font-bold text-white/70 mb-2">
                        ¿Qué encontrará el viajero en esta actividad? (Opcional)
                      </label>
                      <textarea :id="`desc-act-${actividad.id}`"
                        v-model="fichaActividad(actividad).descripcion"
                        rows="2"
                        placeholder="Ej.: altura de cascada, tipo de sendero, pendiente, caudal o recomendaciones de calzado..."
                        class="form-input text-xs resize-none leading-relaxed"></textarea>
                    </div>
                  </article>
                  <p v-if="errores.clasificacion_actividades" class="error-msg">{{ errores.clasificacion_actividades }}</p>
                </div>
              </div>

              <!-- 4.2: INFORMACIÓN OPERATIVA DEL TOUR (PREGUNTAS EN TARJETAS CON ALTO CONTRASTE) -->
              <div class="border-t border-white/10 pt-7">
                <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
                  <div>
                    <h4 class="text-sm font-black text-white">Información operativa del tour</h4>
                    <p class="text-xs text-white/50">Responde cada pregunta con información concreta que la agencia y los guías puedan garantizar</p>
                  </div>
                  <span v-if="requiereCertificacion" class="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-amber-400/15 border border-amber-400/30 text-amber-300">
                    Campos requeridos por turismo de aventura
                  </span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <!-- Tarjeta 1: ¿Quién puede participar? -->
                  <div class="rounded-2xl border p-5 transition-all bg-gradient-to-b from-white/[0.04] to-black/30"
                    :class="errores.requisitos_participantes ? 'border-rose-500/50' : 'border-emerald-500/20 hover:border-emerald-500/40'">
                    <div class="flex items-start gap-3.5 mb-3">
                      <div class="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between gap-2">
                          <label for="requisitos-participantes" class="text-sm font-black text-white">¿Quién puede participar?</label>
                          <span class="text-[10px] font-bold px-2 py-0.5 rounded" :class="requiereCertificacion ? 'bg-amber-400/20 text-amber-300' : 'bg-white/10 text-white/50'">
                            {{ requiereCertificacion ? 'Obligatorio' : 'Opcional' }}
                          </span>
                        </div>
                        <p class="text-xs text-white/45 mt-0.5">Edad, condición física, restricciones médicas o experiencia previa.</p>
                      </div>
                    </div>
                    <textarea id="requisitos-participantes" v-model="newTour.requisitos_participantes" rows="3"
                      placeholder="Ej.: Mayores de 14 años, saber nadar, no apto para personas con problemas cardíacos o cirugías recientes."
                      class="form-input text-xs resize-none"></textarea>
                    <p v-if="errores.requisitos_participantes" class="error-msg mt-1.5">{{ errores.requisitos_participantes }}</p>
                  </div>

                  <!-- Tarjeta 2: ¿Cuándo puede realizarse? -->
                  <div class="rounded-2xl border p-5 transition-all bg-gradient-to-b from-white/[0.04] to-black/30"
                    :class="errores.condiciones_operacion ? 'border-rose-500/50' : 'border-sky-500/20 hover:border-sky-500/40'">
                    <div class="flex items-start gap-3.5 mb-3">
                      <div class="w-10 h-10 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-400 flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between gap-2">
                          <label for="condiciones-operacion" class="text-sm font-black text-white">¿Cuándo puede realizarse?</label>
                          <span class="text-[10px] font-bold px-2 py-0.5 rounded" :class="requiereCertificacion ? 'bg-amber-400/20 text-amber-300' : 'bg-white/10 text-white/50'">
                            {{ requiereCertificacion ? 'Obligatorio' : 'Opcional' }}
                          </span>
                        </div>
                        <p class="text-xs text-white/45 mt-0.5">Horarios recomendados, temporada de lluvias, caudal del río o motivos de suspensión.</p>
                      </div>
                    </div>
                    <textarea id="condiciones-operacion" v-model="newTour.condiciones_operacion" rows="3"
                      placeholder="Ej.: Salidas de 6:00 a.m. a 2:00 p.m. Se suspende en caso de tormentas eléctricas o creciente del río."
                      class="form-input text-xs resize-none"></textarea>
                    <p v-if="errores.condiciones_operacion" class="error-msg mt-1.5">{{ errores.condiciones_operacion }}</p>
                  </div>

                  <!-- Tarjeta 3: ¿Cómo se protege al viajero? -->
                  <div class="rounded-2xl border p-5 transition-all bg-gradient-to-b from-white/[0.04] to-black/30"
                    :class="errores.medidas_seguridad ? 'border-rose-500/50' : 'border-amber-500/20 hover:border-amber-500/40'">
                    <div class="flex items-start gap-3.5 mb-3">
                      <div class="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-400 flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between gap-2">
                          <label for="medidas-seguridad" class="text-sm font-black text-white">¿Cómo se protege al viajero?</label>
                          <span class="text-[10px] font-bold px-2 py-0.5 rounded" :class="requiereCertificacion ? 'bg-amber-400/20 text-amber-300' : 'bg-white/10 text-white/50'">
                            {{ requiereCertificacion ? 'Obligatorio' : 'Opcional' }}
                          </span>
                        </div>
                        <p class="text-xs text-white/45 mt-0.5">Equipamiento certificado, botiquín de primeros auxilios y plan de contingencia.</p>
                      </div>
                    </div>
                    <textarea id="medidas-seguridad" v-model="newTour.medidas_seguridad" rows="3"
                      placeholder="Ej.: Chaleco salvavidas certificado, cascos, guía certificado con primeros auxilios y radio satelital."
                      class="form-input text-xs resize-none"></textarea>
                    <p v-if="errores.medidas_seguridad" class="error-msg mt-1.5">{{ errores.medidas_seguridad }}</p>
                  </div>

                  <!-- Tarjeta 4: ¿Cómo se cuida el destino? -->
                  <div class="rounded-2xl border border-teal-500/20 bg-gradient-to-b from-white/[0.04] to-black/30 p-5 hover:border-teal-500/40 transition-all">
                    <div class="flex items-start gap-3.5 mb-3">
                      <div class="w-10 h-10 rounded-xl bg-teal-500/15 border border-teal-500/30 text-teal-400 flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582"/></svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between gap-2">
                          <label for="informacion-sostenibilidad" class="text-sm font-black text-white">¿Cómo se cuida el destino?</label>
                          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-white/10 text-white/50">Opcional</span>
                        </div>
                        <p class="text-xs text-white/45 mt-0.5">Políticas de no dejar rastro, respeto a la fauna, apoyo a comunidades locales.</p>
                      </div>
                    </div>
                    <textarea id="informacion-sostenibilidad" v-model="newTour.informacion_sostenibilidad" rows="3"
                      placeholder="Ej.: Cero plásticos de un solo uso, senderos delimitados para no erosionar y compra de refrigerios a mujeres de la comunidad."
                      class="form-input text-xs resize-none"></textarea>
                  </div>
                </div>
              </div>

              <!-- Certificación de Aventura (si aplica) -->
              <div v-if="requiereCertificacion" class="mt-6 rounded-2xl border border-amber-400/30 bg-amber-400/5 p-5 sm:p-6">
                <div class="flex flex-wrap items-start justify-between gap-4 mb-4">
                  <div>
                    <span class="text-xs font-black uppercase tracking-wider text-amber-300">Certificación técnica de aventura</span>
                    <p class="text-xs text-amber-100/60 mt-1 max-w-xl">Para publicar el tour como activo en el catálogo, ingresa los datos del organismo evaluador o acreditación sectorial.</p>
                  </div>
                  <select v-model="newTour.certificacion_aventura.estado" class="form-input text-xs font-bold max-w-xs">
                    <option value="pendiente" class="bg-[#121c15]">En trámite / Pendiente</option>
                    <option value="vigente" class="bg-[#121c15]">Vigente</option>
                    <option value="vencida" class="bg-[#121c15]">Vencida</option>
                  </select>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-[10px] font-bold uppercase tracking-wider text-white/60 mb-1.5">Organismo evaluador</label>
                    <input v-model="newTour.certificacion_aventura.organismo" type="text" placeholder="Ej.: ONAC / Icontec" class="form-input text-xs">
                  </div>
                  <div>
                    <label class="block text-[10px] font-bold uppercase tracking-wider text-white/60 mb-1.5">Código o Certificado</label>
                    <input v-model="newTour.certificacion_aventura.codigo" type="text" placeholder="Ej.: NTS-AV-2026-004" class="form-input text-xs">
                  </div>
                  <div>
                    <label class="block text-[10px] font-bold uppercase tracking-wider text-white/60 mb-1.5">Fecha de vigencia</label>
                    <input v-model="newTour.certificacion_aventura.vigente_hasta" type="date" class="form-input text-xs">
                  </div>
                </div>
                <p v-if="errores.certificacion_aventura" class="error-msg mt-3">{{ errores.certificacion_aventura }}</p>
              </div>
            </section>

            <!-- ─── SECCIÓN 5: ITINERARIO ─── -->
            <section id="seccion-itinerario" class="form-card">
              <div class="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black flex items-center justify-center">5</div>
                  <div>
                    <h3 class="text-sm font-black text-white uppercase tracking-wider">Itinerario del viaje</h3>
                    <p class="text-xs text-white/40">Programa cronológico de actividades y paradas del tour</p>
                  </div>
                </div>

                <button @click.prevent="addItineraryItem" type="button"
                  class="flex items-center gap-2 text-xs text-emerald-300 font-bold bg-emerald-500/15 hover:bg-emerald-500/25 px-4 py-2 rounded-xl transition-all border border-emerald-500/30">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Agregar parada
                </button>
              </div>

              <div class="space-y-3">
                <div v-for="(item, index) in newTour.itinerario" :key="'iti-'+index"
                  class="group flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 p-3 hover:border-emerald-500/30 transition-all">
                  <span class="w-7 h-7 rounded-lg bg-white/5 text-white/40 text-xs font-bold flex items-center justify-center flex-shrink-0">
                    {{ index + 1 }}
                  </span>
                  <input v-model="item.time" type="time"
                    class="form-input w-28 text-xs font-bold text-center">
                  <input v-model="item.activity" type="text" :placeholder="`Actividad de la parada ${index + 1}...`"
                    class="form-input flex-1 text-xs font-medium">
                  <button v-if="newTour.itinerario.length > 1" @click.prevent="removeItineraryItem(index)" type="button"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-white/30 hover:text-rose-400 hover:bg-rose-500/10 transition-all">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 6: QUÉ INCLUYE ─── -->
            <section id="seccion-incluye" class="form-card">
              <div class="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black flex items-center justify-center">6</div>
                  <div>
                    <h3 class="text-sm font-black text-white uppercase tracking-wider">Qué incluye el paquete</h3>
                    <p class="text-xs text-white/40">Servicios, alimentación, traslados o pólizas contempladas</p>
                  </div>
                </div>

                <button @click.prevent="addIncludedItem" type="button"
                  class="flex items-center gap-2 text-xs text-emerald-300 font-bold bg-emerald-500/15 hover:bg-emerald-500/25 px-4 py-2 rounded-xl transition-all border border-emerald-500/30">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Agregar item
                </button>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div v-for="(inc, index) in newTour.incluido" :key="'inc-'+index"
                  class="flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 p-3 hover:border-emerald-500/30 transition-all">
                  <div class="w-6 h-6 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <input v-model="inc.item" type="text" :placeholder="`Ej: Transporte fluvial ida y vuelta...`"
                    class="form-input flex-1 text-xs border-0 bg-transparent px-0 py-0 focus:ring-0">
                  <button v-if="newTour.incluido.length > 1" @click.prevent="removeIncludedItem(index)" type="button"
                    class="w-7 h-7 rounded-md flex items-center justify-center text-white/30 hover:text-rose-400 hover:bg-rose-500/10 transition-all">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 7: GALERÍA ─── -->
            <section id="seccion-galeria" class="form-card">
              <div class="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black flex items-center justify-center">7</div>
                  <div>
                    <h3 class="text-sm font-black text-white uppercase tracking-wider">Galería fotográfica</h3>
                    <p class="text-xs text-white/40">Imágenes que ilustran los paisajes y vivencias de la aventura</p>
                  </div>
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-bold bg-white/5 border border-white/10 text-white/60">
                  {{ totalImageCount }} foto(s)
                </span>
              </div>

              <!-- Imágenes existentes -->
              <div v-if="imagenesExistentes.length > 0" class="mb-6">
                <span class="text-xs font-bold uppercase tracking-wider text-white/60 block mb-3">Imágenes actuales del tour</span>
                <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                  <div v-for="(img, index) in imagenesExistentes" :key="'existing-'+img.id"
                    class="relative group rounded-xl overflow-hidden aspect-square bg-black/40 border border-white/10">
                    <img :src="img.url" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                      <button @click.prevent="removeExistingImage(img.id, index)" type="button"
                        class="p-2 rounded-xl bg-rose-500 text-white hover:bg-rose-600 transition-all shadow-lg">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      </button>
                    </div>
                    <span v-if="img.es_portada" class="absolute top-2 left-2 bg-emerald-400 text-black text-[9px] font-black px-2 py-0.5 rounded shadow uppercase">Portada</span>
                  </div>
                </div>
              </div>

              <!-- Dropzone -->
              <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                @click="$refs.fileInput.click()"
                class="flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-8 hover:bg-white/[0.02] transition-all cursor-pointer"
                :class="isDragging ? 'border-emerald-400 bg-emerald-500/10' : 'border-white/15 hover:border-emerald-500/40'">
                <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect">
                <div class="w-12 h-12 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-3">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                </div>
                <p class="text-xs font-bold text-white uppercase tracking-wider">Subir nuevas imágenes</p>
                <p class="text-[11px] text-white/40 mt-1">Arrastra tus fotos o haz clic para seleccionarlas de tu dispositivo</p>
              </div>

              <!-- Preview Nuevas -->
              <div v-if="newTour.imagen.length > 0" class="mt-4 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                <div v-for="(img, idx) in newTour.imagen" :key="'new-'+idx"
                  class="relative aspect-square rounded-xl overflow-hidden border border-emerald-400/50 group">
                  <img :src="img.url" class="w-full h-full object-cover">
                  <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button @click.prevent="removeImage(idx)" type="button"
                      class="p-2 rounded-xl bg-rose-500 text-white hover:bg-rose-600 transition-all">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                  </div>
                  <span class="absolute top-2 left-2 bg-emerald-400 text-black text-[9px] font-black px-1.5 py-0.5 rounded shadow uppercase">Nueva</span>
                </div>
              </div>
            </section>
          </form>
        </div>

        <!-- === FOOTER ACCIONES === -->
        <div class="flex-shrink-0 flex items-center justify-end gap-3 border-t border-emerald-500/15 bg-[#06130b]/95 px-6 py-4 sm:px-8">
          <button @click="emit('cerrar')" type="button" :disabled="isLoading"
            class="px-5 py-3 rounded-xl text-xs font-black uppercase tracking-wider text-white/60 hover:text-white hover:bg-white/5 transition-all">
            Descartar Cambios
          </button>
          <button @click="Enviar" type="button" :disabled="isLoading"
            class="group flex items-center gap-2.5 px-7 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black text-xs font-black uppercase tracking-wider shadow-lg shadow-emerald-950/40 transition-all hover:shadow-emerald-500/20 disabled:opacity-50">
            <svg v-if="isLoading" class="animate-spin h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-else>{{ paquete ? 'Guardar Cambios' : 'Confirmar Registro' }}</span>
            <svg v-if="!isLoading" class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.25s ease-out forwards;
}
.animate-fade-in-up {
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(14px) scale(0.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.form-scroll::-webkit-scrollbar {
  width: 6px;
}
.form-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.form-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(52, 211, 153, 0.25);
  border-radius: 9999px;
}
.form-scroll::-webkit-scrollbar-thumb:hover {
  background-color: rgba(52, 211, 153, 0.45);
}

.step-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
.step-pill:hover {
  background: rgba(16, 185, 129, 0.12);
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.25);
}
.step-pill span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 0.4rem;
  background: rgba(255, 255, 255, 0.08);
  font-size: 0.65rem;
  font-weight: 900;
  color: #34d399;
}

.form-card {
  border-radius: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.035) 0%, rgba(255, 255, 255, 0.01) 100%);
  padding: clamp(1.2rem, 2.5vw, 2rem);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  scroll-margin-top: 4.5rem;
}

.form-input {
  width: 100%;
  border-radius: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background-color: rgba(0, 0, 0, 0.35);
  color: #ffffff;
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}
.form-input:focus {
  outline: none;
  border-color: #34d399;
  background-color: rgba(0, 0, 0, 0.55);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}
.form-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.error-msg {
  color: #f87171;
  font-size: 0.75rem;
  font-weight: 700;
  margin-top: 0.35rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
</style>
