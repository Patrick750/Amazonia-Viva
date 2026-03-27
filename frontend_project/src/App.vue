<script setup>
    import Header from './components/header.vue';
    import Footer from './components/footer.vue';
    import Notificacion from './components/notificacion.vue';
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

