<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const morphoRef = ref(null);

onMounted(() => {
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let morphoX = window.innerWidth / 2;
  let morphoY = window.innerHeight / 2;
  let animationFrameId;

  const handleMouseMove = (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  };

  document.addEventListener('mousemove', handleMouseMove);

  const animateMorpho = () => {
    if (!morphoRef.value) return;
    
    // Lerp para persecución fluida
    morphoX += (mouseX - morphoX) * 0.03;
    morphoY += (mouseY - morphoY) * 0.03;
    
    // Calcular ángulo de rotación
    const dx = mouseX - morphoX;
    const dy = mouseY - morphoY;
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    morphoRef.value.style.transform = `translate(${morphoX - 30}px, ${morphoY - 30}px) rotate(${angle + 90}deg)`;
    
    animationFrameId = requestAnimationFrame(animateMorpho);
  };

  animateMorpho();

  // Limpieza al desmontar el componente
  onUnmounted(() => {
    document.removeEventListener('mousemove', handleMouseMove);
    cancelAnimationFrame(animationFrameId);
  });
});
</script>

<template>
  <div class="min-h-screen bg-[#e8f4f1] text-slate-900 p-6 md:p-10 overflow-x-hidden relative z-0">
    
    <div class="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
      <div class="macaw-wrapper">
        <svg viewBox="0 0 200 200" class="w-full h-full">
          <defs>
            <linearGradient id="macaw-red" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#ff0844" />
              <stop offset="100%" stop-color="#ffb199" />
            </linearGradient>
            <linearGradient id="macaw-blue" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#00c6ff" />
              <stop offset="100%" stop-color="#0072ff" />
            </linearGradient>
          </defs>
          <path d="M40,180 L80,110 L95,130 Z" fill="url(#macaw-blue)"/>
          <path d="M80,110 C 110,140 170,80 160,40 C 150,20 130,25 120,45 C 100,75 60,90 80,110 Z" fill="url(#macaw-red)"/>
          <g class="macaw-wing">
            <path d="M110,65 C 145,85 160,145 130,125 C 110,105 95,85 110,65 Z" fill="#fceabb"/>
            <path d="M120,75 C 150,95 150,135 130,115 C 120,95 110,85 120,75 Z" fill="url(#macaw-blue)"/>
          </g>
          <path d="M150,42 C 180,45 180,65 160,55 Z" fill="#1e293b"/>
        </svg>
      </div>

      <div class="dolphin-wrapper">
        <svg viewBox="0 0 300 150" class="w-full h-full">
          <defs>
            <linearGradient id="pink-dolphin" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#ff9a9e" />
              <stop offset="100%" stop-color="#fecfef" />
            </linearGradient>
          </defs>
          <path d="M20,100 C 50,130 90,100 130,110 C 200,125 250,70 290,95 C 280,60 220,50 170,60 C 140,50 150,20 130,40 C 100,65 50,75 20,100 Z" fill="url(#pink-dolphin)"/>
          <path d="M150,85 C 170,120 135,125 150,85 Z" fill="#ff9a9e"/>
        </svg>
      </div>
    </div>

    <div ref="morphoRef" class="fixed top-0 left-0 w-[60px] h-[60px] pointer-events-none z-[9999] drop-shadow-[0_10px_10px_rgba(0,180,255,0.3)]">
      <svg viewBox="0 0 100 100" class="morpho-wings w-full h-full">
        <defs>
          <linearGradient id="morpho-blue" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#00f2fe" />
            <stop offset="100%" stop-color="#4facfe" />
          </linearGradient>
        </defs>
        <path d="M50,40 C 30,10 10,20 15,50 C 30,55 45,45 50,40 Z" fill="url(#morpho-blue)"/>
        <path d="M50,40 C 70,10 90,20 85,50 C 70,55 55,45 50,40 Z" fill="url(#morpho-blue)"/>
        <path d="M50,45 C 35,60 20,80 30,90 C 40,80 48,60 50,45 Z" fill="url(#morpho-blue)"/>
        <path d="M50,45 C 65,60 80,80 70,90 C 60,80 52,60 50,45 Z" fill="url(#morpho-blue)"/>
        <ellipse cx="50" cy="45" rx="3" ry="15" fill="#1e293b"/>
      </svg>
    </div>

    <main class="relative z-10 max-w-7xl mx-auto">
      
      <header class="mb-10 animate-fade-in-down">
        <h1 class="text-3xl font-bold text-emerald-900 tracking-tight">Amazonia Viva</h1>
        <p class="text-slate-600 mt-1">Gestión de Experiencias y Biodiversidad</p>
      </header>

      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        
        <article class="group relative overflow-hidden bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:bg-white/85 animate-fade-in-up" style="animation-delay: 0.1s;">
          <svg class="absolute -bottom-4 -right-4 w-[140px] h-[140px] opacity-5 z-0 pointer-events-none fill-slate-900 transition-all duration-400 group-hover:fill-emerald-600 group-hover:opacity-10 group-hover:-translate-x-2 group-hover:-translate-y-2 group-hover:scale-105" viewBox="0 0 24 24">
            <path d="M12,2C10.89,2 10,2.89 10,4V6H8.5a2.5,2.5 0 0 0 -2.5,2.5V11a2.5,2.5 0 0 0 2.5,2.5H10v7a2,2 0 0 0 4,0v-7h1.5a2.5,2.5 0 0 0 2.5,-2.5V8.5a2.5,2.5 0 0 0 -2.5,-2.5H14V4c0,-1.11 -0.89,-2 -2,-2Z" />
          </svg>
          <div class="relative z-10">
            <h3 class="text-sm font-semibold text-slate-500">Ingresos Totales</h3>
            <div class="text-3xl font-bold text-slate-900 my-2">$45.680.000</div>
            <div class="inline-flex items-center gap-1 text-sm font-semibold text-emerald-600">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              +18% este mes
            </div>
          </div>
        </article>

        <article class="group relative overflow-hidden bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:bg-white/85 animate-fade-in-up" style="animation-delay: 0.2s;">
          <svg class="absolute -bottom-4 -right-4 w-[140px] h-[140px] opacity-5 z-0 pointer-events-none fill-slate-900 transition-all duration-400 group-hover:fill-emerald-600 group-hover:opacity-10 group-hover:-translate-x-3 group-hover:scale-105" viewBox="0 0 24 24">
            <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,19.93C7.06,19.43 4,16.05 4,12C4,7.95 7.06,4.57 11,4.07V19.93M13,4.07C16.94,4.57 20,7.95 20,12C20,16.05 16.94,19.43 13,19.93V4.07M15,10.5A1.5,1.5 0 0,0 16.5,12A1.5,1.5 0 0,0 18,10.5A1.5,1.5 0 0,0 16.5,9A1.5,1.5 0 0,0 15,10.5M16.5,13.5A1.5,1.5 0 0,0 18,15A1.5,1.5 0 0,0 19.5,13.5A1.5,1.5 0 0,0 18,12A1.5,1.5 0 0,0 16.5,13.5Z" />
          </svg>
          <div class="relative z-10">
            <h3 class="text-sm font-semibold text-slate-500">Tours Vendidos</h3>
            <div class="text-3xl font-bold text-slate-900 my-2">156</div>
            <div class="inline-flex items-center gap-1 text-sm font-semibold text-emerald-600">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              +12% este mes
            </div>
          </div>
        </article>

        <article class="group relative overflow-hidden bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:bg-white/85 animate-fade-in-up" style="animation-delay: 0.3s;">
          <svg class="absolute -bottom-4 -right-4 w-[140px] h-[140px] opacity-5 z-0 pointer-events-none fill-slate-900 transition-all duration-400 group-hover:fill-emerald-600 group-hover:opacity-10 group-hover:-translate-y-3 group-hover:scale-105" viewBox="0 0 24 24">
            <path d="M22,12C22,12 21.36,10.58 20.35,9.65C19.35,8.72 18,8.22 18,8.22C18,8.22 16.89,7.5 15.68,7.21C14.47,6.91 13.16,7.05 13.16,7.05C13.16,7.05 11.5,6.67 10.15,6.58C8.81,6.48 7.5,6.67 7.5,6.67C7.5,6.67 6.13,6.33 4.88,6.29C3.62,6.25 2.5,6.5 2.5,6.5C2.5,6.5 3.39,8.22 4.14,9.65C4.89,11.08 5.39,12.5 5.39,12.5V14.17C5.39,14.17 5.72,15.58 6.72,16.52C7.73,17.45 9.06,17.95 9.06,17.95H11.58C11.58,17.95 12.92,18.29 14.17,18.25C15.42,18.21 16.56,17.78 16.56,17.78L19,16.52C19,16.52 20.36,15.11 20.86,13.68C21.36,12.25 21.36,10.82 21.36,10.82C21.36,10.82 22,12 22,12Z" />
          </svg>
          <div class="relative z-10">
            <h3 class="text-sm font-semibold text-slate-500">Satisfacción Promedio</h3>
            <div class="text-3xl font-bold text-slate-900 my-2 flex items-center">
              4.8 
              <svg class="w-6 h-6 ml-1.5 fill-amber-500 text-amber-500" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            </div>
            <div class="text-sm text-slate-500">Basado en 89 reseñas</div>
          </div>
        </article>

        <article class="group relative overflow-hidden bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:bg-white/85 animate-fade-in-up" style="animation-delay: 0.4s;">
          <svg class="absolute -bottom-4 -right-4 w-[140px] h-[140px] opacity-5 z-0 pointer-events-none fill-slate-900 transition-all duration-400 group-hover:fill-emerald-600 group-hover:opacity-10 group-hover:translate-x-2 group-hover:-translate-y-1 group-hover:scale-105" viewBox="0 0 24 24">
            <path d="M12,19.93A10,10 0 0,0 2,10A10,10 0 0,0 12,2.07A10,10 0 0,0 22,10A10,10 0 0,0 12,19.93M12,4.07V7.07C13.66,7.07 15,8.41 15,10.07S13.66,13.07 12,13.07V16.93C15.86,16.93 19,13.86 19,10S15.86,4.07 12,4.07M12,8.07C10.9,8.07 10,8.97 10,10.07S10.9,12.07 12,12.07V8.07Z" />
          </svg>
          <div class="relative z-10">
            <h3 class="text-sm font-semibold text-slate-500">Reservas Pendientes</h3>
            <div class="text-3xl font-bold text-slate-900 my-2">12</div>
            <div class="inline-flex items-center gap-1 text-sm font-semibold text-red-500">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
              Requiere atención
            </div>
          </div>
        </article>
      </section>

      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-2 bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-emerald-900 mb-4 pb-4 border-b border-white/80 relative z-10">Rendimiento de Ventas Mensual</h2>
          <div class="relative z-10 h-[300px] flex items-center justify-center text-slate-500 bg-white/40 rounded-xl border border-dashed border-white/80">
            Espacio reservado para gráfico
          </div>
        </div>

        <div class="bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-emerald-900 mb-4 pb-4 border-b border-white/80 relative z-10">Acciones de Gestión</h2>
          <div class="flex flex-col gap-3 relative z-10">
            
            <button class="flex items-center gap-3 p-4 bg-white/50 border border-white/80 rounded-xl font-semibold text-slate-900 text-sm transition-all duration-200 hover:bg-white hover:border-emerald-600 hover:text-emerald-600 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
              Gestionar Tours
            </button>
            
            <button class="flex items-center gap-3 p-4 bg-white/50 border border-white/80 rounded-xl font-semibold text-slate-900 text-sm transition-all duration-200 hover:bg-white hover:border-emerald-600 hover:text-emerald-600 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
              Ver Ventas
            </button>

            <button class="flex items-center gap-3 p-4 bg-white/50 border border-white/80 rounded-xl font-semibold text-slate-900 text-sm transition-all duration-200 hover:bg-white hover:border-emerald-600 hover:text-emerald-600 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
              Experiencias
            </button>

            <button class="flex items-center gap-3 p-4 bg-white/50 border border-white/80 rounded-xl font-semibold text-slate-900 text-sm transition-all duration-200 hover:bg-white hover:border-emerald-600 hover:text-emerald-600 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
              Mi Perfil
            </button>

          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
