<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import axios from '@/api/axios'

// ── STATE ──────────────────────────────────────────────────
const orders   = ref([])
const loading  = ref(true)
const returning = ref(null) 
const canceling = ref(null) // Para manejar el estado de carga de una cancelación específica
const error    = ref(null)
const activeTab = ref('todos')
const now      = ref(Date.now())
const searchQuery = ref('')
const viewMode = ref('panales') // 'panales', 'filas', 'columnas'

// Modal de Cancelación
const cancelModal = ref({
  show: false,
  orderId: null,
  orderRef: null,
  productName: null
})

// Tick every minute to refresh countdowns
let ticker = null
onMounted(async () => {
  await fetchOrders()
  ticker = setInterval(() => { now.value = Date.now() }, 60_000)
})
onBeforeUnmount(() => clearInterval(ticker))

// ── CONSTANTS ──────────────────────────────────────────────
const STEPS = [
  { key: 'Pendiente de Empaque', label: 'Empaque',   icon: 'box',     color: '#fbbf24' },
  { key: 'Enviado',              label: 'Enviado',   icon: 'truck',   color: '#60a5fa' },
  { key: 'En Tránsito',         label: 'Tránsito',  icon: 'route',   color: '#a78bfa' },
  { key: 'Llegó',               label: 'Llegó',     icon: 'map-pin', color: '#2dd4bf' },
  { key: 'Entregado',           label: 'Entregado', icon: 'check',   color: '#4ade80' },
]
const STEP_KEYS = STEPS.map(s => s.key)

const TERMINAL = new Set(['Cancelado', 'Rechazado', 'Reembolsado', 'Devuelto'])

const TABS = [
  { id: 'todos',     label: 'Todos' },
  { id: 'proceso',   label: 'En Proceso' },
  { id: 'entregados',label: 'Entregados' },
  { id: 'anulados',  label: 'Anulados' },
]

const BADGE = {
  'Pendiente de Empaque': { cls: 'b-warn',    text: 'Empaque' },
  'Enviado':              { cls: 'b-info',    text: 'Enviado' },
  'En Tránsito':         { cls: 'b-purple',  text: 'En Tránsito' },
  'Llegó':               { cls: 'b-teal',    text: 'Llegó' },
  'Entregado':           { cls: 'b-success', text: 'Entregado' },
  'Cancelado':           { cls: 'b-danger',  text: 'Cancelado' },
  'Rechazado':           { cls: 'b-danger',  text: 'Rechazado' },
  'Reembolsado':         { cls: 'b-neutral', text: 'Reembolsado' },
  'Devuelto':            { cls: 'b-danger',  text: 'Devuelto' },
}

