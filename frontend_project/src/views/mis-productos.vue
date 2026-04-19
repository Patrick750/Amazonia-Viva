<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import axios from '@/api/axios'

// ── STATE ──────────────────────────────────────────────────
const orders   = ref([])
const loading  = ref(true)
const error    = ref(null)
const activeTab = ref('todos')
const now      = ref(Date.now())

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

// ── COMPUTED ───────────────────────────────────────────────
const tabCounts = computed(() => ({
  todos:      orders.value.length,
  proceso:    orders.value.filter(o => !TERMINAL.has(o.estado) && o.estado !== 'Entregado').length,
  entregados: orders.value.filter(o => o.estado === 'Entregado').length,
  anulados:   orders.value.filter(o => TERMINAL.has(o.estado) && o.estado !== 'Entregado').length,
}))

const filtered = computed(() => {
  if (activeTab.value === 'todos')      return orders.value
  if (activeTab.value === 'proceso')    return orders.value.filter(o => !TERMINAL.has(o.estado) && o.estado !== 'Entregado')
  if (activeTab.value === 'entregados') return orders.value.filter(o => o.estado === 'Entregado')
  if (activeTab.value === 'anulados')   return orders.value.filter(o => TERMINAL.has(o.estado) && o.estado !== 'Entregado')
  return orders.value
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
      <div v-else class="mp-grid">
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

          <!-- Entregado celebración -->
          <div v-if="order.estado === 'Entregado'" class="mp-delivered-banner">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            ¡Tu pedido fue entregado exitosamente!
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
.mp-delivered-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 18px 0;
  padding: 10px 14px;
  background: rgba(74,222,128,0.08);
  border: 1px solid rgba(74,222,128,0.2);
  border-radius: 9px;
  font-size: 12.5px;
  font-weight: 600;
  color: #4ade80;
}
.mp-delivered-banner svg { width: 16px; height: 16px; flex-shrink: 0; }

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
@media (max-width: 600px) {
  .mp-grid { grid-template-columns: 1fr; }
  .mp-page { padding: 20px 14px 50px; }
  .mp-title { font-size: 21px; }
}
</style>
