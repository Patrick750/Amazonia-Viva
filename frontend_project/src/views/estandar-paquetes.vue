<script setup>
import { onMounted, ref } from 'vue'
import clienteAxios from '@/api/axios'

const cargando = ref(true)
const error = ref('')
const estandar = ref(null)

onMounted(async () => {
  try {
    const { data } = await clienteAxios.get('api/estandar-paquetes/')
    estandar.value = data
  } catch {
    error.value = 'No fue posible cargar la referencia del estándar. Intenta nuevamente.'
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#08150d] text-white px-5 py-8 sm:px-8 lg:px-12">
    <main class="mx-auto max-w-6xl">
      <button
        type="button"
        @click="$router.back()"
        class="mb-8 inline-flex min-h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 text-sm font-semibold text-white/70 transition hover:border-emerald-400/40 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-400"
      >
        <span aria-hidden="true">←</span> Volver
      </button>

      <div v-if="cargando" class="rounded-3xl border border-white/10 bg-white/5 p-10 text-white/60">
        Cargando información del estándar…
      </div>
      <div v-else-if="error" role="alert" class="rounded-3xl border border-rose-400/30 bg-rose-400/10 p-6 text-rose-100">
        {{ error }}
      </div>

      <template v-else-if="estandar">
        <header class="relative overflow-hidden rounded-[2rem] border border-emerald-300/20 bg-gradient-to-br from-emerald-700 to-[#12351f] p-7 shadow-2xl sm:p-10">
          <div class="relative z-10 max-w-3xl">
            <p class="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-emerald-100/70">MEJ-003 · Referencia técnica</p>
            <h1 class="text-3xl font-black tracking-tight sm:text-5xl">{{ estandar.nombre }}</h1>
            <p class="mt-5 max-w-2xl text-base leading-7 text-emerald-50/80">{{ estandar.proposito }}</p>
            <p class="mt-6 inline-flex rounded-full bg-black/20 px-4 py-2 text-xs font-semibold text-emerald-100">
              Revisión de fuentes: {{ estandar.version }}
            </p>
          </div>
        </header>

        <section class="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <article class="rounded-3xl border border-white/10 bg-white/[0.04] p-6 sm:p-8">
            <h2 class="text-xl font-black">Cómo aplica en el registro</h2>
            <ul class="mt-5 space-y-4">
              <li v-for="principio in estandar.principios" :key="principio" class="flex gap-3 text-sm leading-6 text-white/70">
                <span class="mt-1 flex h-5 w-5 flex-none items-center justify-center rounded-full bg-emerald-400/15 text-xs text-emerald-300" aria-hidden="true">✓</span>
                {{ principio }}
              </li>
            </ul>
          </article>

          <aside class="rounded-3xl border border-amber-300/20 bg-amber-300/[0.07] p-6 sm:p-8">
            <p class="text-xs font-bold uppercase tracking-[0.15em] text-amber-200">Alcance de la plataforma</p>
            <h2 class="mt-3 text-xl font-black">La ficha informa y conserva evidencia</h2>
            <p class="mt-4 text-sm leading-6 text-amber-50/70">
              Registrar o publicar un tour en Amazonía Viva no certifica al operador. La agencia debe mantener vigente la certificación exigible y verificar el organismo emisor en el directorio oficial de ONAC.
            </p>
          </aside>
        </section>

        <section class="mt-8">
          <div class="mb-5">
            <p class="text-xs font-bold uppercase tracking-[0.15em] text-emerald-400">Clasificación por actividad</p>
            <h2 class="mt-2 text-2xl font-black">Cada actividad conserva su propia escala</h2>
          </div>
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <article v-for="actividad in estandar.actividades_reguladas" :key="actividad.id" class="rounded-2xl border border-white/10 bg-[#102219] p-5">
              <div class="flex items-start justify-between gap-3">
                <h3 class="font-bold leading-6">{{ actividad.nombre }}</h3>
                <span class="flex-none rounded-full bg-emerald-400/10 px-3 py-1 text-[11px] font-bold text-emerald-300">{{ actividad.norma_tecnica }}</span>
              </div>
              <p class="mt-3 text-sm leading-6 text-white/55">{{ actividad.sistema_dificultad }}</p>
              <div v-if="actividad.opciones_dificultad?.length" class="mt-4 flex flex-wrap gap-2">
                <span v-for="opcion in actividad.opciones_dificultad" :key="opcion.value" class="rounded-lg border border-white/10 bg-black/20 px-2.5 py-1.5 text-xs text-white/60">
                  {{ opcion.label }}
                </span>
              </div>
              <p v-else class="mt-4 text-xs leading-5 text-white/40">Se documenta mediante una descripción técnica del recorrido y sus condiciones.</p>
            </article>
          </div>
        </section>

        <section class="mt-10 pb-10">
          <p class="text-xs font-bold uppercase tracking-[0.15em] text-emerald-400">Trazabilidad</p>
          <h2 class="mt-2 text-2xl font-black">Fuentes utilizadas</h2>
          <div class="mt-5 overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03]">
            <article v-for="(fuente, index) in estandar.fuentes" :key="fuente.titulo" class="p-6 sm:flex sm:items-start sm:justify-between sm:gap-8" :class="index ? 'border-t border-white/10' : ''">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <h3 class="font-bold">{{ fuente.titulo }}</h3>
                  <span class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide" :class="fuente.verificada ? 'bg-emerald-400/10 text-emerald-300' : 'bg-amber-300/10 text-amber-200'">
                    {{ fuente.verificada ? 'Fuente oficial verificada' : 'Referencia funcional' }}
                  </span>
                </div>
                <p class="mt-2 text-sm text-white/45">{{ fuente.entidad }}</p>
                <p class="mt-3 max-w-3xl text-sm leading-6 text-white/65">{{ fuente.alcance }}</p>
              </div>
              <a v-if="fuente.url" :href="fuente.url" target="_blank" rel="noopener noreferrer" class="mt-4 inline-flex min-h-11 flex-none items-center rounded-xl border border-white/10 px-4 text-sm font-semibold text-emerald-300 transition hover:border-emerald-300/40 hover:bg-emerald-300/5 focus:outline-none focus:ring-2 focus:ring-emerald-400 sm:mt-0">
                Consultar fuente <span class="ml-2" aria-hidden="true">↗</span>
              </a>
            </article>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>