// ── FETCH ──────────────────────────────────────────────────
const fetchOrders = async () => {
  loading.value = true
  error.value   = null
  try {
    const { data } = await axios.get('/api/mis-productos/')
    orders.value = data
  } catch (e) {
    error.value = 'No se pudieron cargar tus pedidos. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}

const solicitarDevolucion = async (id_detalle) => {
  if (!confirm('¿Estás seguro de que deseas solicitar la devolución de este producto?')) return
  
  returning.value = id_detalle
  try {
    await axios.post('/api/mis-productos/devolucion/', { id_detalle })
    await fetchOrders()
  } catch (e) {
    console.error(e)
    alert(e.response?.data?.error || 'No se pudo procesar la devolución.')
  } finally {
    returning.value = null
  }
}

const openCancelModal = (order) => {
  cancelModal.value = {
    show: true,
    orderId: order.id_detalle,
    orderRef: order.id_transaccion,
    productName: order.product_nombre || order.producto_nombre
  }
}

const closeCancelModal = () => {
  cancelModal.value.show = false
}

const confirmarCancelacion = async () => {
  const { orderId } = cancelModal.value
  canceling.value = orderId
  closeCancelModal()
  
  try {
    await axios.post('/api/mis-productos/cancelar/', { id_detalle: orderId })
    await fetchOrders()
  } catch (e) {
    console.error(e)
    alert(e.response?.data?.error || 'No se pudo cancelar el pedido.')
  } finally {
    canceling.value = null
  }
}

// ── COMPUTED ───────────────────────────────────────────────
const tabCounts = computed(() => ({
  todos:      orders.value.length,
  proceso:    orders.value.filter(o => !TERMINAL.has(o.estado) && o.estado !== 'Entregado').length,
  entregados: orders.value.filter(o => o.estado === 'Entregado').length,
  anulados:   orders.value.filter(o => TERMINAL.has(o.estado) && o.estado !== 'Entregado').length,
}))

const filtered = computed(() => {
  let list = orders.value

  // 1. Filtro por Tab
  if (activeTab.value === 'proceso')    list = list.filter(o => !TERMINAL.has(o.estado) && o.estado !== 'Entregado')
  else if (activeTab.value === 'entregados') list = list.filter(o => o.estado === 'Entregado')
  else if (activeTab.value === 'anulados')   list = list.filter(o => TERMINAL.has(o.estado) && o.estado !== 'Entregado')

  // 2. Filtro por Búsqueda
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    list = list.filter(o => 
      o.producto_nombre?.toLowerCase().includes(q) || 
      String(o.id_transaccion || '').toLowerCase().includes(q)
    )
  }

  return list
})

// ── HELPERS ────────────────────────────────────────────────
const stepIdx = (estado) => STEP_KEYS.indexOf(estado)

const formatDate = (iso) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const formatHours = (h) => {
  if (h === null || h === undefined) return null
  if (h < 1) return `${Math.round(h * 60)} min`
  const d = Math.floor(h / 24)
  const rem = Math.round(h % 24)
  if (d > 0) return `${d}d ${rem}h`
  return `${h}h`
}

const badge = (estado) => BADGE[estado] || { cls: 'b-neutral', text: estado }

const formatCOP = (val) => {
  const n = parseFloat(val)
  return isNaN(n) ? '—' : `$${n.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`
}
</script>

<template>
  <div class="mp-page">
    <div class="mp-container">

      <!-- ── PAGE HEADER ──────────────────────────────────── -->
      <div class="mp-page-header">
        <div>
          <h1 class="mp-title">Mis Productos</h1>
          <p class="mp-subtitle">Seguimiento en tiempo real de tus pedidos</p>
        </div>
        <button class="mp-refresh-btn" @click="fetchOrders" :disabled="loading" title="Actualizar">
          <svg :class="['mp-refresh-icon', loading ? 'spinning' : '']" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M1 4v6h6M23 20v-6h-6"/>
            <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4-4.64 4.36A9 9 0 013.51 15"/>
          </svg>
          Actualizar
        </button>
      </div>
      
      <!-- ── TOOLBAR (Search + View Toggle) ──────────────── -->
      <div class="mp-toolbar">
        <div class="mp-search-wrapper">
          <svg class="mp-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Buscar por producto o referencia..." 
            class="mp-search-input-field"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="mp-search-clear">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="mp-view-toggles">
          <button 
            class="mp-view-btn" 
            :class="{ 'is-active': viewMode === 'filas' }"
            @click="viewMode = 'filas'"
            title="Vista de Filas"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
          </button>
          <button 
            class="mp-view-btn" 
            :class="{ 'is-active': viewMode === 'columnas' }"
            @click="viewMode = 'columnas'"
            title="Vista de Columnas"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          </button>
          <button 
            class="mp-view-btn" 
            :class="{ 'is-active': viewMode === 'panales' }"
            @click="viewMode = 'panales'"
            title="Vista de Panales"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          </button>
        </div>
      </div>

      <!-- ── TABS ─────────────────────────────────────────── -->
      <div class="mp-tabs" role="tablist">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          :id="`tab-${tab.id}`"
          role="tab"
          class="mp-tab"
          :class="{ 'is-active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
          <span class="mp-tab-count">{{ tabCounts[tab.id] }}</span>
        </button>
      </div>

      <!-- ── LOADING ──────────────────────────────────────── -->
      <div v-if="loading" class="mp-loading">
        <div class="mp-spinner"></div>
        <p>Cargando tus pedidos...</p>
      </div>

      <!-- ── ERROR ────────────────────────────────────────── -->
      <div v-else-if="error" class="mp-error-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/>
        </svg>
        <p>{{ error }}</p>
        <button class="mp-retry-btn" @click="fetchOrders">Reintentar</button>
      </div>

      <!-- ── EMPTY ─────────────────────────────────────────── -->
      <div v-else-if="filtered.length === 0" class="mp-empty">
        <div class="mp-empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
        </div>
        <p class="mp-empty-title">Sin pedidos en esta categoría</p>
        <p class="mp-empty-sub">Cuando compres productos, aparecerán aquí con seguimiento en tiempo real.</p>
      </div>

      <!-- ── ORDER CARDS GRID ──────────────────────────────── -->
      <div v-else :class="['mp-grid', `view-${viewMode}`]">
        <article
          v-for="order in filtered"
          :key="order.id_detalle"
          class="mp-card"
          :class="{ 'is-terminal': order.es_terminal, 'is-delivered': order.estado === 'Entregado' }"
        >
          <!-- Card Header -->
          <div class="mp-card-header">
            <div class="mp-product-thumb">
              <img v-if="order.producto_imagen" :src="order.producto_imagen" :alt="order.producto_nombre" />
              <span v-else class="mp-thumb-fallback">{{ (order.producto_nombre || 'P').charAt(0) }}</span>
            </div>
            <div class="mp-product-meta">
              <p class="mp-product-name">{{ order.producto_nombre }}</p>
              <p class="mp-product-ref">{{ order.id_transaccion }}</p>
            </div>
            <span class="mp-badge" :class="badge(order.estado).cls">
              {{ badge(order.estado).text }}
            </span>
          </div>

          <!-- Progress Stepper (solo pedidos activos) -->
          <div v-if="!order.es_terminal" class="mp-stepper">
            <div
              v-for="(step, i) in STEPS"
              :key="step.key"
              class="mp-step"
              :class="{
                'is-done':   i < stepIdx(order.estado) || order.estado === 'Entregado',
                'is-active': i === stepIdx(order.estado) && order.estado !== 'Entregado',
                'is-future': i > stepIdx(order.estado)
              }"
            >
              <div class="mp-step-circle" :style="i <= stepIdx(order.estado) ? { borderColor: step.color, background: i < stepIdx(order.estado) || order.estado === 'Entregado' ? step.color : 'transparent' } : {}">
                <!-- Done: checkmark -->
                <svg v-if="i < stepIdx(order.estado) || order.estado === 'Entregado'" viewBox="0 0 24 24" fill="none" stroke="#050e0a" stroke-width="3" stroke-linecap="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <!-- Active: pulsing dot -->
                <span v-else-if="i === stepIdx(order.estado)" class="mp-step-dot" :style="{ background: step.color }"></span>
                <!-- Future: number -->
                <span v-else class="mp-step-num">{{ i + 1 }}</span>
              </div>
              <span class="mp-step-label">{{ step.label }}</span>
              <!-- Connector line -->
              <div v-if="i < STEPS.length - 1" class="mp-step-line" :class="{ 'is-filled': i < stepIdx(order.estado) || order.estado === 'Entregado' }"></div>
            </div>
          </div>

          <!-- Anulado / Terminal banner -->
          <div v-else class="mp-terminal-banner" :class="order.estado === 'Reembolsado' ? 'tb-neutral' : 'tb-danger'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/>
            </svg>
            Pedido {{ order.estado }}
          </div>

          <!-- Time estimate (solo activos no terminados) -->
          <div v-if="!order.es_terminal && order.proximo_estado && order.estado !== 'Entregado'" class="mp-eta">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>
              Llegará a <strong>{{ order.proximo_estado }}</strong> en aprox.
              <strong class="eta-time">{{ formatHours(order.horas_para_proximo) }}</strong>
            </span>
          </div>

          <!-- Acción de Cancelación (Solo en Empaque) -->
          <div v-if="order.estado === 'Pendiente de Empaque'" class="mp-cancel-container">
            <button 
              class="mp-cancel-btn"
              @click="openCancelModal(order)"
              :disabled="canceling === order.id_detalle"
            >
               <svg v-if="canceling === order.id_detalle" class="spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <circle cx="12" cy="12" r="10" opacity="0.2"/><path d="M12 2a10 10 0 0110 10" stroke-linecap="round"/>
              </svg>
              <span v-else>Cancelar Pedido</span>
            </button>
            <p class="mp-cancel-note">Puedes cancelar sin costo antes del despacho</p>
          </div>

          <!-- Entregado celebración -->
          <div v-if="order.estado === 'Entregado'" class="mp-delivered-container">
            <div class="mp-delivered-banner">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span>¡Tu pedido fue entregado exitosamente!</span>
            </div>
            <button 
              class="mp-return-btn" 
              @click="solicitarDevolucion(order.id_detalle)"
              :disabled="returning === order.id_detalle"
            >
              <svg v-if="returning === order.id_detalle" class="spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <circle cx="12" cy="12" r="10" opacity="0.2"/><path d="M12 2a10 10 0 0110 10" stroke-linecap="round"/>
              </svg>
              <span v-else>Solicitar Devolución</span>
            </button>
          </div>

          <!-- Card Footer -->
          <div class="mp-card-footer">
            <div class="mp-footer-row">
              <span class="mp-footer-label">Fecha</span>
              <span class="mp-footer-val">{{ formatDate(order.fecha_pedido) }}</span>
            </div>
            <div class="mp-footer-row">
              <span class="mp-footer-label">Cantidad</span>
              <span class="mp-footer-val">×{{ order.cantidad }}</span>
            </div>
            <div class="mp-footer-row">
              <span class="mp-footer-label">Total</span>
              <span class="mp-footer-val mp-footer-price">{{ formatCOP(order.precio_total) }}</span>
            </div>
          </div>

        </article>
      </div>
    </div>

    <!-- ── CUSTOM CANCEL MODAL ──────────────────────────────── -->
    <Teleport to="body">
      <transition name="modal">
        <div v-if="cancelModal.show" class="mp-modal-overlay" @click.self="closeCancelModal">
          <div class="mp-modal">
            <div class="mp-modal-header">
              <div class="mp-modal-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0zM12 9v4m0 4h.01"/>
                </svg>
              </div>
              <h3>Confirmar Cancelación</h3>
            </div>
            
            <div class="mp-modal-body">
              <p>¿Estás seguro de que deseas cancelar el pedido <strong>{{ cancelModal.orderRef }}</strong>?</p>
              <p class="mp-modal-product">{{ cancelModal.productName }}</p>
              <div class="mp-modal-info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                <span>El stock se devolverá automáticamente al inventario.</span>
              </div>
            </div>

            <div class="mp-modal-footer">
              <button class="mp-mt-btn btn-secondary" @click="closeCancelModal">No, mantener pedido</button>
              <button class="mp-mt-btn btn-danger" @click="confirmarCancelacion">Sí, cancelar pedido</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── ROOT ─────────────────────────────────────────────── */
