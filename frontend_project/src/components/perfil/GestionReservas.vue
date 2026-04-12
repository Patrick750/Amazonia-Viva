<template>
  <div class="h-full flex flex-col bg-[#050a09] relative font-sans overflow-hidden">
    
    <!-- ═══════════════════════════════════
         HERO ADMINISTRATIVO COMPACTO
    ═══════════════════════════════════ -->
    <section class="relative min-h-[220px] md:h-[25vh] flex items-center overflow-hidden shrink-0 py-12 md:py-0">
      <!-- Botón Volver (Sticky-style absolute) -->
      <div class="absolute top-4 left-6 md:top-8 md:left-8 z-20">
        <router-link to="/panel/dashboard" class="group flex items-center gap-3 px-4 py-2 bg-white/5 hover:bg-[#00f5d4]/10 border border-white/10 hover:border-[#00f5d4]/30 rounded-full transition-all duration-300">
           <svg class="w-4 h-4 text-[#00f5d4] transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
           <span class="text-[9px] font-black text-white/60 group-hover:text-white uppercase tracking-widest">Dashboard</span>
        </router-link>
      </div>

      <!-- Fondo Selva Brumosa -->
      <div class="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=2560&auto=format&fit=crop"
          alt="Jungle"
          class="w-full h-full object-cover opacity-40 scale-105 animate-subtle-zoom"
        />
        <div class="absolute inset-0 misty-overlay"></div>
      </div>

      <div class="relative z-10 w-full max-w-[1400px] mx-auto px-6 md:px-8 mt-4 md:mt-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <span class="text-[#00f5d4] text-[10px] font-black uppercase tracking-[0.3em] mb-2 block">Operaciones Amazónicas</span>
          <h1 class="text-3xl md:text-5xl font-black text-white tracking-tighter">
            GESTIÓN <span class="text-emerald-400/50 uppercase">Logística</span>
          </h1>
        </div>

        <div class="glass-pill p-1 md:p-1.5 flex gap-1 shadow-2xl overflow-x-auto no-scrollbar max-w-full">
          <button v-for="tab in tabs" :key="tab.id"
            @click="changeTab(tab.id)"
            :class="['px-4 md:px-6 py-2 md:py-2.5 rounded-full text-[9px] md:text-[10px] font-black tracking-widest uppercase transition-all duration-500 whitespace-nowrap',
              currentTab === tab.id ? 'bg-[#00f5d4] text-[#050a09] emerald-glow-active' : 'text-white/40 hover:text-white']"
          >
            {{ tab.name }}
          </button>
        </div>
      </div>
    </section>

    <!-- ÁREA DE TRABAJO -->
    <div class="flex-1 overflow-y-auto bg-[#050a09]">
      <div class="max-w-[1400px] mx-auto p-8 pt-10">
        
        <!-- === SECCIÓN: RESERVADOS / RECHAZADOS === -->
        <section v-if="currentTab === 'reservados' || currentTab === 'rechazados'" class="space-y-6">
          
          <!-- BREADCRUMBS PREMIUM -->
          <nav class="flex flex-wrap items-center gap-2 md:gap-4 text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] text-white/20 mb-8 md:mb-10 pb-4 border-b border-white/5">
            <button @click="backToLevel(1)" 
              :class="navigationLevel === 1 ? 'text-[#00f5d4]' : 'hover:text-white/60'"
              class="transition-colors shrink-0"
            >
              LOGÍSTICA
            </button>
            <span v-if="navigationLevel >= 2" class="text-white/5 shrink-0">/</span>
            <button v-if="navigationLevel >= 2" @click="backToLevel(2)" 
              :class="navigationLevel === 2 ? 'text-[#00f5d4]' : 'hover:text-white/60'"
              class="transition-colors max-w-[120px] md:max-w-[200px] truncate"
            >
              {{ selectedPackage?.paquete?.nombre || 'PAQUETE' }}
            </button>
            <span v-if="navigationLevel === 3" class="text-white/5 shrink-0">/</span>
            <span v-if="navigationLevel === 3" class="text-[#00f5d4] opacity-50 shrink-0">
              MANIFIESTO
            </span>
            
            <!-- Buscador responsivo -->
            <div v-if="navigationLevel === 1" class="ml-auto relative w-full md:w-auto mt-4 md:mt-0">
              <input 
                v-model="searchQuery"
                type="text" 
                placeholder="BUSCAR EXPEDICIÓN..." 
                class="bg-white/5 border border-white/10 rounded-full px-10 py-2.5 md:py-2 text-[9px] md:text-[10px] font-black text-white placeholder:text-white/20 focus:border-[#00f5d4]/40 transition-all outline-none w-full md:w-[280px]"
              >
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
          </nav>

          <!-- NIVEL 1: PAQUETES -->
          <div v-if="navigationLevel === 1" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 items-start">
            <div v-for="(grupo, idx) in reservasFiltradas" :key="grupo?.paquete?.id" 
              @click="selectPackage(grupo)"
              class="group bg-zinc-900/40 rounded-[32px] p-5 backdrop-blur-sm border border-white/5 hover:border-[#00f5d4]/20 transition-all duration-700 hover:-translate-y-2 flex flex-col animate-fade-in shadow-2xl"
              :style="{ animationDelay: (idx * 0.03) + 's' }"
            >
              <!-- MARCO INDEPENDIENTE PARA LA IMAGEN (TEMA OSCURO) -->
              <div class="h-44 w-full relative overflow-hidden rounded-2xl bg-zinc-950/50 border border-white/5 flex items-center justify-center mb-6">
                <!-- Imagen centrada y nunca estirada -->
                <div v-if="grupo.paquete.portada" 
                  class="w-full h-full bg-contain bg-no-repeat bg-center transition-transform duration-1000 group-hover:scale-105"
                  :style="{ backgroundImage: `url(${grupo.paquete.portada})` }"
                >
                </div>
                <div v-else class="w-full h-full flex items-center justify-center bg-zinc-950">
                  <svg class="w-10 h-10 text-zinc-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                </div>

                <!-- BADGE OPERATIVO (IZQUIERDA) -->
                <div class="absolute top-4 left-4">
                   <span class="px-3 py-1 bg-black/50 backdrop-blur-md border border-white/10 text-white text-[8px] font-black uppercase tracking-widest rounded-full">
                    ID-{{ grupo.paquete.id }}
                  </span>
                </div>

                <!-- BADGE DE SALIDAS (DERECHA) -->
                <div class="absolute top-4 right-4">
                  <span :class="currentTab === 'reservados' ? 'bg-[#00f5d4] text-[#050a09]' : 'bg-zinc-800 text-zinc-400'" class="text-[9px] font-black px-3 py-1 rounded-full uppercase tracking-tighter shadow-sm">
                    {{ grupo.reservasPorFecha.length }} {{ grupo.reservasPorFecha.length === 1 ? 'Salida' : 'Salidas' }}
                  </span>
                </div>
              </div>

              <!-- CUERPO DE INFORMACIÓN SEPARADO -->
              <div class="flex flex-col gap-5">
                <div>
                  <h4 class="text-xl font-black text-white leading-tight group-hover:text-[#00f5d4] transition-colors uppercase tracking-tight mb-4">
                    {{ grupo?.paquete?.nombre }}
                  </h4>

                  <div class="space-y-4">
                    <div class="flex justify-between items-end">
                      <span class="text-[10px] font-black uppercase tracking-[0.1em] text-white/30">
                        {{ currentTab === 'reservados' ? 'Ocupación Confirmada' : 'Total Cancelaciones' }}
                      </span>
                      <span class="text-base font-black text-white">{{ grupo.totalReservas }} pax</span>
                    </div>
                  </div>
                </div>

                <div class="pt-5 border-t border-white/5 flex items-center justify-between">
                  <span class="text-[10px] font-black text-white/40 uppercase tracking-widest group-hover:text-[#00f5d4] transition-colors">Ver Detalles de Ventas</span>
                  <div class="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 group-hover:bg-[#00f5d4] group-hover:text-[#050a09] transition-all shadow-md group-hover:shadow-[#00f5d4]/40">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7-7 7"/></svg>
                  </div>
                </div>
              </div>
            </div>


            <!-- Empty State -->
            <div v-if="reservasFiltradas.length === 0" class="col-span-full py-24 text-center border-2 border-dashed border-slate-100 rounded-2xl bg-slate-50/20">
              <svg class="w-12 h-12 text-slate-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0l-8 4-8-4"/></svg>
              <h3 class="text-lg font-bold text-slate-700">Sin actividad registrada</h3>
              <p class="text-xs text-slate-400 mt-2 font-medium">No se encontraron paquetes con reservas en el estado actual.</p>
            </div>
          </div>

          <!-- NIVEL 2: CALENDARIO DE SALIDAS (GLASS CARDS) -->
          <div v-else-if="navigationLevel === 2 && selectedPackage" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
             <div v-for="(fechaObj, idx) in (selectedPackage?.reservasPorFecha || [])" :key="fechaObj?.fecha"
                @click="selectDate(fechaObj)"
                class="group relative glass-card p-6 rounded-[24px] transition-all duration-500 cursor-pointer flex items-center justify-between animate-fade-in hover:emerald-glow-active"
                :style="{ animationDelay: (idx * 0.02) + 's' }"
              >
                <div class="flex items-center gap-6">
                  <!-- Indicador de Fecha Premium -->
                  <div class="flex flex-col items-center justify-center w-14 h-14 bg-white/5 rounded-2xl border border-white/10 group-hover:border-[#00f5d4]/40 transition-all">
                    <span class="text-[8px] font-black text-[#00f5d4] uppercase tracking-widest mb-1">{{ new Date(fechaObj.fecha).toLocaleDateString('es-CO', { month: 'short', timeZone: 'UTC' }) }}</span>
                    <span class="text-xl font-black text-white leading-none">{{ new Date(fechaObj.fecha).getUTCDate() }}</span>
                  </div>
                  
                  <div>
                    <h5 class="text-sm font-black text-white uppercase tracking-tight mb-1">{{ formatDate(fechaObj.fecha) }}</h5>
                    <div class="flex items-center gap-2">
                      <div class="w-1.5 h-1.5 rounded-full bg-[#00f5d4] shadow-[0_0_8px_#00f5d4]"></div>
                      <span class="text-[10px] font-bold text-white/30 uppercase tracking-widest">{{ currentTab === 'reservados' ? 'Active' : 'Archived' }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="flex items-center gap-6">
                  <div class="text-right">
                    <p class="text-xl font-black text-white leading-none">{{ fechaObj.totalTuristas }}</p>
                    <p class="text-[9px] text-[#00f5d4] font-black uppercase tracking-widest mt-1">Pax</p>
                  </div>
                  <div class="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center text-white/20 group-hover:text-white transition-all">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7-7 7"/></svg>
                  </div>
                </div>
              </div>
          </div>

          <!-- NIVEL 3: MANIFIESTO PREMIUM -->
          <div v-else-if="navigationLevel === 3 && selectedDateGroup" class="space-y-8 animate-fade-in">
            
            <div class="glass-card rounded-[32px] p-8 flex flex-col lg:flex-row items-center justify-between gap-8 border-white/10 relative overflow-hidden">
               <!-- Glow decorativo -->
              <div class="absolute -top-20 -right-20 w-64 h-64 bg-[#00f5d4]/5 rounded-full blur-[100px]"></div>

              <div class="flex items-center gap-8 relative z-10">
                <div class="w-16 h-16 bg-[#00f5d4]/10 rounded-[22px] flex items-center justify-center text-[#00f5d4] border border-[#00f5d4]/20">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>
                </div>
                <div>
                  <h4 class="text-2xl font-black text-white tracking-tighter">MANIFIESTO OPERATIVO</h4>
                  <p class="text-[10px] text-white/30 font-black uppercase tracking-[0.3em] mt-1">Control de Despacho y Logística de Campo</p>
                </div>
              </div>
              
              <div class="flex flex-wrap items-center gap-4 w-full lg:w-auto relative z-10">
                <div class="flex items-center gap-3 px-5 py-3 bg-white/5 rounded-2xl border border-white/10 shrink-0">
                  <span class="text-[10px] text-white/20 font-black uppercase tracking-widest">FORMATO:</span>
                  <select v-model="exportFormat" class="bg-transparent text-white text-[10px] font-black outline-none cursor-pointer uppercase tracking-widest">
                    <option value="" class="bg-[#0a1210]">ELEGIR</option>
                    <option value="CSV" class="bg-[#0a1210]">CSV UTF-8</option>
                    <option value="XLS" class="bg-[#0a1210]">EXCEL XLS</option>
                    <option value="PDF" class="bg-[#0a1210]">REPORTE PDF</option>
                  </select>
                </div>

                <button 
                  @click="ejecutarDescarga"
                  :disabled="!exportFormat"
                  class="bg-[#00f5d4] text-[#050a09] px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:scale-105 active:scale-95 disabled:opacity-20 transition-all shadow-[0_0_20px_rgba(0,245,212,0.3)]"
                >
                  DESCARGAR
                </button>
                <div class="h-10 w-px bg-white/5 mx-2 hidden lg:block"></div>

                <button 
                  @click="abrirConfirmarAnularSalida"
                  class="px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] text-rose-500 border border-rose-500/20 hover:bg-rose-500 hover:text-white transition-all duration-500"
                >
                  RECHAZAR SALIDA
                </button>
              </div>
            </div>

            <!-- PASAJEROS (CARDS DARK) -->
            <div class="space-y-4">
              <div class="flex items-center justify-between px-6">
                <span class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em]">Lista de Pasajeros Registrados ({{ selectedDateGroup?.turistas.length }})</span>
              </div>

              <div v-for="turista in (selectedDateGroup?.turistas || [])" :key="turista?.id_transaccion + '-' + turista?.nombre" 
                class="group glass-card p-6 rounded-[28px] hover:border-[#00f5d4]/20 transition-all duration-500 flex flex-col md:flex-row md:items-center justify-between gap-8 border-white/5"
              >
                <!-- INFO PRINCIPAL -->
                <div class="flex items-center gap-6">
                  <div class="relative">
                    <img v-if="turista.foto" 
                      :src="turista.foto" 
                      class="w-16 h-16 object-cover bg-white/5 border border-white/10 rounded-[20px] shadow-xl shadow-black/20 transition-all duration-500 group-hover:border-[#00f5d4]/40" 
                    />
                    <div v-else class="w-16 h-16 bg-white/5 border border-white/10 text-[#00f5d4] rounded-[20px] flex items-center justify-center font-black text-2xl group-hover:bg-[#00f5d4] group-hover:text-[#050a09] transition-all duration-500 shadow-xl shadow-black/20">
                      {{ turista.nombre.charAt(0) }}
                    </div>
                    <div v-if="turista.es_comprador" class="absolute -top-1 -right-1 w-6 h-6 bg-[#00f5d4] text-[#050a09] rounded-xl flex items-center justify-center border-[3px] border-[#0a1210] shadow-xl">
                      <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                    </div>
                  </div>
                  <div>
                    <h5 class="text-lg font-black text-white tracking-tight uppercase mb-1">{{ turista.nombre }}</h5>
                    <div class="flex flex-wrap items-center gap-3">
                       <span class="text-[10px] font-mono font-black text-white/30 bg-white/5 border border-white/10 px-3 py-1 rounded-lg uppercase tracking-widest">{{ turista.identificacion }}</span>
                       <span :class="turista.es_comprador ? 'text-[#00f5d4] border-[#00f5d4]/30 bg-[#00f5d4]/5' : 'text-white/20 border-white/10 bg-white/5'" class="px-3 py-1 text-[9px] font-black uppercase rounded-lg tracking-[0.2em] border">
                        {{ turista.rol }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- INFO LOGÍSTICA -->
                <div class="grid grid-cols-2 lg:flex items-center gap-12 flex-1 lg:justify-center px-4">
                  <div class="space-y-2">
                    <p class="text-[9px] font-black text-white/20 uppercase tracking-[0.2em]">Contacto</p>
                    <p class="text-xs font-bold text-white/60 tracking-wide">{{ turista.contacto !== 'N/A' ? turista.contacto : 'SECURE_REG' }}</p>
                  </div>
                  <div class="space-y-2">
                    <p class="text-[9px] font-black text-white/20 uppercase tracking-[0.2em]">Referencia</p>
                    <p class="text-xs font-mono font-black text-[#00f5d4]/50">TRX-{{ turista.id_transaccion }}</p>
                  </div>
                </div>

                <!-- ACCIONES -->
                <div class="flex items-center gap-4 border-t border-white/5 md:border-t-0 pt-6 md:pt-0">
                  <div class="flex items-center gap-3">
                    <button @click="abrirConfirmarAnulacion(turista)" 
                      v-if="currentTab === 'reservados'"
                      class="h-12 px-6 flex items-center gap-3 bg-white/5 text-white/40 hover:bg-rose-500/10 hover:text-rose-500 border border-white/10 hover:border-rose-500/30 rounded-2xl transition-all font-black text-[10px] uppercase tracking-widest"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      ANULAR
                    </button>
                    <span v-else class="text-[10px] font-black text-rose-500 uppercase bg-rose-500/10 px-6 py-3 rounded-2xl border border-rose-500/20 tracking-[0.2em]">ANULADO</span>
                  </div>
                </div>
              </div>

              <!-- Vacío en Nivel 3 -->
              <div v-if="selectedDateGroup?.turistas.length === 0" class="py-20 text-center bg-slate-50 border border-dashed border-slate-200 rounded-2xl">
                 <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Cámara de pasajeros vacía</p>
              </div>
            </div>
          </div>
        </section>

        <!-- === SECCIÓN: CANCELACIONES (DESKTOP + MOBILE) === -->
        <section v-else-if="currentTab === 'cancelaciones'" class="space-y-6 md:space-y-8 animate-fade-in">
           <div class="px-4">
              <h3 class="text-[10px] md:text-sm font-black text-rose-500 uppercase tracking-[0.3em]">Registro de Reversiones y Cancelaciones</h3>
           </div>

           <!-- Desktop: Table -->
           <div class="hidden md:block glass-card rounded-[32px] border-white/5 overflow-hidden shadow-2xl">
              <table class="w-full text-left text-sm text-white/60 border-collapse">
                <thead class="bg-white/5 text-[9px] font-black uppercase tracking-[0.2em] text-white/30 border-b border-white/5">
                  <tr>
                    <th class="px-8 py-6">LOG-ID</th>
                    <th class="px-8 py-6">SERVICE_NAME</th>
                    <th class="px-8 py-6 text-center">SCHEDULED</th>
                    <th class="px-8 py-6">EXECUTION</th>
                    <th class="px-8 py-6 text-right">FINANCIAL_IMPACT</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/5">
                  <tr v-for="cancelado in cancelaciones" :key="cancelado.id_reserva" class="hover:bg-white/5 transition-all duration-300">
                    <td class="px-8 py-6">
                      <span class="font-mono text-[10px] font-black text-[#00f5d4]/40">#LOG-{{ cancelado.id_reserva }}</span>
                    </td>
                    <td class="px-8 py-6">
                      <p class="font-black text-white text-sm tracking-tight uppercase">{{ cancelado.paquete_nombre }}</p>
                      <span class="text-[8px] text-rose-500 font-black uppercase tracking-widest mt-1 block">REVERSED_FUNDS</span>
                    </td>
                    <td class="px-8 py-6 text-center">
                      <span class="text-[10px] font-black text-white bg-white/5 border border-white/10 px-4 py-2 rounded-xl uppercase tracking-widest">{{ formatDate(cancelado.fecha_salida) }}</span>
                    </td>
                    <td class="px-8 py-6">
                       <span class="text-[10px] font-bold text-white/40 uppercase tracking-widest">{{ formatDate(cancelado.fecha_cancelacion) }}</span>
                    </td>
                    <td class="px-8 py-6 text-right text-rose-500">
                      <span class="text-[10px] font-black uppercase tracking-widest block mb-1">TOTAL_REFUND</span>
                      <span class="font-black text-lg tracking-tighter">COP {{ formatCurrency(cancelado.monto_reembolso) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
           </div>

           <!-- Mobile: Cards -->
           <div class="md:hidden space-y-4">
              <div v-for="cancelado in cancelaciones" :key="cancelado.id_reserva" class="glass-card p-6 rounded-[32px] border-rose-500/10 relative overflow-hidden">
                 <div class="absolute inset-0 bg-gradient-to-br from-rose-500/[0.05] to-transparent pointer-events-none"></div>
                 <div class="flex justify-between items-start mb-4 relative z-10">
                    <span class="text-[9px] font-black text-rose-500 uppercase tracking-widest">#LOG-{{ cancelado.id_reserva }}</span>
                    <span class="px-3 py-1 bg-white/5 rounded-full text-[8px] font-bold text-white/40 uppercase tracking-widest">
                       {{ formatDate(cancelado.fecha_salida) }}
                    </span>
                 </div>
                 <div class="relative z-10 mb-6">
                    <h4 class="text-xs font-black text-white uppercase tracking-tight leading-tight">{{ cancelado.paquete_nombre }}</h4>
                    <p class="text-[8px] text-white/20 uppercase font-bold mt-1">EJECUCIÓN: {{ formatDate(cancelado.fecha_cancelacion) }}</p>
                 </div>
                 <div class="flex justify-between items-center border-t border-white/5 pt-4 relative z-10">
                    <span class="text-[8px] font-black text-rose-500 uppercase tracking-[0.2em]">REEMBOLSO 100%</span>
                    <span class="font-black text-rose-500 text-base tracking-tighter">COP {{ formatCurrency(cancelado.monto_reembolso) }}</span>
                 </div>
              </div>
           </div>

           <!-- Vacío -->
           <div v-if="cancelaciones.length === 0" class="py-24 text-center glass-card rounded-[32px] border-dashed border-white/10">
              <div class="w-16 h-16 bg-white/5 rounded-3xl flex items-center justify-center mx-auto mb-6 text-white/10">
                 <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              </div>
              <p class="text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Sin registros de cancelaciones</p>
           </div>
        </section>

      </div>
    </div>

    <!-- MODAL DE CONFIRMACIÓN (GLASSMOPRHISM RED) -->
    <transition name="fade">
            <div v-if="cancelModal.isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-6 bg-black/60 backdrop-blur-xl">
        <div class="glass-card rounded-[32px] md:rounded-[40px] shadow-[0_0_50px_rgba(0,0,0,0.5)] w-full max-w-md overflow-hidden animate-zoom-in border-white/10">
          <div class="p-6 md:p-10 text-center relative z-10">
             <div class="absolute -top-10 -left-10 w-32 h-32 bg-rose-500/10 rounded-full blur-3xl pointer-events-none"></div>

            <div class="w-16 h-16 md:w-20 md:h-20 bg-rose-500/10 rounded-[24px] md:rounded-[28px] flex items-center justify-center mx-auto mb-6 md:mb-8 text-rose-500 border border-rose-500/20 shadow-[0_0_20px_rgba(244,63,94,0.1)]">
               <svg class="w-8 h-8 md:w-10 md:h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            </div>
            
            <h3 class="text-xl md:text-2xl font-black text-white mb-2 uppercase tracking-tighter">RECHAZO TÉCNICO</h3>
            <p class="text-[10px] md:text-[11px] text-rose-500 font-black uppercase tracking-[0.15em] mb-8 md:mb-12 animate-pulse">
              ⚠️ ADVERTENCIA: DEVOLUCIÓN OBLIGATORIA DEL 100%
            </p>

            <div class="bg-white/5 rounded-[24px] p-6 md:p-8 text-left space-y-4 md:space-y-6 mb-8 md:mb-12 border border-white/5">
              <div class="flex justify-between items-center gap-4">
                <span class="text-[9px] md:text-[10px] text-white/20 font-black uppercase tracking-widest shrink-0">PASAJERO:</span>
                <span class="font-black text-white uppercase text-xs md:text-sm truncate">{{ cancelModal.turista?.nombre }}</span>
              </div>
              <div class="flex justify-between items-end border-t border-white/5 pt-4 md:pt-6">
                <div>
                  <span class="text-[8px] md:text-[9px] text-rose-500 font-black uppercase block mb-1 tracking-widest">TOTAL_REFUND</span>
                  <span class="text-[9px] md:text-[10px] font-bold text-white/20 uppercase tracking-widest">Unrestricted</span>
                </div>
                <div class="text-right">
                  <span class="font-black text-rose-500 text-xl md:text-2xl tracking-tighter">COP {{ formatCurrency(cancelModal.turista?.monto_total) }}</span>
                </div>
              </div>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
              <button @click="closeCancelModal" class="order-2 sm:order-1 flex-1 px-6 md:px-8 py-4 md:py-5 rounded-2xl text-[9px] md:text-[10px] font-black uppercase tracking-widest text-white/30 hover:bg-white/5 transition-all">
                ABORTAR
              </button>
              <button 
                @click="confirmarAnulacion" 
                :disabled="cancelModal.isProcessing"
                class="order-1 sm:order-2 flex-1 px-6 md:px-8 py-4 md:py-5 bg-rose-600 hover:bg-rose-500 text-white rounded-2xl text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] shadow-2xl shadow-rose-900/20 transition-all flex items-center justify-center gap-2"
              >
                <svg v-if="cancelModal.isProcessing" class="animate-spin h-3 w-3 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
                <span>CONFIRMAR_RECHAZO</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
    <!-- MODAL DE ANULACIÓN MASIVA (CRITICAL) -->
    <transition name="fade">
            <div v-if="cancelSalidaModal.isOpen" class="fixed inset-0 z-[110] flex items-center justify-center p-4 md:p-6 bg-black/80 backdrop-blur-2xl">
        <div class="glass-card rounded-[32px] md:rounded-[48px] shadow-2xl w-full max-w-lg overflow-hidden animate-zoom-in border-rose-500/20">
          <div class="p-6 md:p-12 text-center text-white relative z-10">
             <div class="absolute inset-0 bg-gradient-to-b from-rose-500/5 to-transparent pointer-events-none"></div>

            <div class="w-20 h-20 md:w-24 md:h-24 bg-rose-500/10 text-rose-500 rounded-[28px] md:rounded-[32px] flex items-center justify-center mx-auto mb-6 md:mb-10 border border-rose-500/30 shadow-[0_0_40px_rgba(244,63,94,0.2)]">
               <svg class="w-10 h-10 md:w-12 md:h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            </div>
            
            <h3 class="text-2xl md:text-3xl font-black tracking-tighter mb-2 uppercase">¡ALERTA_CRÍTICA!</h3>
            <p class="text-[10px] md:text-[11px] font-black text-rose-500 uppercase tracking-[0.4em] mb-8 md:mb-12">Anulación Masiva de Operación</p>

            <div class="bg-white/5 rounded-[24px] md:rounded-[32px] p-6 md:p-10 text-left space-y-4 md:space-y-6 mb-8 md:mb-12 border border-white/10 shadow-inner">
              <div class="flex justify-between items-center gap-4">
                <span class="text-[9px] md:text-[10px] text-white/20 font-black uppercase tracking-widest shrink-0">SERVICIO:</span>
                <span class="font-black text-white uppercase text-[10px] md:text-xs tracking-tight truncate">{{ selectedPackage?.paquete?.nombre }}</span>
              </div>
              <div class="flex justify-between items-center border-t border-white/5 pt-4 md:pt-6">
                <span class="text-[9px] md:text-[10px] text-white/20 font-black uppercase tracking-widest">DESPACHO:</span>
                <span class="font-black text-white uppercase text-[10px] md:text-xs">{{ formatDate(selectedDate) }}</span>
              </div>
              <div class="flex justify-between items-center border-t border-white/5 pt-4 md:pt-6">
                <span class="text-[9px] md:text-[10px] font-black text-rose-500 uppercase tracking-widest">AFECTACIÓN TOTAL:</span>
                <span class="font-black text-rose-500 text-xl md:text-2xl tracking-tighter">{{ selectedDateGroup?.turistas.length }} pax</span>
              </div>
            </div>

            <p class="text-[10px] md:text-xs text-white/30 font-medium leading-relaxed mb-6 italic uppercase tracking-widest leading-relaxed">
              Esta acción revocará irreversiblemente todas las reservas confirmadas.
            </p>
            
            <div class="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4 mb-8 md:mb-12">
              <p class="text-[10px] md:text-[11px] text-rose-500 font-black uppercase tracking-[0.1em]">
                ⚠️ ALERTA: LA AGENCIA DEBERÁ REEMBOLSAR EL 100% DE LOS PAGOS A TODOS LOS TURISTAS AFECTADOS.
              </p>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
              <button @click="closeCancelSalidaModal" class="order-2 sm:order-1 flex-1 px-6 md:px-10 py-4 md:py-6 rounded-2xl md:rounded-3xl text-[9px] md:text-[10px] font-black uppercase tracking-widest text-white/40 hover:bg-white/5 transition-all outline-none">
                ABORTAR
              </button>
              <button 
                @click="confirmarAnularSalida" 
                :disabled="cancelSalidaModal.isProcessing"
                class="order-1 sm:order-2 flex-1 px-6 md:px-10 py-4 md:py-6 bg-rose-600 hover:bg-rose-500 text-white rounded-2xl md:rounded-3xl text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] shadow-[0_20px_40px_rgba(225,29,72,0.3)] transition-all flex items-center justify-center gap-3"
              >
                <svg v-if="cancelSalidaModal.isProcessing" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
                <span>CONFIRMAR_RECHAZO</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from '@/api/axios'

// --- RECURSOS DINÁMICOS ---
const paquetesRaw = ref([])
const reservasAgrupadasRaw = ref([])
const rechazadosAgrupadasRaw = ref([])
const cancelaciones = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const exportFormat = ref('')

// --- NAVEGACIÓN CORPORATIVA ---
const tabs = [
  { id: 'reservados', name: 'Almacén Reservas' },
  { id: 'rechazados', name: 'Filtro Rechazos' },
  { id: 'cancelaciones', name: 'Cancelaciones' }
]
const currentTab = ref('reservados')
const navigationLevel = ref(1)

// --- ESTADO DE SELECCIÓN ---
const selectedPackage = ref(null)
const selectedDate = ref(null)
const selectedDateGroup = ref(null)


const reservasAgrupadas = computed(() => {
  if (currentTab.value === 'reservados') return reservasAgrupadasRaw.value
  if (currentTab.value === 'rechazados') return rechazadosAgrupadasRaw.value
  return []
})

const reservasFiltradas = computed(() => {
  return reservasAgrupadas.value.filter(p => p.paquete.nombre.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const fetchGestionReservas = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/api/gestion-logistica/')
    paquetesRaw.value = data.paquetes_list
    reservasAgrupadasRaw.value = data.reservasAgrupadas
    rechazadosAgrupadasRaw.value = data.rechazadosAgrupados
    cancelaciones.value = data.cancelaciones
  } catch (err) {
    console.error('Error:', err)
    error.value = 'Fallo de conexión con el servidor.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchGestionReservas)

// --- ACCIONES ---
const changeTab = (id) => { currentTab.value = id; navigationLevel.value = 1; selectedPackage.value = null }
const selectPackage = (g) => { selectedPackage.value = g; navigationLevel.value = 2 }
const selectDate = (f) => { selectedDate.value = f.fecha; selectedDateGroup.value = f; navigationLevel.value = 3 }
const backToLevel = (l) => {
  navigationLevel.value = l
  if (l < 3) { selectedDate.value = null; selectedDateGroup.value = null }
  if (l < 2) { selectedPackage.value = null }
}
const ejecutarDescarga = async () => {
  if (!exportFormat.value) {
    alert('Por favor selecciona un formato de exportación.')
    return
  }

  try {
    const response = await axios.post('/api/gestion-logistica/exportar/', {
      paquete_id: selectedPackage.value.paquete.id,
      fecha: selectedDate.value,
      formato: exportFormat.value
    }, { responseType: 'blob' })

    // Crear un blob con el contenido y el tipo MIME correcto
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    
    // Generar nombre de archivo amigable
    const tourName = selectedPackage.value.paquete.nombre.replace(/\s+/g, '_')
    const ext = exportFormat.value.toLowerCase() === 'xls' ? 'xlsx' : exportFormat.value.toLowerCase()
    link.download = `Manifiesto_${tourName}_${selectedDate.value}.${ext}`
    
    // Forzar descarga
    document.body.appendChild(link)
    link.click()
    
    // Limpieza
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
  } catch (err) {
    console.error('Error en descarga:', err)
    alert('No se pudo generar el archivo de exportación. Verifica la conexión con el servidor.')
  }
}

// --- CANCELACIÓN TÉCNICA ---
const cancelModal = reactive({ isOpen: false, turista: null, isProcessing: false })
const cancelSalidaModal = reactive({ isOpen: false, isProcessing: false })
const abrirConfirmarAnulacion = (t) => { cancelModal.turista = t; cancelModal.isOpen = true }
const closeCancelModal = () => { cancelModal.isOpen = false }
const confirmarAnulacion = async () => {
  const t = cancelModal.turista
  cancelModal.isProcessing = true
  try {
    await axios.post('/api/gestion-logistica/anular/', { id_detalle: t.id_detalle })
    cancelaciones.value.unshift({ 
      id_reserva: t.id_transaccion, 
      paquete_nombre: selectedPackage.value.paquete.nombre, 
      fecha_salida: selectedDate.value, 
      fecha_cancelacion: new Date().toISOString(), 
      monto_reembolso: t.monto_total 
    })
    
    if (selectedDateGroup.value) {
      selectedDateGroup.value.turistas = selectedDateGroup.value.turistas.filter(item => item.id_detalle !== t.id_detalle)
      selectedDateGroup.value.totalTuristas = selectedDateGroup.value.turistas.reduce((sum, item) => sum + item.cupos, 0)
      if (selectedDateGroup.value.totalTuristas === 0) { 
        backToLevel(2)
        fetchGestionReservas() 
      }
    }
    closeCancelModal()
    
    // REDIRECCIÓN Y RECARGA SOLICITADA POR EL USUARIO
    await fetchGestionReservas()
    currentTab.value = 'reservados'
    backToLevel(1)
  } catch (err) {
    alert('Error en el procedimiento de anulación.')
  } finally {
    cancelModal.isProcessing = false
  }
}

// --- ANULACIÓN MASIVA DE SALIDA ---
const abrirConfirmarAnularSalida = () => { cancelSalidaModal.isOpen = true }
const closeCancelSalidaModal = () => { cancelSalidaModal.isOpen = false }
const confirmarAnularSalida = async () => {
  cancelSalidaModal.isProcessing = true
  try {
    await axios.post('/api/gestion-logistica/anular-salida/', { 
      paquete_id: selectedPackage.value.paquete.id,
      fecha: selectedDate.value
    })
    
    // Al anular toda la salida, regresamos al Nivel 1 del Almacén de Reservas por solicitud
    await fetchGestionReservas()
    currentTab.value = 'reservados'
    backToLevel(1)
    closeCancelSalidaModal()
  } catch (err) {
    console.error(err)
    alert('Fallo en la anulación masiva de la salida.')
  } finally {
    cancelSalidaModal.isProcessing = false
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('es-CO').format(val || 0)
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' })
}
</script>

<style scoped>
/* SOPORTES DE ANIMACIÓN SOBRIA */
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-zoom-in {
  animation: zoomIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes zoomIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

/* ESTILOS DE TRANSICIÓN VUE */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* OPTIMIZACIÓN DE SCROLL */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }
</style>
