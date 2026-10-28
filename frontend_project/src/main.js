import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

// Evitar que el navegador restaure la posición del scroll al recargar
if ('scrollRestoration' in window.history) {
    window.history.scrollRestoration = 'manual';
}

app.mount('#app')

// PWA: guarda la carcasa de la aplicación para abrirla sin conexión. Solo en producción,
// porque en desarrollo el servicio de Vite cambia constantemente sus archivos.
if ('serviceWorker' in navigator && import.meta.env.PROD) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch((error) => console.error('No se pudo registrar el service worker', error))
    })
}
