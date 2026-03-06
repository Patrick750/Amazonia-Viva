<script setup>
    import { onMounted, ref } from 'vue'
    import axios from 'axios';
    import Header from './header.vue';

    const acc = localStorage.getItem('rol')
    console.log(acc)



</script>
<template>
    <Header></Header>
    <h1>{{ acc }}</h1>
</template>