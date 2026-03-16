<script setup>
import { ref } from 'vue';

// Estado para controlar el modal
const isModalOpen = ref(false);

// Datos simulados de la tabla (basados en la captura)
const tours = ref([
  {
    id: 1,
    name: 'Playa Paraíso - Tour Todo Incluido',
    category: 'Playa',
    location: 'Cartagena, Colombia',
    duration: '8 horas',
    price: '$250.000',
    capacity: 20,
    rating: 4.8,
    reviews: 124,
    image: 'https://images.unsplash.com/photo-1512813195386-6cb8edc04fe5?auto=format&fit=crop&w=150&q=80'
  },
  {
    id: 2,
    name: 'Aventura en la Montaña',
    category: 'Aventura',
    location: 'Bogotá, Colombia',
    duration: '6 horas',
    price: '$180.000',
    capacity: 15,
    rating: 4.9,
    reviews: 89,
    image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=150&q=80'
  },
  {
    id: 3,
    name: 'City Tour Histórico',
    category: 'Cultural',
    location: 'Cartagena, Colombia',
    duration: '4 horas',
    price: '$120.000',
    capacity: 25,
    rating: 4.7,
    reviews: 156,
    image: 'https://images.unsplash.com/photo-1552559564-96e00192e2fb?auto=format&fit=crop&w=150&q=80'
  },
  {
    id: 4,
    name: 'Expedición Selva Tropical',
    category: 'Naturaleza',
    location: 'Amazonas, Colombia',
    duration: '2 días',
    price: '$450.000',
    capacity: 10,
    rating: 5.0,
    reviews: 67,
    image: 'https://images.unsplash.com/photo-1518182170546-076616fd61fd?auto=format&fit=crop&w=150&q=80'
  }
]);

// Estado del formulario
const newTour = ref({
  name: '',
  description: '',
  price: '',
  duration: '',
  location: '',
  capacity: '',
  category: '',
  itinerary: '',
  included: '',
  image: ''
});

// Funciones
const openModal = () => isModalOpen.value = true;
const closeModal = () => {
  isModalOpen.value = false;
  // Limpiar formulario al cerrar (opcional)
};
const saveTour = () => {
  console.log('Guardando tour:', newTour.value);
  closeModal();
};
const deleteTour = (id) => {
  console.log('Eliminar tour con ID:', id);
};
</script>

<template>
  <div class="min-h-screen bg-[#e8f4f1] text-slate-900 p-6 md:p-10 relative z-0">
    
    <main class="max-w-6xl mx-auto">
      <header class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 class="text-3xl font-bold text-emerald-900 tracking-tight">Gestión de Tours</h1>
          <p class="text-slate-600 mt-1">Administra tu oferta de experiencias turísticas</p>
        </div>
        <button @click="openModal" 
                class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 px-5 rounded-xl transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 w-fit">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Nuevo Tour
        </button>
      </header>

      <section class="bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm">
        
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-slate-800">Mis Tours</h2>
          <p class="text-sm text-slate-500">{{ tours.length }} tours en total</p>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr class="text-sm font-semibold text-slate-500 border-b border-white/80">
                <th class="pb-3 pl-2 w-1/3">Tour</th>
                <th class="pb-3">Ubicación</th>
                <th class="pb-3">Duración</th>
                <th class="pb-3">Precio</th>
                <th class="pb-3">Capacidad</th>
                <th class="pb-3">Calificación</th>
                <th class="pb-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tour in tours" :key="tour.id" class="border-b border-white/40 hover:bg-white/40 transition-colors group">
                <td class="py-4 pl-2">
                  <div class="flex items-center gap-3">
                    <img :src="tour.image" alt="Tour image" class="w-12 h-12 rounded-lg object-cover border border-white shadow-sm" />
                    <div>
                      <h3 class="font-semibold text-slate-800 text-sm">{{ tour.name }}</h3>
                      <span class="text-xs text-slate-500">{{ tour.category }}</span>
                    </div>
                  </div>
                </td>
                <td class="py-4 text-sm text-slate-600">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                    {{ tour.location }}
                  </div>
                </td>
                <td class="py-4 text-sm text-slate-600">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    {{ tour.duration }}
                  </div>
                </td>
                <td class="py-4 text-sm font-medium text-slate-800">{{ tour.price }}</td>
                <td class="py-4 text-sm text-slate-600">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    {{ tour.capacity }}
                  </div>
                </td>
                <td class="py-4 text-sm text-slate-800">
                  <div class="flex items-center gap-1">
                    {{ tour.rating }}
                    <svg class="w-4 h-4 text-amber-400 fill-amber-400" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    <span class="text-slate-500">({{ tour.reviews }})</span>
                  </div>
                </td>
                <td class="py-4">
                  <div class="flex items-center justify-center gap-2">
                    <button class="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-transparent hover:border-emerald-200" title="Editar">
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button @click="deleteTour(tour.id)" class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-200" title="Eliminar">
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </main>

    <Teleport to="body">
      <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
        
        <div class="bg-white/95 backdrop-blur-xl border border-white/80 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col relative animate-fade-in-up">
          
          <div class="flex items-start justify-between p-6 border-b border-slate-100">
            <div>
              <h2 class="text-xl font-bold text-emerald-900">Crear Nuevo Tour</h2>
              <p class="text-sm text-slate-500 mt-1">Agrega un nuevo tour a tu oferta</p>
            </div>
            <button @click="closeModal" class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>

          <div class="p-6 overflow-y-auto form-scroll">
            <form @submit.prevent="saveTour" class="space-y-5">
              
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
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Ubicación <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.location" type="text" placeholder="Ciudad, País" 
                         class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-1">Capacidad Máxima <span class="text-emerald-600">*</span></label>
                  <input v-model="newTour.capacity" type="number" placeholder="20" 
                         class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
                </div>
              </div>

              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1">Categoría <span class="text-emerald-600">*</span></label>
                <input v-model="newTour.category" type="text" placeholder="Ej: Aventura, Playa, Cultural" 
                       class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400" required>
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
                <label class="block text-sm font-semibold text-slate-700 mb-1">URL de Imagen <span class="text-slate-400 font-normal">(opcional)</span></label>
                <input v-model="newTour.image" type="text" placeholder="https://ejemplo.com/imagen.jpg" 
                       class="w-full bg-[#f4fcf9] border border-[#d1ebe1] rounded-xl px-4 py-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-400">
                <p class="text-xs text-slate-500 mt-1">Si no proporcionas una imagen, se usará una predeterminada.</p>
              </div>

            </form>
          </div>

          <div class="p-6 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl flex justify-end gap-3">
            <button @click="closeModal" type="button" class="px-5 py-2.5 rounded-xl font-semibold text-slate-600 hover:bg-slate-200 transition-colors">
              Cancelar
            </button>
            <button @click="saveTour" type="button" class="px-5 py-2.5 rounded-xl font-semibold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm transition-all hover:-translate-y-0.5">
              Crear Tour
            </button>
          </div>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<style scoped>
/* Animación simple para la entrada del modal (opcional, pero mejora la UX) */
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Personalización sutil del scrollbar para el modal */
.form-scroll::-webkit-scrollbar {
  width: 6px;
}
.form-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.form-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
</style>