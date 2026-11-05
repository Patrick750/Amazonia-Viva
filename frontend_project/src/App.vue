<script setup>
    import { computed } from 'vue';
    import { useRoute } from 'vue-router';
    import Header from './components/header.vue';
    import Footer from './components/footer.vue';
    import Notificacion from './components/notificacion.vue';

    const route = useRoute();
    const esRutaAutenticacion = computed(() => ['/auth/login', '/auth/signup'].includes(route.path));
</script>

<template>
    <div class="flex flex-col min-h-screen">
        <Header v-if="!esRutaAutenticacion"></Header>
        <Notificacion />
        <main class="flex-grow">
            <RouterView />
        </main>
        <Footer v-if="!esRutaAutenticacion" />
    </div>
</template>

