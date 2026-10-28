<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  error: { type: String, default: '' },
  ayuda: { type: String, default: '' },
  opcional: { type: Boolean, default: false },
  autocomplete: { type: String, default: 'off' },
  inputmode: { type: String, default: undefined },
  placeholder: { type: String, default: '' },
  maxlength: { type: Number, default: undefined },
  max: { type: String, default: undefined },
})

const emit = defineEmits(['update:modelValue', 'blur'])

const contrasenaVisible = ref(false)
const esContrasena = computed(() => props.type === 'password')
const tipoActual = computed(() => (esContrasena.value && contrasenaVisible.value ? 'text' : props.type))
const errorId = computed(() => `${props.id}-error`)
const ayudaId = computed(() => `${props.id}-ayuda`)
const descripcion = computed(() => [props.ayuda && ayudaId.value, props.error && errorId.value].filter(Boolean).join(' ') || undefined)
</script>

<template>
  <div class="flex flex-col">
    <label :for="id" class="mb-1.5 text-sm font-semibold text-gray-900">
      {{ label }}
      <span v-if="opcional" class="font-normal text-gray-600">(opcional)</span>
    </label>

    <div class="relative">
      <input
        :id="id"
        :name="id"
        :type="tipoActual"
        :value="modelValue"
        :autocomplete="autocomplete"
        :inputmode="inputmode"
        :placeholder="placeholder"
        :maxlength="maxlength"
        :max="max"
        :required="!opcional"
        :aria-invalid="error ? 'true' : undefined"
        :aria-describedby="descripcion"
        class="w-full rounded-xl border bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-500 outline-none transition-colors focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:border-teal-600"
        :class="[error ? 'border-red-600 bg-red-50' : 'border-gray-300 hover:border-gray-400', esContrasena ? 'pr-14' : '']"
        @input="emit('update:modelValue', $event.target.value)"
        @blur="emit('blur')"
      />
      <button
        v-if="esContrasena"
        type="button"
        class="absolute inset-y-0 right-0 flex w-12 items-center justify-center rounded-r-xl text-gray-600 outline-none hover:text-gray-900 focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-teal-600"
        :aria-label="contrasenaVisible ? 'Ocultar contraseña' : 'Mostrar contraseña'"
        :aria-pressed="contrasenaVisible"
        @click="contrasenaVisible = !contrasenaVisible"
      >
        <svg v-if="!contrasenaVisible" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
        <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
      </button>
    </div>

    <p v-if="ayuda" :id="ayudaId" class="mt-1.5 text-xs text-gray-600">{{ ayuda }}</p>
    <div :id="errorId" aria-live="polite">
      <p v-if="error" class="mt-1.5 flex items-start gap-1.5 text-sm font-medium text-red-700">
        <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <span>{{ error }}</span>
      </p>
    </div>
  </div>
</template>
