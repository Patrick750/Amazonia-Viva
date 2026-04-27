<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import axios from '@/api/axios';
import { useNotificacion } from '@/composables/useNotificacion';

const { mostrarNotificacion } = useNotificacion();

const props = defineProps({
  abrir: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['cerrar', 'cargaExitosa']);

const isLoading = ref(false);
const isDragging = ref(false);
const fileInput = ref(null);
const archivoSeleccionado = ref(null);
const erroresCarga = ref([]);
const resultadosCarga = ref(null);

const handleDrop = (e) => {
  isDragging.value = false;
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    procesarArchivo(e.dataTransfer.files[0]);
  }
};

const handleSelect = (event) => {
  if (event.target.files && event.target.files.length > 0) {
    procesarArchivo(event.target.files[0]);
  }
};

const procesarArchivo = (file) => {
  // Validate extension
  const extension = file.name.split('.').pop().toLowerCase();
  if (!['csv', 'xlsx', 'xls'].includes(extension)) {
    mostrarNotificacion('Formato no soportado. Usa .csv, .xlsx o .xls', 'error');
    return;
  }
  archivoSeleccionado.value = file;
  erroresCarga.value = [];
  resultadosCarga.value = null;
};

const removerArchivo = () => {
  archivoSeleccionado.value = null;
  if (fileInput.value) fileInput.value.value = '';
  erroresCarga.value = [];
  resultadosCarga.value = null;
};

const descargarPlantilla = async () => {
  try {
    const res = await axios.get('api/pack/carga-masiva/', { responseType: 'blob' });
    const url = URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "plantilla_tours.xlsx");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error descargando plantilla", error);
    mostrarNotificacion("Error al descargar la plantilla", "error");
  }
};