.mp-page {
  min-height: 100vh;
  background: #07100d;
  font-family: 'Inter', system-ui, sans-serif;
  color: #dff0e8;
  font-size: 14px;
  padding: 32px 20px 60px;
}
.mp-container {
  max-width: 1080px;
  margin: 0 auto;
}

/* ── PAGE HEADER ──────────────────────────────────────── */
.mp-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 16px;
  flex-wrap: wrap;
}
.mp-title {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #f1faf4;
  margin-bottom: 4px;
}
.mp-subtitle {
  font-size: 13px;
  color: #5a8070;
  font-weight: 400;
}
.mp-refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 16px;
  border-radius: 9px;
  background: rgba(0,214,143,0.08);
  border: 1px solid rgba(0,214,143,0.2);
  color: #00d68f;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.mp-refresh-btn:hover { background: rgba(0,214,143,0.14); }
.mp-refresh-btn:disabled { opacity: 0.5; pointer-events: none; }
.mp-refresh-icon { width: 14px; height: 14px; }
.spinning { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── TABS ─────────────────────────────────────────────── */
.mp-tabs {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid #1d2e25;
  margin-bottom: 28px;
  overflow-x: auto;
  scrollbar-width: none;
}
.mp-tabs::-webkit-scrollbar { display: none; }
.mp-tab {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 11px 18px 10px;
  font-size: 12.5px;
  font-weight: 500;
  color: #5a8070;
  background: none;
  border: none;
  border-bottom: 2.5px solid transparent;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  transition: color 0.14s, border-color 0.14s;
}
.mp-tab:hover { color: #dff0e8; }
.mp-tab.is-active { color: #00d68f; border-bottom-color: #00d68f; font-weight: 700; }
.mp-tab-count {
  font-size: 10px;
  font-weight: 800;
  background: #1d2e25;
  border-radius: 10px;
  padding: 1px 6px;
  min-width: 18px;
  text-align: center;
  transition: background 0.14s;
}
.mp-tab.is-active .mp-tab-count { background: rgba(0,214,143,0.15); color: #00d68f; }

/* ── LOADING / ERROR / EMPTY ──────────────────────────── */
.mp-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 20px;
  color: #5a8070;
}
.mp-spinner {
  width: 38px; height: 38px;
  border: 3px solid #1d2e25;
  border-top-color: #00d68f;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}
.mp-error-state, .mp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 80px 20px;
  text-align: center;
}
.mp-error-state svg { width: 42px; height: 42px; color: #f87171; }
.mp-retry-btn {
  padding: 8px 20px;
  background: rgba(248,113,113,0.1);
  border: 1px solid rgba(248,113,113,0.3);
  border-radius: 8px;
  color: #f87171;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.mp-empty-icon {
  width: 60px; height: 60px;
  background: #0d1512;
  border: 1px solid #1d2e25;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  color: #3e5a4a;
}
.mp-empty-icon svg { width: 28px; height: 28px; }
.mp-empty-title { font-size: 15px; font-weight: 700; color: #7a9b87; }
.mp-empty-sub { font-size: 12.5px; color: #3e5a4a; max-width: 320px; }

/* ── GRID ─────────────────────────────────────────────── */
.mp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

/* ── CARD ─────────────────────────────────────────────── */
.mp-card {
  background: #0d1512;
  border: 1px solid #1d2e25;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.mp-card:hover { border-color: #253c2e; box-shadow: 0 6px 28px rgba(0,0,0,0.3); }
.mp-card.is-delivered { border-color: rgba(74,222,128,0.22); }
.mp-card.is-terminal  { opacity: 0.75; }

/* Card header */
.mp-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid #1d2e25;
}
.mp-product-thumb {
  width: 44px; height: 44px;
  border-radius: 10px;
  background: #131c18;
  border: 1px solid #1d2e25;
  overflow: hidden;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.mp-product-thumb img { width: 100%; height: 100%; object-fit: cover; }
.mp-thumb-fallback { font-size: 18px; font-weight: 800; color: #00d68f; }
.mp-product-meta { flex: 1; min-width: 0; }
.mp-product-name {
  font-size: 13.5px; font-weight: 700; color: #dff0e8;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mp-product-ref { font-size: 11px; color: #3e5a4a; font-weight: 500; margin-top: 2px; }

/* Badges */
.mp-badge {
  font-size: 10.5px; font-weight: 700;
  padding: 3px 9px; border-radius: 20px;
  white-space: nowrap; flex-shrink: 0;
}
.b-warn    { background: rgba(251,191,36,0.12); color: #fbbf24; }
.b-info    { background: rgba(96,165,250,0.12);  color: #60a5fa; }
.b-purple  { background: rgba(167,139,250,0.12); color: #a78bfa; }
.b-teal    { background: rgba(45,212,191,0.12); color: #2dd4bf; }
.b-success { background: rgba(74,222,128,0.12);  color: #4ade80; }
.b-danger  { background: rgba(248,113,113,0.12); color: #f87171; }
.b-neutral { background: rgba(155,168,160,0.10); color: #9ba8a0; }

/* ── STEPPER ──────────────────────────────────────────── */
.mp-stepper {
  display: flex;
  align-items: flex-start;
  padding: 20px 18px 14px;
  position: relative;
  gap: 0;
}
.mp-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}
.mp-step-circle {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 2px solid #1d2e25;
  background: #0d1512;
  display: flex; align-items: center; justify-content: center;
  position: relative;
  z-index: 1;
  transition: all 0.2s;
}
.mp-step-circle svg { width: 14px; height: 14px; }
.mp-step-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  animation: pulse-dot 1.4s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(1.35); }
}
.mp-step-num { font-size: 10px; font-weight: 700; color: #3e5a4a; }
.mp-step-label {
  font-size: 9.5px;
  font-weight: 600;
  color: #3e5a4a;
  margin-top: 5px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  transition: color 0.2s;
}
.mp-step.is-done   .mp-step-label { color: #4ade80; }
.mp-step.is-active .mp-step-label { color: #dff0e8; }

/* Connector line */
.mp-step-line {
  position: absolute;
  top: 13px;
  left: calc(50% + 14px);
  right: calc(-50% + 14px);
  height: 2px;
  background: #1d2e25;
  z-index: 0;
  transition: background 0.25s;
}
.mp-step-line.is-filled { background: #4ade80; }

/* ── TERMINAL BANNER ──────────────────────────────────── */
.mp-terminal-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 14px 18px 0;
  padding: 10px 14px;
  border-radius: 9px;
  font-size: 12.5px;
  font-weight: 600;
}
.mp-terminal-banner svg { width: 16px; height: 16px; flex-shrink: 0; }
.tb-danger  { background: rgba(248,113,113,0.1); color: #f87171; border: 1px solid rgba(248,113,113,0.2); }
.tb-neutral { background: rgba(155,168,160,0.08); color: #9ba8a0; border: 1px solid rgba(155,168,160,0.18); }

/* ── ETA ──────────────────────────────────────────────── */
.mp-eta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 18px 0;
  padding: 9px 13px;
  background: rgba(96,165,250,0.07);
  border: 1px solid rgba(96,165,250,0.15);
  border-radius: 9px;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
}
.mp-eta svg { width: 14px; height: 14px; flex-shrink: 0; color: #60a5fa; }
.eta-time { color: #60a5fa; }

/* ── DELIVERED BANNER ─────────────────────────────────── */
.mp-delivered-container {
  margin: 12px 18px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mp-delivered-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(74,222,128,0.08);
  border: 1px solid rgba(74,222,128,0.2);
  border-radius: 9px;
  font-size: 12.5px;
  font-weight: 600;
  color: #4ade80;
}
.mp-delivered-banner svg { width: 16px; height: 16px; flex-shrink: 0; }

.mp-return-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px;
  background: rgba(248,113,113,0.06);
  border: 1px solid rgba(248,113,113,0.15);
  border-radius: 9px;
  color: #f87171;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.mp-return-btn:hover:not(:disabled) {
  background: rgba(248,113,113,0.12);
  border-color: rgba(248,113,113,0.3);
}
.mp-return-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.mp-return-btn svg { width: 14px; height: 14px; }

/* ── CANCEL BANNER ────────────────────────────────────── */
.mp-cancel-container {
  margin: 12px 18px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.mp-cancel-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px;
  background: rgba(248,113,113,0.06);
  border: 1px solid rgba(248,113,113,0.15);
  border-radius: 9px;
  color: #f87171;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.mp-cancel-btn:hover:not(:disabled) {
  background: rgba(248,113,113,0.1);
  border-color: rgba(248,113,113,0.3);
}
.mp-cancel-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.mp-cancel-note {
  font-size: 10px;
  color: #3e5a4a;
  text-align: center;
}

/* ── CARD FOOTER ──────────────────────────────────────── */
.mp-card-footer {
  margin-top: auto;
  padding: 14px 18px;
  border-top: 1px solid #1d2e25;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.mp-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mp-footer-label { font-size: 11.5px; color: #3e5a4a; font-weight: 500; }
.mp-footer-val   { font-size: 12.5px; color: #7a9b87; font-weight: 600; }
.mp-footer-price { color: #00d68f; font-weight: 700; font-size: 13.5px; }

/* ── RESPONSIVE ───────────────────────────────────────── */
/* ── MODAL ─────────────────────────────────────────────── */
.mp-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 14, 10, 0.85);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 10000;
}
.mp-modal {
  background: #0d1512;
  border: 1px solid #1d2e25;
  width: 100%;
  max-width: 440px;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  animation: modalSlide 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes modalSlide {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.mp-modal-header {
  padding: 24px 24px 10px;
  text-align: center;
}
.mp-modal-icon {
  width: 56px;
  height: 56px;
  background: rgba(248, 113, 113, 0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #f87171;
}
.mp-modal-icon svg { width: 28px; height: 28px; }
.mp-modal-header h3 {
  font-size: 20px;
  font-weight: 800;
  color: #f1faf4;
}

.mp-modal-body {
  padding: 0 24px 24px;
  text-align: center;
}
.mp-modal-body p {
  font-size: 14px;
  color: #7a9b87;
  line-height: 1.6;
}
.mp-modal-product {
  margin: 8px 0 16px;
  font-weight: 700;
  color: #dff0e8;
}
.mp-modal-info {
  background: rgba(0, 214, 143, 0.05);
  border: 1px solid rgba(0, 214, 143, 0.1);
  padding: 10px 14px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  text-align: left;
  font-size: 12px;
  color: #00d68f;
}
.mp-modal-info svg { width: 16px; height: 16px; flex-shrink: 0; }

.mp-modal-footer {
  background: #0a120f;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.mp-mt-btn {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.btn-danger {
  background: #f87171;
  color: #050e0a;
  border: none;
}
.btn-danger:hover { background: #ef4444; }
.btn-secondary {
  background: transparent;
  color: #5a8070;
  border: 1px solid #1d2e25;
}
.btn-secondary:hover { background: #1d2e25; color: #dff0e8; }

/* Transitions */
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

@media (max-width: 600px) {
  .mp-grid { grid-template-columns: 1fr; gap: 12px; }
  .mp-page { padding: 16px 12px 40px; }
  .mp-title { font-size: 21px; }
  .mp-toolbar { flex-direction: column; align-items: stretch; gap: 12px; }
  .mp-search-wrapper { min-width: 0; }
  .mp-view-toggles { justify-content: center; }
  .mp-tab { padding: 10px 14px; font-size: 11.5px; }
  
  /* Compact cards for mobile in Columnas view */
  .mp-grid.view-columnas { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .mp-grid.view-columnas .mp-card-header { padding: 10px; gap: 8px; }
  .mp-grid.view-columnas .mp-product-thumb { width: 32px; height: 32px; }
  .mp-grid.view-columnas .mp-product-name { font-size: 11px; }
  .mp-grid.view-columnas .mp-badge { font-size: 9px; padding: 2px 6px; }
  .mp-grid.view-columnas .mp-stepper { display: none; } /* Hide stepper in very compact mobile view */
  .mp-grid.view-columnas .mp-card-footer { padding: 10px; }
}

@media (max-width: 400px) {
  .mp-grid.view-columnas { grid-template-columns: 1fr; }
}

/* ── TOOLBAR (Search + View Toggle) ──────────────── */
.mp-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.mp-search-wrapper {
  position: relative;
  flex: 1;
  min-width: 280px;
}
.mp-search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #3e5a4a;
  pointer-events: none;
}
.mp-search-input-field {
  width: 100%;
  background: #0d1512;
  border: 1px solid #1d2e25;
  border-radius: 12px;
  padding: 11px 40px;
  color: #dff0e8;
  font-family: inherit;
  font-size: 13.5px;
  transition: all 0.2s;
}
.mp-search-input-field:focus {
  outline: none;
  border-color: #00d68f;
  box-shadow: 0 0 0 3px rgba(0, 214, 143, 0.1);
  background: #131c18;
}
.mp-search-clear {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #3e5a4a;
  cursor: pointer;
  padding: 4px;
  display: flex;
  transition: color 0.2s;
}
.mp-search-clear:hover { color: #f87171; }
.mp-search-clear svg { width: 14px; height: 14px; }

.mp-view-toggles {
  display: flex;
  background: #0d1512;
  border: 1px solid #1d2e25;
  padding: 4px;
  border-radius: 12px;
  gap: 4px;
}
.mp-view-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: none;
  background: none;
  color: #3e5a4a;
  cursor: pointer;
  transition: all 0.2s;
}
.mp-view-btn svg { width: 18px; height: 18px; }
.mp-view-btn:hover { color: #7a9b87; background: rgba(255,255,255,0.03); }
.mp-view-btn.is-active {
  background: #1d2e25;
  color: #00d68f;
}

/* ── VIEW MODES ────────────────────────────────────── */

/* Columns View (Denser Grid) */
.mp-grid.view-columnas {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.mp-grid.view-columnas .mp-card-header { padding: 12px 14px; }
.mp-grid.view-columnas .mp-stepper { padding: 14px 14px 10px; }
.mp-grid.view-columnas .mp-step-label { font-size: 8px; }
.mp-grid.view-columnas .mp-step-circle { width: 22px; height: 22px; }
.mp-grid.view-columnas .mp-step-line { top: 10px; left: calc(50% + 11px); right: calc(-50% + 11px); }
.mp-grid.view-columnas .mp-eta, 
.mp-grid.view-columnas .mp-terminal-banner, 
.mp-grid.view-columnas .mp-cancel-container, 
.mp-grid.view-columnas .mp-delivered-container { margin: 10px 14px 0; }
.mp-grid.view-columnas .mp-card-footer { padding: 10px 14px; }

/* Rows View (List Style) */
@media (min-width: 900px) {
  .mp-grid.view-filas {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .mp-grid.view-filas .mp-card {
    flex-direction: row;
    align-items: center;
    padding: 10px 20px;
    gap: 24px;
    min-height: 80px;
  }
  .mp-grid.view-filas .mp-card-header {
    border-bottom: none;
    padding: 0;
    width: 200px;
    flex-shrink: 0;
  }
  .mp-grid.view-filas .mp-stepper {
    padding: 0;
    flex: 1.5;
    margin: 0;
  }
  .mp-grid.view-filas .mp-eta,
  .mp-grid.view-filas .mp-terminal-banner {
    margin: 0;
    flex: 1;
    padding: 6px 10px;
    font-size: 11px;
  }
  .mp-grid.view-filas .mp-card-footer {
    border-top: none;
    padding: 0;
    width: 140px;
    flex-direction: column;
    gap: 2px;
  }
  .mp-grid.view-filas .mp-cancel-container,
  .mp-grid.view-filas .mp-delivered-container {
     margin: 0;
     width: 140px;
  }
  .mp-grid.view-filas .mp-step-label { display: none; }
  .mp-grid.view-filas .mp-step-line { top: 13px; }
  .mp-grid.view-filas .mp-footer-row { justify-content: flex-end; gap: 8px; }
  .mp-grid.view-filas .mp-footer-label { display: none; }
}

/* Panales View (Default Grid) - Already implemented as .mp-grid */
</style>
