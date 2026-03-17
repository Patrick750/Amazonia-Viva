<script setup>
    import { reactive, watch, ref, onMounted } from 'vue';
     
    const props = defineProps(['abrir', 'datos'])
    const emit = defineEmits(['cerrar', 'guardar'])

    // Referencias para el Drag & Drop
    const isDragging = ref(false);
    const fileInput = ref(null);

    // Referencias para Google Maps
    const locationInput = ref(null);
    const mapContainer = ref(null);
    let map = null;
    let marker = null;
    let autocomplete = null;

    // Estado del formulario (Añadidos lat y lng)
    const newTour = reactive({
        name: '',
        description: '',
        price: '',
        duration: '',
        location: '',
        lat: null, // Nueva propiedad
        lng: null, // Nueva propiedad
        capacity: '',
        category: '',
        itinerary: '',
        included: '',
        images: [] 
    });

    const inicial = reactive({ ...newTour})

    watch(() => props.datos, (nuevosdatos) => {
        if(nuevosdatos){
            Object.assign(newTour, nuevosdatos)
            // Si editas un tour con lat/lng previo, aquí podrías actualizar el marcador del mapa
        }else{
            Object.assign(newTour, inicial)
        }
    }, {immediate: true})

    // --- LÓGICA DE GOOGLE MAPS ---
    const initMap = () => {
        // Asegurarnos de que el objeto de google exista y el modal esté abierto
        if (typeof google === 'undefined' || !mapContainer.value || !locationInput.value) return;

        // Coordenadas por defecto (ejemplo: un punto central o dejar un zoom alejado)
        const defaultPos = { lat: 4.6097, lng: -74.0817 }; // Bogotá por defecto

        map = new google.maps.Map(mapContainer.value, {
            center: defaultPos,
            zoom: 12,
            mapTypeControl: false,
            streetViewControl: false,
        });

        marker = new google.maps.Marker({
            map,
            position: defaultPos,
            visible: false // Oculto hasta que seleccionen un lugar
        });

        // Inicializar Autocompletado
        autocomplete = new google.maps.places.Autocomplete(locationInput.value, {
            fields: ["geometry", "name", "formatted_address"],
        });

        autocomplete.bindTo("bounds", map);

        // Escuchar cuando el usuario selecciona un lugar
        autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            
            if (!place.geometry || !place.geometry.location) {
                return; // El usuario no seleccionó una sugerencia válida
            }

            // Centrar el mapa en el lugar seleccionado
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(17);
            }
            
            // Mover y mostrar el marcador
            marker.setPosition(place.geometry.location);
            marker.setVisible(true);

            // Actualizar nuestro estado reactivo con los datos exactos
            newTour.location = place.formatted_address || place.name;
            newTour.lat = place.geometry.location.lat();
            newTour.lng = place.geometry.location.lng();
        });
    };

