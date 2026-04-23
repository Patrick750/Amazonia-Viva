<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '@/api/axios';

// ── Estado global ─────────────────────────────────────────────────────────────
const cargando        = ref(true);
const saldos          = ref(null);
const errorSaldos     = ref('');

// ── Movimientos ───────────────────────────────────────────────────────────────
const movimientos     = ref([]);
const paginacion      = ref({ page: 1, page_size: 15, total_count: 0, total_pages: 1 });
const cargandoMovs    = ref(false);
const filtroTipo      = ref('todos');
const filtroDesde     = ref('');
const filtroHasta     = ref('');

// ── Modal Retiro ──────────────────────────────────────────────────────────────
const showRetiroModal  = ref(false);
const retiroMonto      = ref('');
const retiroMetodo     = ref('');
const retiroDatos      = ref({ banco: '', cuenta: '', tipo_cuenta: '', titular: '', numero: '' });
const retiroProcesando = ref(false);
const retiroExito      = ref(null);
const retiroError      = ref('');

// ── Exportar ──────────────────────────────────────────────────────────────────
const exportando       = ref(false);

// ── Helpers ───────────────────────────────────────────────────────────────────
const COP = (v) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(v || 0);

const formatFecha = (iso) => {
  if (!iso) return '—';
  return new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(iso));
};

// ── Carga de saldos ───────────────────────────────────────────────────────────
async function cargarSaldos() {
  cargando.value = true;
  errorSaldos.value = '';
  try {
    const { data } = await axios.get('api/liquidacion/saldos/');
    saldos.value = data;
  } catch (e) {
    errorSaldos.value = e.response?.data?.error || 'No se pudieron cargar los saldos.';
  } finally {
    cargando.value = false;
  }
}

// ── Carga de movimientos ──────────────────────────────────────────────────────
async function cargarMovimientos(page = 1) {
  cargandoMovs.value = true;
  try {
    const params = {
      page,
      page_size: paginacion.value.page_size,
      tipo: filtroTipo.value,
    };
    if (filtroDesde.value) params.fecha_desde = filtroDesde.value;
    if (filtroHasta.value) params.fecha_hasta = filtroHasta.value;
    const { data } = await axios.get('api/liquidacion/movimientos/', { params });
    movimientos.value  = data.movimientos;
    paginacion.value   = data.pagination;
  } catch (e) {
    console.error('Error cargando movimientos:', e);
  } finally {
    cargandoMovs.value = false;
  }
}

function aplicarFiltros() { cargarMovimientos(1); }

function irPagina(p) {
  if (p < 1 || p > paginacion.value.total_pages) return;
  cargarMovimientos(p);
}

onMounted(() => {
  cargarSaldos();
  cargarMovimientos();
});

// ── Retiro ────────────────────────────────────────────────────────────────────
function abrirRetiro() {
  retiroMonto.value     = '';
  retiroMetodo.value    = '';
  retiroDatos.value     = { banco: '', cuenta: '', tipo_cuenta: 'ahorros', titular: '', numero: '' };
  retiroExito.value     = null;
  retiroError.value     = '';
  showRetiroModal.value = true;
}

function cerrarRetiro() {
  showRetiroModal.value = false;
}

const montoParsed = computed(() => {
  const raw = String(retiroMonto.value).replace(/\./g, '').replace(',', '.');
  return parseFloat(raw) || 0;
});

async function confirmarRetiro() {
  retiroError.value = '';
  if (!retiroMonto.value || montoParsed.value <= 0) {
    retiroError.value = 'Ingresa un monto válido.';
    return;
  }
  if (!retiroMetodo.value) {
    retiroError.value = 'Selecciona un método de retiro.';
    return;
  }
  retiroProcesando.value = true;
  try {
    const { data } = await axios.post('api/liquidacion/solicitar-retiro/', {
      monto: montoParsed.value,
      metodo: retiroMetodo.value,
      datos_bancarios: retiroDatos.value,
    });
    retiroExito.value = data;
    setTimeout(() => {
      cerrarRetiro();
      cargarSaldos();
    }, 3500);
  } catch (e) {
    retiroError.value = e.response?.data?.error || 'Error al procesar el retiro.';
  } finally {
    retiroProcesando.value = false;
  }
}

