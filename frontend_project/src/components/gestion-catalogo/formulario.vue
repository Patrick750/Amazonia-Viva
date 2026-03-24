<script setup>
import { reactive, watch, ref, computed } from 'vue';
import { GuardarRegistro } from '@/composables/gestion-tours/create-pack';
import { useNotificacion } from '@/composables/useNotificacion';

const props = defineProps(['abrir', 'actividades', 'paquete']);
const emit = defineEmits(['cerrar', 'guardadoExitoso']);

// --- COMPOSABLE ---
const { guardarDatos } = GuardarRegistro();

// --- ESTADOS ---
const isLoading = ref(false);
const errores = reactive({});
const isDragging = ref(false);
const fileInput = ref(null);
const locationInput = ref(null);
const mapContainer = ref(null);
let map = null;
let marker = null;
let autocomplete = null;

// --- NOTIFICACIÓN ---
const { mostrarNotificacion } = useNotificacion();

// --- ESTADO DEL FORMULARIO ---
const newTour = reactive({
    id: null,
    activo: true,
    nombre: '',
    descripcion: '',
    precio: '',
    duracion: '',
    ubicacion: 'default',
    latitud: null,
    longitud: null,
    capacidad: '',
    actividades: [],
    itinerario: [{ time: '', activity: '' }],
    incluido: [{ item: '' }],
    imagen: []   // nuevas imágenes locales { file, url, name }
});

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
        if (!newTour.itinerario || newTour.itinerario.length === 0) newTour.itinerario = [{ time: '', activity: '' }];
        if (!newTour.incluido || newTour.incluido.length === 0) newTour.incluido = [{ item: '' }];
        newTour.imagen = [];
        // Cargar imágenes existentes
        imagenesExistentes.value = paqueteAEditar.imagen_paquete
            ? paqueteAEditar.imagen_paquete.map(i => ({ ...i }))
            : [];
    } else {
        Object.assign(newTour, JSON.parse(JSON.stringify(inicial)));
        newTour.itinerario = [{ time: '', activity: '' }];
        newTour.incluido = [{ item: '' }];
        newTour.imagen = [];
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
    imagenesExistentes.value = [];
    imagenesAEliminar.value = [];
    if (locationInput.value) locationInput.value.value = '';
    if (fileInput.value) fileInput.value.value = '';
    if (marker) marker.setVisible(false);
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
    if (newTour.actividades.length === 0) { errores.actividades = "Selecciona al menos una actividad."; valido = false; }
    return valido;
};

// --- ITINERARIO E INCLUIDO ---
const addItineraryItem = () => newTour.itinerario.push({ time: '', activity: '' });
const removeItineraryItem = (index) => { if (newTour.itinerario.length > 1) newTour.itinerario.splice(index, 1); };
const addIncludedItem = () => newTour.incluido.push({ item: '' });
const removeIncludedItem = (index) => { if (newTour.incluido.length > 1) newTour.incluido.splice(index, 1); };

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

// --- GOOGLE MAPS ---
const initMap = () => {
    if (typeof google === 'undefined' || !mapContainer.value || !locationInput.value) return;
    const defaultPos = (newTour.latitud && newTour.longitud)
        ? { lat: Number(newTour.latitud), lng: Number(newTour.longitud) }
        : { lat: 4.6097, lng: -74.0817 };
    map = new google.maps.Map(mapContainer.value, {
        center: defaultPos, zoom: newTour.latitud ? 15 : 12,
        mapTypeControl: false, streetViewControl: false,
    });
    marker = new google.maps.Marker({ map, position: defaultPos, visible: !!newTour.latitud });
    autocomplete = new google.maps.places.Autocomplete(locationInput.value, {
        fields: ["geometry", "name", "formatted_address"],
    });
    autocomplete.bindTo("bounds", map);
    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry?.location) return;
        if (place.geometry.viewport) { map.fitBounds(place.geometry.viewport); }
        else { map.setCenter(place.geometry.location); map.setZoom(17); }
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
        newTour.ubicacion = place.formatted_address || place.name;
        newTour.latitud = place.geometry.location.lat();
        newTour.longitud = place.geometry.location.lng();
    });
};