/* Animaciones personalizadas que son más limpias en CSS puro que en tailwind.config.js */
.animate-fade-in-down {
  animation: fadeInDown 0.8s ease-out forwards;
}
.animate-fade-in-up {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s ease-out forwards;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Animaciones complejas de la fauna */
.macaw-wrapper {
  position: absolute;
  width: 350px;
  height: 350px;
  animation: flyAcross 30s linear infinite;
  filter: drop-shadow(0 20px 30px rgba(0,0,0,0.15));
  opacity: 0.8;
}
.macaw-wing {
  transform-origin: 50% 50%;
  animation: flapWing 0.4s ease-in-out infinite alternate;
}

@keyframes flyAcross {
  0% { transform: translate(-20vw, 110vh) scale(0.8) rotate(15deg); }
  100% { transform: translate(110vw, -20vh) scale(1.2) rotate(-5deg); }
}
@keyframes flapWing {
  0% { transform: rotate(0deg) scaleY(1); }
  100% { transform: rotate(-35deg) scaleY(0.6); }
}

.dolphin-wrapper {
  position: absolute;
  width: 450px;
  height: 250px;
  bottom: 5%;
  left: -500px;
  animation: swimWave 35s ease-in-out infinite;
  opacity: 0.7;
  filter: blur(1px);
}

@keyframes swimWave {
  0% { transform: translateX(0) translateY(0) rotate(5deg); }
  25% { transform: translateX(40vw) translateY(-50px) rotate(-5deg); }
  50% { transform: translateX(80vw) translateY(30px) rotate(5deg); }
  100% { transform: translateX(120vw) translateY(-20px) rotate(-5deg); }
}

.morpho-wings {
  transform-origin: center;
  animation: flutterFast 0.15s ease-in-out infinite alternate;
}
@keyframes flutterFast {
  0% { transform: scaleX(1); }
  100% { transform: scaleX(0.2); }
}
</style>