// ── Exportar ──────────────────────────────────────────────────────────────────
async function exportarReporte(formato = 'csv') {
  exportando.value = true;
  try {
    const params = { tipo: filtroTipo.value, formato };
    if (filtroDesde.value) params.fecha_desde = filtroDesde.value;
    if (filtroHasta.value) params.fecha_hasta = filtroHasta.value;

    const response = await axios.get('api/liquidacion/exportar/', {
      params,
      responseType: 'blob',
    });

    const mimes = {
      csv: 'text/csv;charset=utf-8;',
      excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      pdf: 'application/pdf',
    };

    const blobType = formato === 'xls' || formato === 'excel' ? mimes.excel : (formato === 'pdf' ? mimes.pdf : mimes.csv);
    const url = URL.createObjectURL(new Blob([response.data], { type: blobType }));
    const a = document.createElement('a');
    const ext = (formato === 'xls' || formato === 'excel') ? 'xlsx' : (formato === 'pdf' ? 'pdf' : 'csv');
    a.href = url;
    a.download = `movimientos_amazonia_${new Date().toISOString().slice(0, 10)}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    console.error('Error exportando:', e);
  } finally {
    exportando.value = false;
  }
}

// ── Clases de tipo de movimiento ──────────────────────────────────────────────
const tipoClases = {
  ingreso:   'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  pendiente: 'text-amber-400  bg-amber-500/10  border-amber-500/25',
  reembolso: 'text-red-400    bg-red-500/10    border-red-500/25',
};
const tipoLabel = { ingreso: 'Ingreso', pendiente: 'Pendiente', reembolso: 'Reembolso' };
const tipoIcono = {
  ingreso:   'M5 10l7-7 7 7M12 3v18',
  pendiente: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  reembolso: 'M19 14l-7 7-7-7M12 21V3',
};

// Icono de método de retiro
const metodoIconos = {
  transferencia_bancaria: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3z',
  nequi:   'M12 18h.01M8 21h8a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2z',
  daviplata:'M12 18h.01M8 21h8a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2z',
  pse:     'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0 1 12 2.944a11.955 11.955 0 0 1-8.618 3.04A12.02 12.02 0 0 0 3 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
};
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] text-white font-sans">

    <!-- ── HERO ─────────────────────────────────────────────────────────── -->
    <section class="relative pt-28 pb-10 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-[#0a1f12] via-[#0a1a0f] to-[#0a1a0f]"></div>
      <div class="absolute top-20 left-1/3 w-80 h-80 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-64 h-64 rounded-full bg-teal-400/4 blur-3xl pointer-events-none"></div>

      <div class="relative z-10 max-w-6xl mx-auto px-6">
        <div class="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-400/20 text-emerald-300 text-[11px] font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3z"/>
          </svg>
          Billetera Virtual
        </div>
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 class="text-4xl sm:text-5xl font-black text-white leading-tight mb-2">Liquidación</h1>
            <p class="text-white/45 text-base max-w-lg">Gestiona tus saldos, solicita retiros y consulta el historial de movimientos financieros.</p>
          </div>
          <!-- Botón retiro y volver -->
          <div class="flex items-center gap-3">
            <template v-if="saldos && saldos.saldo_disponible > 0">
              <button
                @click="abrirRetiro"
                class="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-black text-sm transition-all shadow-xl shadow-emerald-500/25 hover:scale-105 flex-shrink-0"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Solicitar Retiro
              </button>
            </template>
            <router-link
              to="/panel/dashboard"
              class="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-bold text-sm transition-all border border-white/10 flex-shrink-0"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
              </svg>
              Volver al Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CONTENIDO PRINCIPAL ────────────────────────────────────────────── -->
    <main class="max-w-6xl mx-auto px-6 pb-28 space-y-8 relative z-10">

      <!-- ── SKELETON LOADING ─────────────────────────────────────────── -->
      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div v-for="i in 3" :key="i"
          class="bg-white/5 rounded-2xl border border-white/8 p-6 animate-pulse h-36 relative overflow-hidden">
          <div class="shimmer absolute inset-0 rounded-2xl"></div>
          <div class="h-3 bg-white/8 rounded w-1/2 mb-4"></div>
          <div class="h-8 bg-white/10 rounded w-3/4 mb-2"></div>
          <div class="h-2 bg-white/6 rounded w-2/3"></div>
        </div>
      </div>

      <!-- ── ERROR ─────────────────────────────────────────────────────── -->
      <div v-else-if="errorSaldos"
        class="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-red-300 text-sm flex items-center gap-3">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        {{ errorSaldos }}
      </div>

      <!-- ── TARJETAS DE SALDO ────────────────────────────────────────── -->
      <template v-else-if="saldos">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

          <!-- Saldo Total -->
          <div class="relative bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/25 rounded-2xl p-6 overflow-hidden group hover:border-emerald-400/40 transition-all duration-300">
            <div class="absolute -right-6 -bottom-6 w-32 h-32 rounded-full bg-emerald-500/8 group-hover:bg-emerald-500/14 transition-all duration-500"></div>
            <p class="text-[11px] uppercase tracking-widest font-bold text-emerald-400/70 mb-1">Saldo Total</p>
            <p class="text-3xl font-black text-white tabular-nums leading-none mb-1">{{ COP(saldos.saldo_total) }}</p>
            <p class="text-xs text-white/40">Bruto: {{ COP(saldos.bruto_total) }}</p>
            <div class="mt-4 flex items-center gap-1.5">
              <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
              <span class="text-[11px] text-emerald-400/80 font-semibold">Neto después de comisión</span>
            </div>
          </div>

          <!-- Saldo Disponible -->
          <div class="relative bg-white/4 border border-white/10 rounded-2xl p-6 overflow-hidden group hover:bg-white/6 hover:border-white/18 transition-all duration-300">
            <div class="absolute -right-6 -bottom-6 w-28 h-28 rounded-full bg-blue-500/6 group-hover:bg-blue-500/10 transition-all duration-500"></div>
            <p class="text-[11px] uppercase tracking-widest font-bold text-blue-300/70 mb-1">Disponible para Retiro</p>
            <p class="text-3xl font-black text-blue-300 tabular-nums leading-none mb-1">{{ COP(saldos.saldo_disponible) }}</p>
            <p class="text-xs text-white/40">Ventas completadas y liquidadas</p>
            <button
              v-if="saldos.saldo_disponible > 0"
              @click="abrirRetiro"
              class="mt-4 text-[11px] font-black uppercase tracking-widest text-blue-300 hover:text-blue-200 transition-colors flex items-center gap-1"
            >
              Retirar ahora
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </button>
          </div>

          <!-- Saldo Pendiente -->
          <div class="relative bg-white/4 border border-white/10 rounded-2xl p-6 overflow-hidden group hover:bg-white/6 hover:border-white/18 transition-all duration-300">
            <div class="absolute -right-6 -bottom-6 w-28 h-28 rounded-full bg-amber-500/6 group-hover:bg-amber-500/10 transition-all duration-500"></div>
            <p class="text-[11px] uppercase tracking-widest font-bold text-amber-400/70 mb-1">Saldo Pendiente</p>
            <p class="text-3xl font-black text-amber-400 tabular-nums leading-none mb-1">{{ COP(saldos.saldo_pendiente) }}</p>
            <p class="text-xs text-white/40">Transacciones en proceso</p>
            <div class="mt-4 flex items-center gap-1.5">
              <div class="w-1.5 h-1.5 rounded-full bg-amber-400/70 animate-pulse"></div>
              <span class="text-[11px] text-amber-400/70 font-semibold">Aguardando confirmación</span>
            </div>
          </div>
        </div>

        <!-- ── DESGLOSE DE COMISIÓN ──────────────────────────────────── -->
        <div class="bg-white/3 border border-white/8 rounded-2xl p-6">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-9 h-9 rounded-xl bg-amber-500/15 border border-amber-500/25 flex items-center justify-center flex-shrink-0">
              <svg class="w-4.5 h-4.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"/>
              </svg>
            </div>
            <div>
              <h2 class="font-black text-white text-base">Desglose de Comisión</h2>
              <p class="text-xs text-white/40">Amazonia Viva – Modelo de comisión fija por ventas generadas</p>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-white/4 border border-white/8 rounded-xl p-4">
              <p class="text-[10px] uppercase tracking-widest text-white/35 font-bold mb-1">Tasa plataforma</p>
              <p class="text-2xl font-black text-amber-400">{{ saldos.comision_porcentaje }}%</p>
              <p class="text-xs text-white/35 mt-1">Sobre ventas brutas</p>
            </div>
            <div class="bg-white/4 border border-white/8 rounded-xl p-4">
              <p class="text-[10px] uppercase tracking-widest text-white/35 font-bold mb-1">Comisión cobrada</p>
              <p class="text-xl font-black text-red-400 tabular-nums">{{ COP(saldos.comision_total) }}</p>
              <p class="text-xs text-white/35 mt-1">Total descontado</p>
            </div>
            <div class="bg-white/4 border border-white/8 rounded-xl p-4">
              <p class="text-[10px] uppercase tracking-widest text-white/35 font-bold mb-1">Sobre completadas</p>
              <p class="text-xl font-black text-white/70 tabular-nums">{{ COP(saldos.desglose_comision.sobre_completado) }}</p>
              <p class="text-xs text-white/35 mt-1">Ventas liquidadas</p>
            </div>
            <div class="bg-white/4 border border-white/8 rounded-xl p-4">
              <p class="text-[10px] uppercase tracking-widest text-white/35 font-bold mb-1">Sobre pendientes</p>
              <p class="text-xl font-black text-white/70 tabular-nums">{{ COP(saldos.desglose_comision.sobre_pendiente) }}</p>
              <p class="text-xs text-white/35 mt-1">Por confirmar</p>
            </div>
          </div>
          <!-- Barra visual de comisión -->
          <div class="mt-5">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs text-white/40">Retención de plataforma</span>
              <span class="text-xs font-bold text-white/60">{{ saldos.comision_porcentaje }}% de {{ COP(saldos.bruto_total) }}</span>
            </div>
            <div class="h-2 bg-white/8 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full transition-all duration-1000"
                :style="{ width: saldos.comision_porcentaje + '%' }"
              ></div>
            </div>
            <p class="text-[10px] text-white/25 mt-2">La comisión cubre: procesamiento de pagos, mantenimiento de plataforma, soporte y marketing.</p>
          </div>
        </div>
      </template>

      <!-- ── TABLA DE MOVIMIENTOS ────────────────────────────────────── -->
      <div class="bg-white/3 border border-white/8 rounded-2xl overflow-hidden">

        <!-- Cabecera con filtros -->
        <div class="px-6 py-5 border-b border-white/8 flex flex-col sm:flex-row items-start sm:items-center gap-4 justify-between">
          <div>
            <h2 class="font-black text-white text-base">Historial de Movimientos</h2>
            <p class="text-xs text-white/35 mt-0.5">{{ paginacion.total_count }} transacciones encontradas</p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <!-- Filtro tipo -->
            <div class="flex items-center gap-1 bg-white/6 rounded-xl p-1">
              <button
                v-for="t in ['todos','ingreso','pendiente','reembolso']" :key="t"
                @click="filtroTipo = t; aplicarFiltros()"
                :class="[
                  'px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider transition-all',
                  filtroTipo === t ? 'bg-emerald-500 text-black' : 'text-white/40 hover:text-white/70'
                ]"
              >{{ { todos: 'Todos', ingreso: 'Ingresos', pendiente: 'Pendientes', reembolso: 'Reembolsos' }[t] }}</button>
            </div>

            <!-- Filtro fecha desde/hasta -->
            <input type="date" v-model="filtroDesde" @change="aplicarFiltros"
              class="bg-white/6 border border-white/10 text-white/70 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-emerald-400/50 transition-colors" />
            <input type="date" v-model="filtroHasta" @change="aplicarFiltros"
              class="bg-white/6 border border-white/10 text-white/70 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-emerald-400/50 transition-colors" />

            <!-- Exportar Reporte -->
            <div class="relative group/export">
              <button
                :disabled="exportando"
                class="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white/8 border border-white/12 text-white/70 hover:bg-white/12 hover:text-white text-xs font-bold transition-all disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
                {{ exportando ? 'Exportando…' : 'Exportar como' }}
              </button>
              
              <!-- Dropdown Formatos -->
              <div class="absolute right-0 top-full mt-2 w-48 bg-[#0d2114] border border-white/10 rounded-xl shadow-2xl opacity-0 invisible group-hover/export:opacity-100 group-hover/export:visible transition-all z-20 overflow-hidden">
                <button @click="exportarReporte('csv')" class="w-full text-left px-4 py-3 text-xs hover:bg-white/5 flex items-center gap-3 border-b border-white/5">
                  <span class="w-8 h-8 rounded bg-white/5 flex items-center justify-center text-[10px] font-black text-white/30">CSV</span>
                  <div>
                    <p class="text-white font-bold">CSV</p>
                    <p class="text-white/35 text-[9px]">Valores separados por coma</p>
                  </div>
                </button>
                <button @click="exportarReporte('excel')" class="w-full text-left px-4 py-3 text-xs hover:bg-white/5 flex items-center gap-3 border-b border-white/5">
                  <span class="w-8 h-8 rounded bg-emerald-500/10 flex items-center justify-center text-[10px] font-black text-emerald-400">XLS</span>
                  <div>
                    <p class="text-white font-bold font-white">Excel</p>
                    <p class="text-white/35 text-[9px]">Hoja de cálculo profesional</p>
                  </div>
                </button>
                <button @click="exportarReporte('pdf')" class="w-full text-left px-4 py-3 text-xs hover:bg-white/5 flex items-center gap-3">
                  <span class="w-8 h-8 rounded bg-red-500/10 flex items-center justify-center text-[10px] font-black text-red-400">PDF</span>
                  <div>
                    <p class="text-white font-bold">PDF</p>
                    <p class="text-white/35 text-[9px]">Documento financiero</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading skeleton movimientos -->
        <div v-if="cargandoMovs" class="p-6 space-y-3">
          <div v-for="i in 5" :key="i" class="h-14 bg-white/4 rounded-xl animate-pulse relative overflow-hidden">
            <div class="shimmer absolute inset-0 rounded-xl"></div>
          </div>
        </div>

        <!-- Tabla -->
        <div v-else-if="movimientos.length > 0" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-[10px] uppercase tracking-widest text-white/30 font-bold border-b border-white/6">
                <th class="text-left px-6 py-3">Referencia</th>
                <th class="text-left px-4 py-3">Fecha</th>
                <th class="text-left px-4 py-3">Concepto</th>
                <th class="text-center px-4 py-3">Tipo</th>
                <th class="text-center px-4 py-3">Estado</th>
                <th class="text-right px-4 py-3">Bruto</th>
                <th class="text-right px-4 py-3">Comisión</th>
                <th class="text-right px-6 py-3">Neto</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr
                v-for="m in movimientos"
                :key="m.id"
                class="hover:bg-white/3 transition-colors duration-150 group"
              >
                <!-- Ref -->
                <td class="px-6 py-3.5 font-mono text-xs text-white/50 group-hover:text-white/70 transition-colors">
                  {{ m.referencia }}
                </td>
                <!-- Fecha -->
                <td class="px-4 py-3.5 text-xs text-white/45 whitespace-nowrap">
                  {{ formatFecha(m.fecha) }}
                </td>
                <!-- Concepto -->
                <td class="px-4 py-3.5 text-xs text-white/70 max-w-[200px] truncate">{{ m.concepto }}</td>
                <!-- Tipo -->
                <td class="px-4 py-3.5 text-center">
                  <span :class="['inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-full border', tipoClases[m.tipo] || 'text-white/40 bg-white/5 border-white/10']">
                    <svg class="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" :d="tipoIcono[m.tipo] || 'M12 5v14'"/>
                    </svg>
                    {{ tipoLabel[m.tipo] || m.tipo }}
                  </span>
                </td>
                <!-- Estado -->
                <td class="px-4 py-3.5 text-center">
                  <span class="text-[10px] font-semibold text-white/50 bg-white/5 border border-white/8 px-2.5 py-1 rounded-full">{{ m.estado }}</span>
                </td>
                <!-- Bruto -->
                <td class="px-4 py-3.5 text-right font-mono text-xs text-white/60 tabular-nums">
                  {{ COP(m.monto_bruto) }}
                </td>
                <!-- Comisión -->
                <td class="px-4 py-3.5 text-right font-mono text-xs text-red-400/70 tabular-nums">
                  -{{ COP(m.comision) }}
                </td>
                <!-- Neto -->
                <td class="px-6 py-3.5 text-right font-mono font-black tabular-nums"
                  :class="m.tipo === 'ingreso' ? 'text-emerald-400' : m.tipo === 'reembolso' ? 'text-red-400' : 'text-amber-400'">
                  {{ COP(m.monto_neto) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty state -->
        <div v-else class="py-20 text-center">
          <div class="w-16 h-16 mx-auto rounded-2xl bg-white/5 border border-white/8 flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3z"/>
            </svg>
          </div>
          <p class="text-white/30 font-semibold">Sin movimientos para los filtros seleccionados</p>
        </div>

        <!-- Paginación -->
        <div v-if="paginacion.total_pages > 1" class="px-6 py-4 border-t border-white/6 flex items-center justify-between">
          <p class="text-xs text-white/30">
            Página {{ paginacion.page }} de {{ paginacion.total_pages }}
            · {{ paginacion.total_count }} registros
          </p>
          <div class="flex items-center gap-1">
            <button
              @click="irPagina(paginacion.page - 1)"
              :disabled="paginacion.page === 1"
              class="w-8 h-8 rounded-lg bg-white/6 border border-white/10 text-white/50 hover:bg-white/10 hover:text-white transition-all disabled:opacity-30 flex items-center justify-center"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
            </button>
            <button
              v-for="p in Math.min(paginacion.total_pages, 5)" :key="p"
              @click="irPagina(p)"
              :class="[
                'w-8 h-8 rounded-lg text-xs font-bold transition-all',
                paginacion.page === p ? 'bg-emerald-500 text-black' : 'bg-white/6 border border-white/10 text-white/50 hover:bg-white/10 hover:text-white'
              ]"
            >{{ p }}</button>
            <button
              @click="irPagina(paginacion.page + 1)"
              :disabled="paginacion.page === paginacion.total_pages"
              class="w-8 h-8 rounded-lg bg-white/6 border border-white/10 text-white/50 hover:bg-white/10 hover:text-white transition-all disabled:opacity-30 flex items-center justify-center"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>

      </div>
    </main>

    <!-- ══ MODAL DE RETIRO ════════════════════════════════════════════════ -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showRetiroModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/75 backdrop-blur-md" @click="cerrarRetiro"></div>

        <Transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0 scale-95 translate-y-4"
          enter-to-class="opacity-100 scale-100 translate-y-0"
        >
          <div v-if="showRetiroModal" class="relative bg-[#0d1f14] border border-white/10 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">

            <!-- Decoración superior -->
            <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-600"></div>

            <!-- Header -->
            <div class="px-7 pt-7 pb-5 border-b border-white/8 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/25 flex items-center justify-center">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3z"/>
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-black text-white">Solicitar Retiro</h3>
                  <p class="text-sm text-white/40">Disponible: <span class="text-emerald-400 font-bold">{{ COP(saldos?.saldo_disponible) }}</span></p>
                </div>
              </div>
              <button @click="cerrarRetiro" class="text-white/30 hover:text-white transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <!-- Estado de éxito -->
            <div v-if="retiroExito" class="px-7 py-10 text-center">
              <div class="w-16 h-16 mx-auto rounded-2xl bg-emerald-500/15 border border-emerald-500/25 flex items-center justify-center mb-5">
                <svg class="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <h4 class="text-xl font-black text-white mb-2">¡Retiro Solicitado!</h4>
              <p class="text-white/50 text-sm mb-4">{{ retiroExito.mensaje }}</p>
              <div class="bg-white/5 border border-white/8 rounded-2xl p-4 text-left space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-white/40">Referencia</span>
                  <span class="font-mono text-white/70 text-xs">{{ retiroExito.referencia }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-white/40">Monto</span>
                  <span class="font-black text-emerald-400">{{ COP(retiroExito.monto) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-white/40">Tiempo estimado</span>
                  <span class="text-white/70 text-xs">{{ retiroExito.estimado }}</span>
                </div>
              </div>
            </div>

            <!-- Formulario -->
            <div v-else class="px-7 py-6 space-y-5 max-h-[70vh] overflow-y-auto">

              <!-- Monto -->
              <div>
                <label class="text-[10px] uppercase tracking-widest font-bold text-white/40 block mb-2">Monto a Retirar (COP)</label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 font-bold text-sm">$</span>
                  <input
                    v-model="retiroMonto"
                    type="number"
                    placeholder="0"
                    min="10000"
                    :max="saldos?.saldo_disponible"
                    class="w-full bg-white/5 border border-white/10 rounded-xl pl-8 pr-4 py-3.5 text-white text-lg font-black tabular-nums focus:outline-none focus:border-emerald-400/50 transition-colors placeholder:text-white/15"
                  />
                </div>
                <p class="text-[10px] text-white/30 mt-1.5">Mínimo: $10,000 COP · Disponible: {{ COP(saldos?.saldo_disponible) }}</p>
              </div>

              <!-- Método de retiro -->
              <div>
                <label class="text-[10px] uppercase tracking-widest font-bold text-white/40 block mb-3">Método de Retiro</label>
                <div class="grid grid-cols-2 gap-2.5">
                  <button
                    v-for="m in saldos?.metodos_retiro" :key="m.id"
                    @click="retiroMetodo = m.id"
                    :class="[
                      'flex flex-col items-start gap-1 p-4 rounded-xl border transition-all text-left',
                      retiroMetodo === m.id
                        ? 'bg-emerald-500/15 border-emerald-400/50 shadow-lg shadow-emerald-500/10'
                        : 'bg-white/4 border-white/10 hover:border-white/20 hover:bg-white/6'
                    ]"
                  >
                    <div class="flex items-center gap-2">
                      <svg class="w-4 h-4 flex-shrink-0" :class="retiroMetodo === m.id ? 'text-emerald-400' : 'text-white/35'"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" :d="metodoIconos[m.id] || metodoIconos.pse"/>
                      </svg>
                      <span :class="['text-sm font-black', retiroMetodo === m.id ? 'text-emerald-300' : 'text-white/70']">{{ m.nombre }}</span>
                    </div>
                    <span class="text-[10px] text-white/35 pl-6">{{ m.descripcion }}</span>
                  </button>
                </div>
              </div>

              <!-- Datos adicionales: transferencia bancaria -->
              <div v-if="retiroMetodo === 'transferencia_bancaria'" class="space-y-3">
                <label class="text-[10px] uppercase tracking-widest font-bold text-white/40 block">Datos Bancarios</label>
                <input v-model="retiroDatos.banco" placeholder="Nombre del Banco" class="input-liq" />
                <div class="grid grid-cols-2 gap-3">
                  <input v-model="retiroDatos.cuenta" placeholder="Número de cuenta" class="input-liq" />
                  <select v-model="retiroDatos.tipo_cuenta" class="input-liq">
                    <option value="ahorros">Ahorros</option>
                    <option value="corriente">Corriente</option>
                  </select>
                </div>
                <input v-model="retiroDatos.titular" placeholder="Nombre del titular" class="input-liq" />
              </div>

              <!-- Datos: Nequi / Daviplata -->
              <div v-if="retiroMetodo === 'nequi' || retiroMetodo === 'daviplata'" class="space-y-3">
                <label class="text-[10px] uppercase tracking-widest font-bold text-white/40 block">Número de cuenta {{ retiroMetodo === 'nequi' ? 'Nequi' : 'Daviplata' }}</label>
                <input v-model="retiroDatos.numero" placeholder="+57 300 000 0000" class="input-liq" />
              </div>

              <!-- Error -->
              <div v-if="retiroError" class="flex items-center gap-2.5 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-sm text-red-300">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                {{ retiroError }}
              </div>
            </div>

            <!-- Footer del modal -->
            <div v-if="!retiroExito" class="px-7 pb-7 flex gap-3">
              <button @click="cerrarRetiro"
                class="flex-1 px-6 py-3.5 rounded-xl border border-white/10 text-white/50 font-bold hover:bg-white/5 hover:text-white transition-all text-sm">
                Cancelar
              </button>
              <button @click="confirmarRetiro" :disabled="retiroProcesando"
                class="flex-1 px-6 py-3.5 rounded-xl font-black text-sm transition-all flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-black disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20">
                <svg v-if="retiroProcesando" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ retiroProcesando ? 'Procesando…' : 'Confirmar Retiro' }}
              </button>
            </div>

          </div>
        </Transition>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.input-liq {
  width: 100%;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.875rem;
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.input-liq:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  border-color: rgba(52, 211, 153, 0.5); /* emerald-400/50 */
}
.input-liq::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

/* Shimmer loader */
.shimmer {
  background: linear-gradient(
    90deg,
    rgba(255,255,255,0) 0%,
    rgba(255,255,255,0.04) 50%,
    rgba(255,255,255,0) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s infinite;
}
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

/* Scrollbar */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 4px; }
</style>
