import { computed, ref } from 'vue'

// Instalación de la PWA. Los navegadores basados en Chromium avisan con `beforeinstallprompt`
// cuando la app es instalable; ese evento se guarda para ofrecerlo desde un botón propio.
// Safari en iOS no emite ese evento: allí solo se puede mostrar la guía manual.
const promptDiferido = ref(null)

const esStandalone = () =>
    window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true

const instalada = ref(esStandalone())

export const esIOS = () =>
    /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)

// Debe llamarse antes de montar la app: el evento puede dispararse muy pronto.
export function iniciarCapturaInstalacion() {
    window.addEventListener('beforeinstallprompt', (evento) => {
        evento.preventDefault()
        promptDiferido.value = evento
    })
    window.addEventListener('appinstalled', () => {
        instalada.value = true
        promptDiferido.value = null
    })
}

export function useInstalarPwa() {
    const puedeInstalar = computed(() => !instalada.value && !!promptDiferido.value)
    const requiereGuiaIOS = computed(() => !instalada.value && !promptDiferido.value && esIOS())
    const disponible = computed(() => puedeInstalar.value || requiereGuiaIOS.value)

    const instalar = async () => {
        const evento = promptDiferido.value
        if (!evento) return null
        evento.prompt()
        const { outcome } = await evento.userChoice
        // El evento solo sirve una vez; si se rechaza, el navegador volverá a emitirlo más adelante.
        promptDiferido.value = null
        if (outcome === 'accepted') instalada.value = true
        return outcome
    }

    return { puedeInstalar, requiereGuiaIOS, disponible, instalada, instalar }
}