const subirArchivo = async () => {
  if (!archivoSeleccionado.value) return;

  isLoading.value = true;
  erroresCarga.value = [];
  resultadosCarga.value = null;

  try {
    const formData = new FormData();
    formData.append('archivo', archivoSeleccionado.value);

    const res = await axios.post('api/pack/carga-masiva/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    resultadosCarga.value = res.data;
    if (res.data.errores && res.data.errores.length > 0) {
      erroresCarga.value = res.data.errores;
      mostrarNotificacion(`Carga completada con ${res.data.errores.length} errores`, 'warning');
    } else {
      mostrarNotificacion(res.data.mensaje || 'Carga masiva exitosa', 'exito');
      setTimeout(() => {
        emit('cargaExitosa');
        cerrarModal();
      }, 2000);
    }

  } catch (error) {
    console.error('Error en carga masiva:', error);
    let msg = 'Hubo un error al procesar el archivo.';
    if (error.response?.data?.error) {
      msg = error.response.data.error;
    }
    mostrarNotificacion(msg, 'error');
  } finally {
    isLoading.value = false;
  }
};

const cerrarModal = () => {
  removerArchivo();
  emit('cerrar');
};

</script>

<template>
  <Teleport to="body">
    <div v-if="abrir"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4"
      @click.self="cerrarModal">

      <div class="absolute inset-0 bg-black/80 backdrop-blur-md"></div>

      <div class="relative bg-[#0d2114] border border-white/10 rounded-[2.5rem] shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden animate-fade-in-up">
        
        <!-- HEADER -->
        <div class="bg-gradient-to-br from-emerald-600 to-emerald-900 px-7 sm:px-9 py-6 sm:py-8 flex-shrink-0 relative overflow-hidden">
          <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/leaf.png')] opacity-10"></div>
          <div class="relative z-10 flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-3">
                <span class="inline-flex items-center gap-1.5 text-[10px] font-black tracking-[0.2em] uppercase text-emerald-200/70">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/></svg>
                  Carga Masiva
                </span>
              </div>
              <h2 class="text-3xl font-black text-white leading-tight">
                Importar Tours
              </h2>
              <p class="text-emerald-100/60 text-sm mt-1.5 font-medium italic">
                Sube un archivo Excel o CSV para crear múltiples tours a la vez.
              </p>
            </div>
            <button @click="cerrarModal"
              class="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-2xl bg-white/10 hover:bg-white/20 text-white transition-all hover:rotate-90 duration-300 border border-white/5">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="isLoading"
          class="absolute inset-0 bg-[#0d2114]/90 backdrop-blur-md z-20 flex flex-col items-center justify-center rounded-[2.5rem]">
          <div class="w-16 h-16 border-4 border-emerald-500/10 border-t-emerald-500 rounded-full animate-spin mb-6"></div>
          <p class="text-white font-black text-xl tracking-tight">Procesando archivo...</p>
          <p class="text-emerald-500/50 text-sm mt-2 font-medium">Esto puede tomar un momento dependiendo del tamaño.</p>
        </div>

        <!-- FORM BODY -->
        <div class="p-7 sm:p-9 bg-[#0a1a0f] space-y-6">
          
          <div class="flex items-center justify-between bg-white/5 border border-white/10 p-4 rounded-2xl">
            <div>
              <h3 class="text-white font-bold text-sm">¿No tienes la plantilla?</h3>
              <p class="text-white/40 text-xs">Descarga el formato correcto para asegurar la compatibilidad.</p>
            </div>
            <button @click="descargarPlantilla" type="button" class="px-4 py-2 bg-emerald-500/10 text-emerald-400 font-bold text-xs rounded-xl border border-emerald-500/20 hover:bg-emerald-500/20 transition-all flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
              Descargar Excel
            </button>
          </div>

          <div v-if="!archivoSeleccionado">
            <!-- Drop Zone -->
            <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                @click="$refs.fileInput.click()"
                :class="['rounded-[2rem] border-2 border-dashed p-10 transition-all duration-300 cursor-pointer text-center flex flex-col items-center gap-4',
                isDragging ? 'border-emerald-500 bg-emerald-500/10 scale-[1.01] shadow-2xl shadow-emerald-500/20' : 'border-white/10 bg-white/3 hover:border-emerald-500/40 hover:bg-white/5']">
                
                <div :class="['w-16 h-16 rounded-[1.5rem] flex items-center justify-center transition-all', isDragging ? 'bg-emerald-500 text-black rotate-6' : 'bg-white/5 border border-white/10 text-emerald-500']">
                  <svg :class="['w-8 h-8 transition-colors', isDragging ? 'text-black' : 'text-emerald-500']" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-black text-white/70">
                    <span class="text-emerald-400">Selecciona</span> o arrastra tu archivo aquí
                  </p>
                  <p class="text-[11px] text-white/20 mt-2 font-bold uppercase tracking-widest">.CSV, .XLSX, .XLS</p>
                </div>
                <input ref="fileInput" type="file" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" class="hidden" @change="handleSelect">
            </div>
          </div>
          
          <div v-else class="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 bg-emerald-500 text-black rounded-xl flex items-center justify-center font-black">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              </div>
              <div>
                <p class="text-white font-bold text-sm">{{ archivoSeleccionado.name }}</p>
                <p class="text-white/40 text-xs mt-0.5">{{ (archivoSeleccionado.size / 1024).toFixed(2) }} KB</p>
              </div>
            </div>
            <button @click="removerArchivo" class="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center hover:bg-rose-500 hover:text-white transition-all">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <!-- RESULTADOS DE CARGA -->
          <div v-if="resultadosCarga" class="mt-6 border-t border-white/5 pt-6 space-y-4">
            <div class="flex items-center gap-3">
              <span class="flex items-center justify-center w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              </span>
              <p class="text-white font-bold text-sm">{{ resultadosCarga.mensaje }}</p>
            </div>
            
            <div v-if="erroresCarga.length > 0" class="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-4">
              <h4 class="text-rose-400 font-bold text-xs mb-3 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                Errores en filas ({{ erroresCarga.length }})
              </h4>
              <ul class="text-rose-300/80 text-[11px] space-y-1.5 max-h-32 overflow-y-auto form-scroll pr-2">
                <li v-for="(error, i) in erroresCarga" :key="i" class="list-disc ml-4">{{ error }}</li>
              </ul>
            </div>
          </div>

        </div>

        <!-- FOOTER -->
        <div class="border-t border-white/5 px-8 py-6 flex items-center justify-end gap-4 bg-[#0d2114] flex-shrink-0 rounded-b-[2.5rem]">
            <button @click="cerrarModal" type="button" :disabled="isLoading"
              class="px-6 py-3 rounded-2xl font-black text-[11px] uppercase tracking-widest text-white/40 border-2 border-white/5 hover:bg-white/5 hover:text-white transition-all disabled:opacity-30">
              Cancelar
            </button>
            <button @click="subirArchivo" type="button" :disabled="isLoading || !archivoSeleccionado"
              class="px-8 py-3 rounded-2xl font-black text-[11px] uppercase tracking-widest text-black bg-emerald-500 hover:bg-emerald-400 shadow-xl shadow-emerald-900/40 transition-all flex items-center gap-3 hover:-translate-y-1 active:translate-y-0 disabled:opacity-50 disabled:hover:translate-y-0 disabled:cursor-not-allowed">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/></svg>
              Iniciar Importación
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
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.form-scroll::-webkit-scrollbar { width: 5px; }
.form-scroll::-webkit-scrollbar-track { background: transparent; }
.form-scroll::-webkit-scrollbar-thumb { background-color: #f43f5e; border-radius: 20px; }
</style>