watch(() => props.abrir, (estaAbierto) => {
    if (estaAbierto) {
        if (typeof google === 'undefined') {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyDaDxKnE-8fzSc58TS-sMCm3UiP9cY577U&libraries=places&callback=iniciarMapaGlobal`;
            script.async = true; script.defer = true;
            document.head.appendChild(script);
            window.iniciarMapaGlobal = () => setTimeout(() => initMap(), 100);
        } else {
            setTimeout(() => initMap(), 100);
        }
    }
});

// --- ENVÍO ---
const Enviar = async () => {
    if (locationInput.value?.value) newTour.ubicacion = locationInput.value.value;
    if (!validarFormulario()) return;
    isLoading.value = true;
    try {
        const formData = new FormData();
        for (const key in newTour) {
            if (!['itinerario', 'incluido', 'actividades', 'archivos_subidos', 'imagen', 'imagen_paquete'].includes(key)) {
                if (newTour[key] !== null && newTour[key] !== undefined) {
                    formData.append(key, newTour[key]);
                }
            }
        }
        const itFiltrado = newTour.itinerario.filter(i => i.time.trim() || i.activity.trim());
        formData.append('itinerario', JSON.stringify(itFiltrado));
        const incFiltrado = newTour.incluido.filter(i => i.item.trim());
        formData.append('incluido', JSON.stringify(incFiltrado));
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
        mostrarNotificacion('Hubo un error al guardar el tour. Intenta de nuevo.', 'error');
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
  <Teleport to="body">
    <!-- Overlay + Modal -->
    <div v-if="abrir"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4"
      @click.self="emit('cerrar')">

      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>

      <!-- Modal Card -->
      <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden animate-fade-in-up">

        <!-- === HEADER GRADIENTE === -->
        <div class="bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-600 px-8 py-6 flex-shrink-0">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest uppercase text-emerald-200">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                  {{ paquete ? 'Editando Tour' : 'Nuevo Tour' }}
                </span>
              </div>
              <h2 class="text-2xl font-bold text-white leading-tight">
                {{ paquete ? paquete.nombre : 'Crear Experiencia' }}
              </h2>
              <p class="text-emerald-100 text-sm mt-1">
                {{ paquete ? 'Actualiza los datos de este tour' : 'Diseña una experiencia única para tus viajeros' }}
              </p>
            </div>
            <button @click="emit('cerrar')"
              class="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 text-white transition-all hover:rotate-90 duration-200">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- === LOADING OVERLAY === -->
        <div v-if="isLoading"
          class="absolute inset-0 bg-white/85 backdrop-blur-sm z-20 flex flex-col items-center justify-center rounded-3xl">
          <div class="w-16 h-16 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin mb-4"></div>
          <p class="text-emerald-800 font-bold text-lg">{{ paquete ? 'Actualizando...' : 'Creando tour...' }}</p>
          <p class="text-slate-400 text-sm mt-1">Esto tomará solo un momento</p>
        </div>

        <!-- === CUERPO DEL FORMULARIO === -->
        <div class="overflow-y-auto flex-1 form-scroll">
          <form @submit.prevent="Enviar" class="p-8 space-y-10">

            <!-- ─── SECCIÓN 1: INFO BÁSICA ─── -->
            <section>
              <div class="flex items-center gap-3 mb-6">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">1</div>
                <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Información Básica</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
              </div>

              <!-- Estado Activo -->
              <div class="mb-5 flex items-center justify-between bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-4">
                <div>
                  <h4 class="text-sm font-bold text-slate-700">Estado del Tour</h4>
                  <p class="text-xs text-slate-500 mt-0.5">Define si el tour est&aacute; visible y activo para los clientes.</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="newTour.activo" class="sr-only peer">
                  <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                  <span class="ml-3 text-sm font-bold flex-shrink-0 w-16" :class="newTour.activo ? 'text-emerald-600' : 'text-slate-400'">
                    {{ newTour.activo ? 'Activo' : 'Inactivo' }}
                  </span>
                </label>
              </div>

              <!-- Nombre -->
              <div class="mb-5">
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Nombre del Tour <span class="text-emerald-500">*</span></label>
                <input v-model="newTour.nombre" type="text" placeholder="Ej: Aventura en el Corazón del Amazonas"
                  :class="['w-full bg-slate-50 border-2 rounded-2xl px-5 py-3 text-slate-800 font-medium focus:outline-none focus:bg-white transition-all placeholder:text-slate-300 placeholder:font-normal',
                  errores.nombre ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-emerald-500']">
                <p v-if="errores.nombre" class="text-xs text-red-500 mt-1.5 ml-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                  {{ errores.nombre }}
                </p>
              </div>

              <!-- Descripción -->
              <div class="mb-5">
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Descripción <span class="text-emerald-500">*</span></label>
                <textarea v-model="newTour.descripcion" rows="3"
                  placeholder="Describe qué hace única esta experiencia..."
                  :class="['w-full bg-slate-50 border-2 rounded-2xl px-5 py-3 text-slate-800 focus:outline-none focus:bg-white transition-all resize-none placeholder:text-slate-300',
                  errores.descripcion ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-emerald-500']"></textarea>
                <p v-if="errores.descripcion" class="text-xs text-red-500 mt-1 ml-1">{{ errores.descripcion }}</p>
              </div>

              <!-- Grid: Precio + Duración + Capacidad -->
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Precio (COP) <span class="text-emerald-500">*</span></label>
                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold">$</span>
                    <input v-model="newTour.precio" type="number" placeholder="0"
                      :class="['w-full bg-slate-50 border-2 rounded-2xl pl-9 pr-4 py-3 text-slate-800 font-semibold focus:outline-none focus:bg-white transition-all placeholder:text-slate-300 placeholder:font-normal',
                      errores.precio ? 'border-red-400' : 'border-slate-200 focus:border-emerald-500']">
                  </div>
                  <p v-if="errores.precio" class="text-xs text-red-500 mt-1 ml-1">{{ errores.precio }}</p>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Duración <span class="text-emerald-500">*</span></label>
                  <input v-model="newTour.duracion" type="text" placeholder="Ej: 8 horas"
                    :class="['w-full bg-slate-50 border-2 rounded-2xl px-4 py-3 text-slate-800 font-medium focus:outline-none focus:bg-white transition-all placeholder:text-slate-300',
                    errores.duracion ? 'border-red-400' : 'border-slate-200 focus:border-emerald-500']">
                  <p v-if="errores.duracion" class="text-xs text-red-500 mt-1 ml-1">{{ errores.duracion }}</p>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Capacidad Máx. <span class="text-emerald-500">*</span></label>
                  <input v-model="newTour.capacidad" type="number" placeholder="20"
                    :class="['w-full bg-slate-50 border-2 rounded-2xl px-4 py-3 text-slate-800 font-semibold focus:outline-none focus:bg-white transition-all placeholder:text-slate-300',
                    errores.capacidad ? 'border-red-400' : 'border-slate-200 focus:border-emerald-500']">
                  <p v-if="errores.capacidad" class="text-xs text-red-500 mt-1 ml-1">{{ errores.capacidad }}</p>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 2: UBICACIÓN ─── -->
            <section>
              <div class="flex items-center gap-3 mb-6">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">2</div>
                <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Ubicación</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
              </div>
              <input ref="locationInput" type="text" placeholder="Busca el lugar exacto del tour..."
                class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-3 text-slate-800 focus:outline-none focus:bg-white focus:border-emerald-500 transition-all placeholder:text-slate-300 mb-3">
              <div ref="mapContainer" class="w-full h-52 bg-slate-100 rounded-2xl overflow-hidden border-2 border-slate-200"></div>
              <div v-if="newTour.latitud && newTour.longitud" class="mt-2.5 flex items-center gap-2 text-xs text-emerald-600 font-bold">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                Coordenadas: {{ Number(newTour.latitud).toFixed(5) }}, {{ Number(newTour.longitud).toFixed(5) }}
              </div>
            </section>

            <!-- ─── SECCIÓN 3: ACTIVIDADES ─── -->
            <section>
              <div class="flex items-center gap-3 mb-6">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">3</div>
                <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Actividades <span class="text-emerald-500">*</span></h3>
                <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                <span v-if="newTour.actividades.length > 0"
                  class="flex-shrink-0 text-xs bg-emerald-100 text-emerald-700 font-bold px-3 py-1 rounded-full">
                  {{ newTour.actividades.length }} seleccionadas
                </span>
              </div>
              <div :class="['grid grid-cols-2 gap-2 max-h-56 overflow-y-auto form-scroll rounded-2xl border-2 p-3',
                errores.actividades ? 'border-red-300 bg-red-50/50' : 'border-slate-200 bg-slate-50']">
                <label v-for="actividad in actividades" :key="actividad.id"
                  :class="['flex items-start gap-3 p-3 rounded-xl cursor-pointer border-2 transition-all select-none',
                  newTour.actividades.includes(actividad.id)
                    ? 'border-emerald-400 bg-white shadow-sm shadow-emerald-100'
                    : 'border-transparent bg-white hover:border-emerald-200 hover:shadow-sm']">
                  <input type="checkbox" :value="actividad.id" v-model="newTour.actividades" class="hidden">
                  <div :class="['w-5 h-5 flex-shrink-0 rounded-md border-2 flex items-center justify-center mt-0.5 transition-all',
                    newTour.actividades.includes(actividad.id) ? 'border-emerald-600 bg-emerald-600' : 'border-slate-300']">
                    <svg v-if="newTour.actividades.includes(actividad.id)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-slate-700 leading-tight">{{ actividad.nombre }}</p>
                    <p class="text-xs text-slate-400 mt-0.5">Riesgo Nivel {{ actividad.nivel_riesgo }}</p>
                  </div>
                </label>
              </div>
              <p v-if="errores.actividades" class="text-xs text-red-500 mt-1.5 ml-1">{{ errores.actividades }}</p>
            </section>

            <!-- ─── SECCIÓN 4: ITINERARIO ─── -->
            <section>
              <div class="flex items-center gap-3 mb-6">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">4</div>
                <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Itinerario</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                <button @click.prevent="addItineraryItem" type="button"
                  class="flex-shrink-0 flex items-center gap-1.5 text-xs text-emerald-700 font-bold bg-emerald-100 hover:bg-emerald-200 px-3 py-1.5 rounded-full transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                  Agregar
                </button>
              </div>
              <div class="space-y-2.5">
                <div v-for="(item, index) in newTour.itinerario" :key="'iti-'+index"
                  class="flex gap-3 items-center group">
                  <span class="text-xs text-slate-300 font-mono w-5 text-center flex-shrink-0">{{ index + 1 }}</span>
                  <input v-model="item.time" type="time"
                    class="bg-slate-50 border-2 border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-500 transition-all w-32 flex-shrink-0">
                  <input v-model="item.activity" type="text" :placeholder="`Actividad ${index + 1}...`"
                    class="flex-1 bg-slate-50 border-2 border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 focus:outline-none focus:bg-white focus:border-emerald-500 transition-all placeholder:text-slate-300">
                  <button v-if="newTour.itinerario.length > 1" @click.prevent="removeItineraryItem(index)" type="button"
                    class="w-8 h-8 flex items-center justify-center rounded-full text-slate-300 hover:text-red-500 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100 flex-shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 5: QUÉ INCLUYE ─── -->
            <section>
              <div class="flex items-center gap-3 mb-6">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">5</div>
                <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">¿Qué Incluye?</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                <button @click.prevent="addIncludedItem" type="button"
                  class="flex-shrink-0 flex items-center gap-1.5 text-xs text-emerald-700 font-bold bg-emerald-100 hover:bg-emerald-200 px-3 py-1.5 rounded-full transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                  Agregar
                </button>
              </div>
              <div class="space-y-2.5">
                <div v-for="(item, index) in newTour.incluido" :key="'inc-'+index"
                  class="flex gap-3 items-center group">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                  <input v-model="item.item" type="text" :placeholder="`Beneficio ${index + 1}... ej: Transporte incluido`"
                    class="flex-1 bg-slate-50 border-2 border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 focus:outline-none focus:bg-white focus:border-emerald-500 transition-all placeholder:text-slate-300">
                  <button v-if="newTour.incluido.length > 1" @click.prevent="removeIncludedItem(index)" type="button"
                    class="w-8 h-8 flex items-center justify-center rounded-full text-slate-300 hover:text-red-500 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100 flex-shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
            </section>

            <!-- ─── SECCIÓN 6: GALERÍA DE IMÁGENES ─── -->
            <section>
              <div class="flex items-center gap-3 mb-6">
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">6</div>
                <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Galería de Imágenes</h3>
                <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                <span class="flex-shrink-0 text-xs text-slate-400 font-medium">{{ totalImageCount }} imagen{{ totalImageCount !== 1 ? 'es' : '' }}</span>
              </div>

              <!-- Imágenes existentes (modo edición) -->
              <div v-if="imagenesExistentes.length > 0" class="mb-5">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-slate-300"></span>
                  Imágenes guardadas
                </p>
                <div class="grid grid-cols-4 sm:grid-cols-5 gap-3">
                  <div v-for="(img, index) in imagenesExistentes" :key="'existing-'+img.id"
                    class="relative group rounded-2xl overflow-hidden aspect-square bg-slate-100 ring-2 ring-slate-200 shadow-sm">
                    <img :src="img.url" :alt="'Imagen guardada ' + (index+1)" class="w-full h-full object-cover">
                    <!-- Overlay hover -->
                    <div class="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                      <button @click.prevent="removeExistingImage(img.id, index)" type="button"
                        class="w-11 h-11 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center shadow-lg transition-all transform hover:scale-110">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                      </button>
                    </div>
                    <!-- Badge portada -->
                    <div v-if="img.es_portada"
                      class="absolute top-1.5 left-1.5 bg-amber-400 text-amber-900 text-[9px] font-bold px-2 py-0.5 rounded-full shadow">
                      PORTADA
                    </div>
                  </div>
                </div>
              </div>

              <!-- Aviso de imágenes a eliminar -->
              <div v-if="imagenesAEliminar.length > 0"
                class="mb-5 flex items-center gap-3 p-3.5 bg-red-50 border border-red-200 rounded-2xl">
                <div class="w-8 h-8 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0">
                  <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <p class="text-sm text-red-700 font-semibold">
                  {{ imagenesAEliminar.length }} imagen{{ imagenesAEliminar.length !== 1 ? 'es' : '' }} se eliminará{{ imagenesAEliminar.length !== 1 ? 'n' : '' }} al guardar.
                </p>
              </div>

              <!-- Nuevas imágenes -->
              <div v-if="newTour.imagen.length > 0" class="mb-5">
                <p class="text-[11px] font-bold text-emerald-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                  Nuevas imágenes a subir
                </p>
                <div class="grid grid-cols-4 sm:grid-cols-5 gap-3">
                  <div v-for="(img, index) in newTour.imagen" :key="'new-'+index"
                    class="relative group rounded-2xl overflow-hidden aspect-square bg-slate-100 ring-2 ring-emerald-400 shadow-sm">
                    <img :src="img.url" :alt="img.name" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                      <button @click.prevent="removeImage(index)" type="button"
                        class="w-11 h-11 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center shadow-lg transition-all transform hover:scale-110">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                      </button>
                    </div>
                    <div class="absolute top-1.5 left-1.5 bg-emerald-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full shadow">
                      NUEVA
                    </div>
                  </div>
                </div>
              </div>

              <!-- Drop Zone -->
              <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                @click="$refs.fileInput.click()"
                :class="['rounded-2xl border-2 border-dashed p-8 transition-all duration-200 cursor-pointer',
                isDragging ? 'border-emerald-500 bg-emerald-50 scale-[1.01] shadow-lg shadow-emerald-100' : 'border-slate-200 bg-slate-50 hover:border-emerald-300 hover:bg-emerald-50/40']">
                <div class="flex flex-col items-center gap-3 pointer-events-none">
                  <div :class="['w-14 h-14 rounded-2xl flex items-center justify-center transition-all', isDragging ? 'bg-emerald-100 rotate-3' : 'bg-white border border-slate-200']">
                    <svg :class="['w-7 h-7 transition-colors', isDragging ? 'text-emerald-600' : 'text-emerald-400']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                    </svg>
                  </div>
                  <div class="text-center">
                    <p class="text-sm font-bold text-slate-600">
                      <span class="text-emerald-600">Haz clic para seleccionar</span> o arrastra aquí
                    </p>
                    <p class="text-xs text-slate-400 mt-1">PNG, JPG, WEBP · Puedes subir múltiples imágenes</p>
                  </div>
                </div>
                <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect">
              </div>
            </section>

          </form>
        </div>

        <!-- === FOOTER === -->
        <div class="border-t border-slate-100 px-8 py-5 flex items-center justify-between gap-4 bg-white/80 backdrop-blur-sm flex-shrink-0 rounded-b-3xl">
          <p class="text-xs text-slate-400">Campos con <span class="text-emerald-500 font-bold">*</span> son obligatorios</p>
          <div class="flex items-center gap-3">
            <button @click="emit('cerrar')" type="button" :disabled="isLoading"
              class="px-6 py-2.5 rounded-2xl font-semibold text-slate-600 border-2 border-slate-200 hover:bg-slate-100 transition-colors disabled:opacity-50">
              Cancelar
            </button>
            <button @click="Enviar" type="button" :disabled="isLoading"
              class="px-7 py-2.5 rounded-2xl font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-700 hover:to-teal-600 shadow-lg shadow-emerald-200/60 transition-all flex items-center gap-2 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:hover:translate-y-0">
              <svg v-if="isLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else-if="paquete" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              {{ isLoading ? (paquete ? 'Actualizando...' : 'Creando...') : (paquete ? 'Guardar Cambios' : 'Crear Tour') }}
            </button>
          </div>
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