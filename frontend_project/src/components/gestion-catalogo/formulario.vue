<script setup>
    import { reactive, watch, ref } from 'vue';
     
    const props = defineProps(['abrir', 'datos'])
    const emit = defineEmits(['cerrar', 'enviar'])

    // --- ESTADOS DE CARGA Y VALIDACIÓN ---
    const isLoading = ref(false);
    const errores = reactive({});

    // --- REFERENCIAS ---
    const isDragging = ref(false);
    const fileInput = ref(null);
    const locationInput = ref(null);
    const mapContainer = ref(null);
    
    let map = null;
    let marker = null;
    let autocomplete = null;

    // --- ESTADO DEL FORMULARIO ---
    const newTour = reactive({
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
        imagen: [] 
    });

    const inicial = JSON.parse(JSON.stringify(newTour));

    watch(() => props.datos, (nuevosdatos) => {
        if(nuevosdatos){
            Object.assign(newTour, JSON.parse(JSON.stringify(nuevosdatos)));
            if (!newTour.itinerario || newTour.itinerario.length === 0) newTour.itinerario = [{ time: '', activity: '' }];
            if (!newTour.incluido || newTour.incluido.length === 0) newTour.incluido = [{ item: '' }];
        }else{
            Object.assign(newTour, JSON.parse(JSON.stringify(inicial)));
        }
        // Limpiar errores al abrir/cambiar datos
        Object.keys(errores).forEach(key => delete errores[key]);
    }, {immediate: true})

    // --- VALIDACIÓN DEL FORMULARIO ---
    const validarFormulario = () => {
        Object.keys(errores).forEach(key => delete errores[key]); // Reiniciar errores
        let valido = true;

        if (!newTour.nombre.trim()) { errores.nombre = "El nombre es obligatorio."; valido = false; }
        if (!newTour.descripcion.trim()) { errores.descripcion = "La descripción es obligatoria."; valido = false; }
        if (!newTour.precio || newTour.precio <= 0) { errores.precio = "Ingresa un precio válido mayor a 0."; valido = false; }
        if (!newTour.duracion.trim()) { errores.duracion = "La duración es obligatoria."; valido = false; }
        if (!newTour.capacidad || newTour.capacidad <= 0) { errores.capacidad = "Ingresa una capacidad válida mayor a 0."; valido = false; }
        if (newTour.actividades.length === 0) { errores.actividades = "Selecciona al menos una actividad."; valido = false; }
        // Se retiró la validación de ubicación

        return valido;
    };

    // --- FUNCIONES DINÁMICAS (ITINERARIO E INCLUIDO) ---
    const addItineraryItem = () => newTour.itinerario.push({ time: '', actividades: '' });
    const removeItineraryItem = (index) => { if (newTour.itinerario.length > 1) newTour.itinerario.splice(index, 1); };

    const addIncludedItem = () => newTour.incluido.push({ item: '' });
    const removeIncludedItem = (index) => { if (newTour.incluido.length > 1) newTour.incluido.splice(index, 1); };

    // --- LÓGICA DE GOOGLE MAPS ---
    const initMap = () => {
        if (typeof google === 'undefined' || !mapContainer.value || !locationInput.value) return;

        const defaultPos = { lat: 4.6097, lng: -74.0817 }; 

        map = new google.maps.Map(mapContainer.value, {
            center: defaultPos, zoom: 12, mapTypeControl: false, streetViewControl: false,
        });

        marker = new google.maps.Marker({ map, position: defaultPos, visible: false });

        autocomplete = new google.maps.places.Autocomplete(locationInput.value, {
            fields: ["geometry", "name", "formatted_address"],
        });

        autocomplete.bindTo("bounds", map);

        autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            if (!place.geometry || !place.geometry.location) return; // Simplemente no hace nada si no selecciona algo válido

            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(17);
            }
            
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
                script.src = `https://maps.googleapis.com/maps/api/js?key=TU_API_KEY&libraries=places&callback=iniciarMapaGlobal`;
                script.async = true; script.defer = true;
                document.head.appendChild(script);

                window.iniciarMapaGlobal = () => setTimeout(() => initMap(), 100);
            } else {
                setTimeout(() => initMap(), 100);
            }
        }
    });

    // --- LÓGICA DE DRAG & DROP ---
    const procesarArchivos = (archivos) => {
        const archivosValidos = Array.from(archivos).filter(file => file.type.startsWith('image/'));
        archivosValidos.forEach(file => {
            const urlPreview = URL.createObjectURL(file);
            newTour.imagen.push({ file, url: urlPreview, name: file.name });
        });
    };

    const handleDrop = (e) => { isDragging.value = false; if (e.dataTransfer.files) procesarArchivos(e.dataTransfer.files); };
    const handleSelect = (e) => { if (e.target.files) procesarArchivos(e.target.files); e.target.value = ''; };
    const removeImage = (index) => { URL.revokeObjectURL(newTour.imagen[index].url); newTour.imagen.splice(index, 1); };

    // --- ENVÍO DE DATOS ---
    const Enviar = async () => {
        // Asegurarnos de capturar el texto que el usuario haya escrito en el input aunque no haya seleccionado una opción de Google
        if (locationInput.value && locationInput.value.value) {
             newTour.ubicacion = locationInput.value.value;
        }

        if (!validarFormulario()) return;

        isLoading.value = true;
        
        try {
            const dataToSend = {
                ...newTour,
                itinerario: newTour.itinerario.filter(i => i.time.trim() !== '' && i.activity.trim() !== ''),
                incluido: newTour.incluido.filter(i => i.item.trim() !== '')
            };
            
            emit('enviar', dataToSend); 
            
            setTimeout(() => { isLoading.value = false; }, 1000);
        } catch (error) {
            console.error("Error al enviar", error);
            isLoading.value = false;
        }
    }
