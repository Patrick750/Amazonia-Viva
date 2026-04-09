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
