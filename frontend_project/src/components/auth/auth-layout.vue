<script setup>
import fondo from '@/assets/public/IMG_2820.JPG'

defineProps({
  titulo: { type: String, default: 'Tu próxima aventura empieza aquí.' },
  texto: { type: String, default: 'Explora destinos únicos, gestiona tu agencia o provee servicios turísticos en la región.' },
})
</script>

<template>
  <div class="flex min-h-screen items-stretch justify-center bg-slate-50 lg:items-center lg:p-6">
    <div class="flex w-full max-w-6xl overflow-hidden bg-white lg:rounded-3xl lg:shadow-[0_10px_40px_rgba(0,0,0,0.08)]">
      <aside class="relative hidden bg-gray-900 p-12 text-white lg:flex lg:w-5/12 lg:flex-col lg:justify-between">
        <img :src="fondo" alt="" loading="lazy" decoding="async" class="absolute inset-0 h-full w-full object-cover opacity-60" />
        <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/30 to-transparent"></div>

        <p class="relative z-10 text-xl font-bold tracking-tight">Amazonia<span class="text-teal-300">Viva</span></p>

        <div class="relative z-10">
          <p class="mb-4 text-4xl font-extrabold leading-tight tracking-tight">{{ titulo }}</p>
          <p class="max-w-sm text-base text-gray-100">{{ texto }}</p>
        </div>
      </aside>

      <section class="flex w-full flex-col justify-center p-6 sm:p-10 lg:w-7/12 lg:p-14">
        <slot />
      </section>
    </div>
  </div>
</template>