// Vigilar cuando se abre el modal para cargar el script e inicializar el mapa
    watch(() => props.abrir, (estaAbierto) => {
        if (estaAbierto) {
            // Verificamos si el script ya se cargó antes para no cargarlo dos veces
            if (typeof google === 'undefined') {
                const script = document.createElement('script');
                
                // AQUÍ VA TU API KEY 👇
                script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyDaDxKnE-8fzSc58TS-sMCm3UiP9cY577U&libraries=places&callback=iniciarMapaGlobal`;
                
                script.async = true;
                script.defer = true;
                document.head.appendChild(script);

                // Función global que Google Maps llama cuando termina de cargar
                window.iniciarMapaGlobal = () => {
                    setTimeout(() => {
                        initMap();
                    }, 100);
                };
            } else {
                // Si el script ya estaba cargado (ej. abrieron y cerraron el modal), solo iniciamos el mapa
                setTimeout(() => {
                    initMap();
                }, 100);
            }
        }
    });

    // --- LÓGICA DE DRAG & DROP ---
    const procesarArchivos = (archivos) => {
        const archivosValidos = Array.from(archivos).filter(file => file.type.startsWith('image/'));
        archivosValidos.forEach(file => {
            const urlPreview = URL.createObjectURL(file);
            newTour.images.push({ file, url: urlPreview, name: file.name });
        });
    };

    const handleDrop = (e) => {
        isDragging.value = false;
        if (e.dataTransfer.files) procesarArchivos(e.dataTransfer.files);
    };

    const handleSelect = (e) => {
        if (e.target.files) procesarArchivos(e.target.files);
        e.target.value = '';
    };

    const removeImage = (index) => {
        URL.revokeObjectURL(newTour.images[index].url);
        newTour.images.splice(index, 1);
    };
    // --- FIN LÓGICA DRAG & DROP ---

    const enviar = () => {
        emit('guardar', { ...newTour }) 
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

          <div class="p-6 overflow-y-auto form-scroll">
            <form @submit.prevent="enviar" class="space-y-5">
              
              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Nombre del Tour <span class="text-emerald-600">*</span></label>
                <input v-model="newTour.name" type="text" placeholder="Ej: Aventura en el Amazonas" 
                       class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Descripción <span class="text-emerald-600">*</span></label>
                <textarea v-model="newTour.description" rows="3" placeholder="Describe la experiencia que ofreces" 
                          class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all resize-none placeholder:text-slate-400" required></textarea>
              </div>

              <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <label class="block text-sm font-semibold text-slate-700 mb-1">Ubicación (Busca un lugar) <span class="text-emerald-600">*</span></label>
                <input ref="locationInput" type="text" placeholder="Ej: Parque Nacional Tayrona, Santa Marta" 
                       class="w-full bg-white border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400 mb-3" required>
                
                <div ref="mapContainer" class="w-full h-48 bg-slate-200 rounded-xl overflow-hidden border border-slate-200"></div>
                
                <div v-if="newTour.lat && newTour.lng" class="mt-2 text-xs text-emerald-600 font-medium flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  Coordenadas capturadas correctamente
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Precio por Persona (COP) <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.price" type="number" placeholder="250000" 
                         class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Duración <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.duration" type="text" placeholder="Ej: 8 horas, 2 días" 
                         class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Capacidad Máxima <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.capacity" type="number" placeholder="20" 
                         class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Categoría <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.category" type="text" placeholder="Ej: Aventura, Playa" 
                         class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
                </div>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Itinerario <span class="text-slate-400 font-normal">(una línea por actividad)</span></label>
                <textarea v-model="newTour.itinerary" rows="3" placeholder="8:00 AM - Recogida en hotel&#10;9:00 AM - Inicio del tour" 
                          class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all resize-none placeholder:text-slate-400"></textarea>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Incluido <span class="text-slate-400 font-normal">(una línea por ítem)</span></label>
                <textarea v-model="newTour.included" rows="3" placeholder="Transporte&#10;Guía profesional" 
                          class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all resize-none placeholder:text-slate-400"></textarea>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Imágenes del Tour <span class="text-slate-400 font-normal">(opcional)</span></label>
                
                <div 
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @drop.prevent="handleDrop"
                  :class="[
                    'mt-2 w-full min-h-[8rem] border-2 border-dashed rounded-xl p-4 transition-colors duration-200 ease-in-out',
                    isDragging ? 'border-emerald-500 bg-emerald-50/50' : 'border-[#d1ebe1] bg-[#f4fcf9] hover:bg-emerald-50/30'
                  ]"
                >
                  <div class="flex flex-col items-center justify-center cursor-pointer mb-2" @click="$refs.fileInput.click()">
                    <svg class="w-8 h-8 mb-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    <p class="mb-1 text-sm text-slate-500 text-center"><span class="font-semibold text-emerald-600">Haz clic para buscar</span> o arrastra aquí</p>
                  </div>
                  <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect" />

                  <div v-if="newTour.images.length > 0" class="flex flex-wrap gap-3 mt-4 border-t border-[#d1ebe1] pt-4">
                    <div v-for="(img, index) in newTour.images" :key="index" class="relative group w-20 h-20 bg-slate-100 rounded-lg overflow-hidden shadow-sm border border-slate-200">
                      
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
            <button @click="emit('cerrar')" type="button" class="px-5 py-2.5 rounded-xl font-semibold text-slate-600 hover:bg-slate-200 transition-colors">
              Cancelar
            </button>
            <button @click="enviar" type="submit" class="px-5 py-2.5 rounded-xl font-semibold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm transition-all hover:-translate-y-0.5">
              Crear Tour
            </button>
          </div>
        </div>
      </div>
    </Teleport>
</template>