</script>

<template>
    <Teleport to="body">
      <div v-if="abrir" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
        
        <div class="bg-white/95 backdrop-blur-xl border border-white/80 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col relative animate-fade-in-up">
          
          <div class="flex items-start justify-between p-6 border-b border-slate-100">
            <div>
              <h2 class="text-xl font-bold text-emerald-900">Crear Nuevo Tour</h2>
              <p class="text-sm text-slate-500 mt-1">Agrega un nuevo tour a tu oferta</p>
            </div>
            <button @click="emit('cerrar')" class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>

          <div class="p-6 overflow-y-auto form-scroll relative">
            
            <div v-if="isLoading" class="absolute inset-0 bg-white/60 backdrop-blur-sm z-10 flex flex-col items-center justify-center rounded-lg">
                <div class="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
                <span class="text-emerald-800 font-semibold mt-3">Procesando...</span>
            </div>

            <form @submit.prevent="Enviar" class="space-y-6">
              
              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Nombre del Tour <span class="text-emerald-600">*</span></label>
                <input v-model="newTour.nombre" type="text" placeholder="Ej: Aventura en el Amazonas" 
                       :class="['w-full bg-[#f4fcf9] border rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 transition-all placeholder:text-slate-400', 
                                errores.nombre ? 'border-red-500 focus:ring-red-500/50' : 'border-[#d1ebe1] focus:ring-emerald-500/50 focus:border-emerald-500']">
                <span v-if="errores.nombre" class="text-xs text-red-500 mt-1 block">{{ errores.nombre }}</span>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Descripción <span class="text-emerald-600">*</span></label>
                <textarea v-model="newTour.descripcion" rows="3" placeholder="Describe la experiencia que ofreces" 
                          :class="['w-full bg-[#f4fcf9] border rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 transition-all resize-none placeholder:text-slate-400', 
                                   errores.descripcion ? 'border-red-500 focus:ring-red-500/50' : 'border-[#d1ebe1] focus:ring-emerald-500/50 focus:border-emerald-500']"></textarea>
                <span v-if="errores.descripcion" class="text-xs text-red-500 mt-1 block">{{ errores.descripcion }}</span>
              </div>

              <div class="bg-slate-50 p-4 rounded-xl border border-slate-100 transition-all">
                <label class="block text-sm font-semibold text-slate-700 mb-1">Ubicación (Busca un lugar)</label>
                <input ref="locationInput" type="text" placeholder="Ej: Parque Nacional Tayrona, Santa Marta" 
                       class="w-full bg-white border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400 mb-3">
                
                <div ref="mapContainer" class="w-full h-48 bg-slate-200 rounded-xl overflow-hidden border border-slate-200"></div>
                
                <div v-if="newTour.latitud && newTour.longitud" class="mt-2 text-xs text-emerald-600 font-medium flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  Coordenadas capturadas correctamente
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Precio por Persona (COP) <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.precio" type="number" placeholder="250000" 
                         :class="['w-full bg-[#f4fcf9] border rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 transition-all placeholder:text-slate-400', 
                                  errores.precio ? 'border-red-500 focus:ring-red-500/50' : 'border-[#d1ebe1] focus:ring-emerald-500/50 focus:border-emerald-500']">
                  <span v-if="errores.precio" class="text-xs text-red-500 mt-1 block">{{ errores.precio }}</span>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Duración <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.duracion" type="text" placeholder="Ej: 8 horas, 2 días" 
                         :class="['w-full bg-[#f4fcf9] border rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 transition-all placeholder:text-slate-400', 
                                  errores.duracion ? 'border-red-500 focus:ring-red-500/50' : 'border-[#d1ebe1] focus:ring-emerald-500/50 focus:border-emerald-500']">
                  <span v-if="errores.duracion" class="text-xs text-red-500 mt-1 block">{{ errores.duracion }}</span>
                </div>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Capacidad Máxima <span class="text-emerald-600">*</span></label>
                <input v-model="newTour.capacidad" type="number" placeholder="20" 
                       :class="['w-full bg-[#f4fcf9] border rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 transition-all placeholder:text-slate-400', 
                                errores.capacidad ? 'border-red-500 focus:ring-red-500/50' : 'border-[#d1ebe1] focus:ring-emerald-500/50 focus:border-emerald-500']">
                <span v-if="errores.capacidad" class="text-xs text-red-500 mt-1 block">{{ errores.capacidad }}</span>
              </div>

              <div :class="['bg-slate-50 p-4 rounded-xl border transition-all', errores.actividades ? 'border-red-300' : 'border-slate-100']">
                <label class="block text-sm font-semibold text-slate-700 mb-3">Actividades del Paquete <span class="text-emerald-600">*</span></label>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-64 overflow-y-auto pr-2 form-scroll">
                  <label v-for="actividad in datos" :key="actividad.id"
                         class="flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-white cursor-pointer hover:border-emerald-400 hover:bg-emerald-50/30 transition-all group">
                    <input type="checkbox" :value="actividad.id" v-model="newTour.actividades"
                           class="mt-0.5 w-4 h-4 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500/50">
                    <div class="flex flex-col">
                      <span class="text-sm font-medium text-slate-700 group-hover:text-emerald-800 transition-colors">{{ actividad.nombre }}</span>
                      <span class="text-xs text-slate-500">Riesgo: Nivel {{ actividad.nivel_riesgo }}</span>
                    </div>
                  </label>
                </div>
                <p v-if="errores.actividades" class="text-xs text-red-500 mt-2 font-medium">{{ errores.actividades }}</p>
              </div>

              <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div class="flex items-center justify-between mb-3">
                  <label class="block text-sm font-semibold text-slate-700">Itinerario Detallado</label>
                  <button @click.prevent="addItineraryItem" type="button" class="text-xs flex items-center gap-1 text-emerald-600 font-semibold hover:text-emerald-700 bg-emerald-50 hover:bg-emerald-100 px-2 py-1 rounded-md transition-colors border border-emerald-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    Agregar Horario
                  </button>
                </div>
                <div class="space-y-3">
                  <div v-for="(item, index) in newTour.itinerario" :key="'iti-'+index" class="flex gap-3 items-start relative group">
                    <div class="w-1/3 sm:w-1/4">
                      <input v-model="item.time" type="time" placeholder="Hora"
                             class="w-full bg-white border border-[#d1ebe1] rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm">
                    </div>
                    <div class="w-full relative">
                      <input v-model="item.activity" type="text" placeholder="Ej: Llegada y charla técnica"
                             class="w-full bg-white border border-[#d1ebe1] rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400 text-sm">
                      <button v-if="newTour.itinerario.length > 1" @click.prevent="removeItineraryItem(index)" type="button" 
                              class="absolute -right-2 -top-2 bg-white text-slate-400 hover:text-red-500 border border-slate-200 hover:border-red-200 rounded-full p-1 shadow-sm transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100" title="Eliminar">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div class="flex items-center justify-between mb-3">
                  <label class="block text-sm font-semibold text-slate-700">¿Qué incluye el paquete?</label>
                  <button @click.prevent="addIncludedItem" type="button" class="text-xs flex items-center gap-1 text-emerald-600 font-semibold hover:text-emerald-700 bg-emerald-50 hover:bg-emerald-100 px-2 py-1 rounded-md transition-colors border border-emerald-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    Agregar Ítem
                  </button>
                </div>
                <div class="space-y-3">
                  <div v-for="(item, index) in newTour.incluido" :key="'inc-'+index" class="relative group">
                    <input v-model="item.item" type="text" placeholder="Ej: Transporte ida y vuelta desde el hotel"
                           class="w-full bg-white border border-[#d1ebe1] rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400 text-sm pr-8">
                    <button v-if="newTour.incluido.length > 1" @click.prevent="removeIncludedItem(index)" type="button" 
                            class="absolute right-2 top-2 text-slate-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100" title="Eliminar">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Imágenes del Tour <span class="text-slate-400 font-normal">(opcional)</span></label>
                <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                     :class="['mt-2 w-full min-h-[8rem] border-2 border-dashed rounded-xl p-4 transition-colors duration-200 ease-in-out',
                              isDragging ? 'border-emerald-500 bg-emerald-50/50' : 'border-[#d1ebe1] bg-[#f4fcf9] hover:bg-emerald-50/30']">
                  <div class="flex flex-col items-center justify-center cursor-pointer mb-2" @click="$refs.fileInput.click()">
                    <svg class="w-8 h-8 mb-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    <p class="mb-1 text-sm text-slate-500 text-center"><span class="font-semibold text-emerald-600">Haz clic para buscar</span> o arrastra aquí</p>
                  </div>
                  <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect" />

                  <div v-if="newTour.imagen.length > 0" class="flex flex-wrap gap-3 mt-4 border-t border-[#d1ebe1] pt-4">
                    <div v-for="(img, index) in newTour.imagen" :key="index" class="relative group w-20 h-20 bg-slate-100 rounded-lg overflow-hidden shadow-sm border border-slate-200">
                      <img :src="img.url" :alt="img.name" class="w-full h-full object-cover" />
                      <button @click.stop="removeImage(index)" type="button" class="absolute top-1 right-1 bg-white text-slate-600 hover:text-red-600 hover:bg-red-50 p-1 rounded-full shadow transition-colors z-10" title="Quitar imagen">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

            </form>
          </div>

          <div class="p-6 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl flex justify-end gap-3">
            <button @click="emit('cerrar')" type="button" :disabled="isLoading" class="px-5 py-2.5 rounded-xl font-semibold text-slate-600 hover:bg-slate-200 transition-colors disabled:opacity-50">
              Cancelar
            </button>
            <button @click="Enviar" type="submit" :disabled="isLoading" 
                    class="px-5 py-2.5 rounded-xl font-semibold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm transition-all flex items-center gap-2 hover:-translate-y-0.5 disabled:opacity-70 disabled:hover:translate-y-0">
              <svg v-if="isLoading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ isLoading ? 'Guardando...' : 'Crear Tour' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
</template>