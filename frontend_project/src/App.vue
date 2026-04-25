<script setup>
import { onMounted } from 'vue';
import Header from './components/header.vue';
import Footer from './components/footer.vue';
import Notificacion from './components/notificacion.vue';

onMounted(() => {
  // Deshabilitar click derecho para evitar "Inspeccionar"
  document.addEventListener('contextmenu', (e) => e.preventDefault());

  // Deshabilitar teclas de acceso a herramientas de desarrollador
  document.addEventListener('keydown', (e) => {
    // F12
    if (e.key === 'F12') e.preventDefault();
    
    // Ctrl+Shift+I / J / C (Inspeccionar, Consola, Selector)
    if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j' || e.key === 'C' || e.key === 'c')) {
      e.preventDefault();
    }
    
    // Ctrl+U (Ver código fuente)
    if (e.ctrlKey && (e.key === 'U' || e.key === 'u')) {
      e.preventDefault();
    }

    // Ctrl+S (Guardar página)
    if (e.ctrlKey && (e.key === 'S' || e.key === 's')) {
      e.preventDefault();
    }
  });

  // Detectar si se abren las DevTools (mediante debugger)
  // Nota: Esto puede ser molesto durante el desarrollo, pero cumple el requerimiento.
  setInterval(() => {
    const startTime = performance.now();
    debugger;
    const endTime = performance.now();
    if (endTime - startTime > 100) {
      // Si el debugger tardó mucho, es que las DevTools están abiertas
      // Podríamos redirigir o limpiar la pantalla
    }
  }, 2000);
});
</script>

<template>
    <div class="flex flex-col min-h-screen">
        <Header></Header>
        <Notificacion />
        <main class="flex-grow">
            <RouterView />
        </main>
        <Footer />
    </div>
</template>

