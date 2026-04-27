<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import axios from '@/api/axios';
import VueApexCharts from "vue3-apexcharts";

// 1. OBTENCIÓN DEL ROL
// Obtiene el rol exacto guardado al iniciar sesión
const userRole = ref(localStorage.getItem('rol') || 'invitado');

// 2. LÓGICA INTERACTIVA (Brújula o Mariposa)
const interactiveElRef = ref(null);

onMounted(() => {
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let elX = window.innerWidth / 2;
  let elY = window.innerHeight / 2;
  let animationFrameId;

  const handleMouseMove = (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  };

  document.addEventListener('mousemove', handleMouseMove);

  const animateElement = () => {
    if (!interactiveElRef.value) return;
    
    elX += (mouseX - elX) * 0.04;
    elY += (mouseY - elY) * 0.04;
    
    const dx = mouseX - elX;
    const dy = mouseY - elY;
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    interactiveElRef.value.style.transform = `translate(${elX - 30}px, ${elY - 30}px) rotate(${angle + 90}deg)`;
    
    animationFrameId = requestAnimationFrame(animateElement);
  };

  animateElement();

  onUnmounted(() => {
    document.removeEventListener('mousemove', handleMouseMove);
    cancelAnimationFrame(animationFrameId);
  });
});

// 3. BASE DE DATOS LOCAL
const roleConfigs = {
  agencia: {
    header: {
      title: "Amazonia Viva",
      subtitle: "Gestión de Experiencias y Biodiversidad"
    },
    gridClass: "lg:grid-cols-4",
    theme: 'fauna',
    kpis: [
      {
        title: "Ingresos Totales", value: "$45.680.000",
        trend: "+18% este mes", trendType: "up",
        icon: '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        watermark: '<path d="M12,2C10.89,2 10,2.89 10,4V6H8.5a2.5,2.5 0 0 0 -2.5,2.5V11a2.5,2.5 0 0 0 2.5,2.5H10v7a2,2 0 0 0 4,0v-7h1.5a2.5,2.5 0 0 0 2.5,-2.5V8.5a2.5,2.5 0 0 0 -2.5,-2.5H14V4c0,-1.11 -0.89,-2 -2,-2Z"/>'
      },
      {
        title: "Tours Vendidos", value: "156",
        trend: "+12% este mes", trendType: "up",
        link: "/panel/gestion-reservas",
        icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        watermark: '<path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,19.93C7.06,19.43 4,16.05 4,12C4,7.95 7.06,4.57 11,4.07V19.93M13,4.07C16.94,4.57 20,7.95 20,12C20,16.05 16.94,19.43 13,19.93V4.07M15,10.5A1.5,1.5 0 0,0 16.5,12A1.5,1.5 0 0,0 18,10.5A1.5,1.5 0 0,0 16.5,9A1.5,1.5 0 0,0 15,10.5M16.5,13.5A1.5,1.5 0 0,0 18,15A1.5,1.5 0 0,0 19.5,13.5A1.5,1.5 0 0,0 18,12A1.5,1.5 0 0,0 16.5,13.5Z"/>'
      },
      {
        title: "Satisfacción Promedio", value: "4.8 ★",
        trend: "Basado en 89 reseñas", trendType: "neutral",
        icon: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>',
        watermark: '<path d="M22,12C22,12 21.36,10.58 20.35,9.65C19.35,8.72 18,8.22 18,8.22C18,8.22 16.89,7.5 15.68,7.21C14.47,6.91 13.16,7.05 13.16,7.05C13.16,7.05 11.5,6.67 10.15,6.58C8.81,6.48 7.5,6.67 7.5,6.67C7.5,6.67 6.13,6.33 4.88,6.29C3.62,6.25 2.5,6.5 2.5,6.5C2.5,6.5 3.39,8.22 4.14,9.65C4.89,11.08 5.39,12.5 5.39,12.5V14.17C5.39,14.17 5.72,15.58 6.72,16.52C7.73,17.45 9.06,17.95 9.06,17.95H11.58C11.58,17.95 12.92,18.29 14.17,18.25C15.42,18.21 16.56,17.78 16.56,17.78L19,16.52C19,16.52 20.36,15.11 20.86,13.68C21.36,12.25 21.36,10.82 21.36,10.82C21.36,10.82 22,12 22,12Z"/>'
      },
      {
        title: "Reservas Pendientes", value: "12",
        trend: "Requiere atención", trendType: "down",
        link: "/panel/gestion-reservas",
        icon: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        watermark: '<path d="M12,19.93A10,10 0 0,0 2,10A10,10 0 0,0 12,2.07A10,10 0 0,0 22,10A10,10 0 0,0 12,19.93M12,4.07V7.07C13.66,7.07 15,8.41 15,10.07S13.66,13.07 12,13.07V16.93C15.86,16.93 19,13.86 19,10S15.86,4.07 12,4.07M12,8.07C10.9,8.07 10,8.97 10,10.07S10.9,12.07 12,12.07V8.07Z"/>'
      }
    ]
  },
  proveedor: {
    header: {
      title: "Panel de Proveedor",
      subtitle: "Amazonia Viva · Gestión de Catálogo y Ventas"
    },
    gridClass: "lg:grid-cols-3",
    theme: 'turismo',
    kpis: [
      {
        title: "Total Productos Vendidos", value: "234",
        trend: "+12% desde el mes pasado", trendType: "neutral",
        link: "/panel/gestion-reservas",
        icon: '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>',
        watermark: '<path d="M20 6h-3V4c0-1.1-.9-2-2-2H9c-1.1 0-2 .9-2 2v2H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zM9 4h6v2H9V4zm11 15H4V8h16v11z"/><path d="M9 10h6v2H9z"/>'
      },
      {
        title: "Ingresos Totales", value: "$28.340.000",
        trend: "+18% desde el mes pasado", trendType: "neutral",
        icon: '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        watermark: '<path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/>'
      },
      {
        title: "Productos Activos", value: "4",
        trend: "En el catálogo actual", trendType: "neutral",
        icon: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
        watermark: '<path d="M12 2L2 20h20L12 2zm0 4.5l5.5 10h-11L12 6.5z"/>'
      },
      {
        title: "Pedidos Pendientes", value: "8",
        trend: "Requieren atención", trendType: "neutral",
        link: "/panel/gestion-reservas",
        icon: '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        watermark: '<path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z"/>'
      },
      {
        title: "Calificación Promedio", value: "4.7 ★",
        trend: "Basado en todas las reseñas", trendType: "neutral",
        icon: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        watermark: '<path d="M4 4h3l2-2h6l2 2h3c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm8 3c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 2c1.65 0 3 1.35 3 3s-1.35 3-3 3-3-1.35-3-3 1.35-3 3-3z"/>'
      },
      {
        title: "Total Clientes", value: "42",
        trend: "Clientes únicos atendidos", trendType: "neutral",
        icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        watermark: '<path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>'
      }
    ]
  },
  turista: {
    header: {
      title: "Hola, Viajero",
      subtitle: "Gestiona tus viajes y revive tus mejores momentos en la Amazonía"
    },
    gridClass: "lg:grid-cols-2",
    theme: 'turismo',
    kpis: [
      {
        title: "Mis Reservas", value: "Activas",
        trend: "Consulta tus próximos tours", trendType: "neutral",
        link: "/panel/reservas",
        icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        watermark: '<path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,19.93C7.06,19.43 4,16.05 4,12C4,7.95 7.06,4.57 11,4.07V19.93M13,4.07C16.94,4.57 20,7.95 20,12C20,16.05 16.94,19.43 13,19.93V4.07M15,10.5A1.5,1.5 0 0,0 16.5,12A1.5,1.5 0 0,0 18,10.5A1.5,1.5 0 0,0 16.5,9A1.5,1.5 0 0,0 15,10.5M16.5,13.5A1.5,1.5 0 0,0 18,15A1.5,1.5 0 0,0 19.5,13.5A1.5,1.5 0 0,0 18,12A1.5,1.5 0 0,0 16.5,13.5Z"/>'
      },
      {
        title: "Mis Experiencias", value: "Fotos y Reseñas",
        trend: "Ver fotos subidas por la agencia", trendType: "up",
        link: "/panel/mis-experiencias",
        icon: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline>',
        watermark: '<path d="M22,12C22,12 21.36,10.58 20.35,9.65C19.35,8.72 18,8.22 18,8.22C18,8.22 16.89,7.5 15.68,7.21C14.47,6.91 13.16,7.05 13.16,7.05C13.16,7.05 11.5,6.67 10.15,6.58C8.81,6.48 7.5,6.67 7.5,6.67C7.5,6.67 6.13,6.33 4.88,6.29C3.62,6.25 2.5,6.5 2.5,6.5C2.5,6.5 3.39,8.22 4.14,9.65C4.89,11.08 5.39,12.5 5.39,12.5V14.17C5.39,14.17 5.72,15.58 6.72,16.52C7.73,17.45 9.06,17.95 9.06,17.95H11.58C11.58,17.95 12.92,18.29 14.17,18.25C15.42,18.21 16.56,17.78 16.56,17.78L19,16.52C19,16.52 20.36,15.11 20.86,13.68C21.36,12.25 21.36,10.82 21.36,10.82C21.36,10.82 22,12 22,12Z"/>'
      }
    ]
  },
  invitado: {
    header: {
      title: "Bienvenido a Amazonia Viva",
      subtitle: "Descubre las maravillas de la selva amazónica"
    },
    gridClass: "lg:grid-cols-2",
    theme: 'turismo',
    kpis: [
      {
        title: "Tours Disponibles", value: "+50",
        trend: "Nuevas experiencias cada semana", trendType: "neutral",
        icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        watermark: '<path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,19.93C7.06,19.43 4,16.05 4,12C4,7.95 7.06,4.57 11,4.07V19.93M13,4.07C16.94,4.57 20,7.95 20,12C20,16.05 16.94,19.43 13,19.93V4.07M15,10.5A1.5,1.5 0 0,0 16.5,12A1.5,1.5 0 0,0 18,10.5A1.5,1.5 0 0,0 16.5,9A1.5,1.5 0 0,0 15,10.5M16.5,13.5A1.5,1.5 0 0,0 18,15A1.5,1.5 0 0,0 19.5,13.5A1.5,1.5 0 0,0 18,12A1.5,1.5 0 0,0 16.5,13.5Z"/>'
      },
      {
        title: "Destinos Únicos", value: "Amazonía",
        trend: "Turismo responsable y consciente", trendType: "neutral",
        icon: '<path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />',
        watermark: '<path d="M22,12C22,12 21.36,10.58 20.35,9.65C19.35,8.72 18,8.22 18,8.22C18,8.22 16.89,7.5 15.68,7.21C14.47,6.91 13.16,7.05 13.16,7.05C13.16,7.05 11.5,6.67 10.15,6.58C8.81,6.48 7.5,6.67 7.5,6.67C7.5,6.67 6.13,6.33 4.88,6.29C3.62,6.25 2.5,6.5 2.5,6.5C2.5,6.5 3.39,8.22 4.14,9.65C4.89,11.08 5.39,12.5 5.39,12.5V14.17C5.39,14.17 5.72,15.58 6.72,16.52C7.73,17.45 9.06,17.95 9.06,17.95H11.58C11.58,17.95 12.92,18.29 14.17,18.25C15.42,18.21 16.56,17.78 16.56,17.78L19,16.52C19,16.52 20.36,15.11 20.86,13.68C21.36,12.25 21.36,10.82 21.36,10.82C21.36,10.82 22,12 22,12Z"/>'
      }
    ]
  }
};

const kpisData = ref([]);
const chartData = ref({ labels: [], series: [] });
const monthlyChartData = ref({ labels: [], series: [] });
const selectedMonths = ref(12);
const filterMonth = ref(new Date().getMonth() + 1);
const filterYear = ref(new Date().getFullYear());
const isLoading = ref(true);

const fetchKPIs = async () => {
  isLoading.value = true;
  try {
    const { data } = await axios.get(`api/dashboard/stats/?months=${selectedMonths.value}&month=${filterMonth.value}&year=${filterYear.value}`);
    kpisData.value = data.kpis;
    if (data.chart_data) {
      chartData.value = data.chart_data;
    }
    if (data.monthly_chart_data) {
      monthlyChartData.value = data.monthly_chart_data;
    }
  } catch (error) {
    console.error('Error fetching dashboard KPIs:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchKPIs();
});

// Si el rol en localStorage no existe en el objeto, usa 'proveedor' de respaldo
const currentConfig = computed(() => {
  const config = JSON.parse(JSON.stringify(roleConfigs[userRole.value] || roleConfigs['proveedor']));
  
  if (kpisData.value.length > 0) {
    // Mapear los datos reales a los KPIs existentes para preservar iconos y links
    config.kpis = config.kpis.map(kpi => {
      const realKpi = kpisData.value.find(rk => rk.title === kpi.title);
      if (realKpi) {
        return {
          ...kpi,
          value: realKpi.value,
          trend: realKpi.trend,
          trendType: realKpi.trendType
        };
      }
      return kpi;
    });
  }
  
  return config;
});

const chartOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: false },
    sparkline: { enabled: false },
    fontFamily: 'Inter, sans-serif'
  },
  dataLabels: { enabled: false },
  stroke: { 
    curve: 'smooth', 
    width: 3, 
    lineCap: 'round'
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.6,
      opacityTo: 0.1,
      stops: [0, 90, 100],
      colorStops: [
        { offset: 0, color: '#10b880', opacity: 0.4 },
        { offset: 100, color: '#10b880', opacity: 0 },
      ]
    }
  },
  markers: {
    size: 5,
    colors: ['#0a1a0f'],
    strokeColors: '#10b880',
    strokeWidth: 3,
    hover: { size: 7 }
  },
  colors: ['#10b880'],
  xaxis: {
    categories: chartData.value.labels,
    axisBorder: { show: false },
    axisTicks: { show: false },
    labels: { style: { colors: 'rgba(255,255,255,0.6)', fontSize: '11px', fontWeight: 600 } }
  },
  yaxis: {
    labels: {
      style: { colors: 'rgba(255,255,255,0.6)', fontSize: '11px', fontWeight: 600 },
      formatter: (val) => `$${(val/1000).toFixed(0)}k`
    }
  },
  grid: { 
    show: true,
    borderColor: 'rgba(255, 255, 255, 0.05)', 
    strokeDashArray: 4,
    xaxis: { lines: { show: true } },
    yaxis: { lines: { show: true } },
    padding: { top: 10, right: 10, bottom: 0, left: 10 }
  },
  legend: {
    show: true,
    position: 'top',
    horizontalAlign: 'right',
    labels: { colors: 'rgba(255,255,255,0.7)', useSeriesColors: false },
    markers: { radius: 12, offsetX: -4 },
    itemMargin: { horizontal: 15, vertical: 0 }
  },
  tooltip: {
    theme: 'dark',
    x: { show: true },
    y: { formatter: (val) => `$${val.toLocaleString()}` },
    style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' }
  }
}));

const monthlyChartSeries = computed(() => monthlyChartData.value.series);

const monthlyChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'Inter, sans-serif',
    background: 'transparent',
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800,
    }
  },
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: '45%',
      distributed: true,
      dataLabels: { position: 'top' }
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => `$${(val/1000).toFixed(0)}k`,
    offsetY: -20,
    style: {
      fontSize: '10px',
      colors: ["#fff"],
      fontWeight: 900
    }
  },
  colors: ['#10b880', '#34d399', '#059669', '#10b880', '#34d399', '#059669'],
  xaxis: {
    categories: monthlyChartData.value.labels,
    axisBorder: { show: false },
    axisTicks: { show: false },
    labels: {
      rotate: -45,
      rotateAlways: monthlyChartData.value.labels.length > 10,
      style: { colors: 'rgba(255,255,255,0.6)', fontSize: '10px', fontWeight: 600 }
    }
  },
  yaxis: {
    labels: {
      style: { colors: 'rgba(255,255,255,0.6)', fontSize: '11px', fontWeight: 600 },
      formatter: (val) => `$${(val/1000).toFixed(0)}k`
    }
  },
  grid: {
    show: true,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    strokeDashArray: 4,
    xaxis: { lines: { show: false } },
    yaxis: { lines: { show: true } },
    padding: { top: 20, right: 10, bottom: 0, left: 10 }
  },
  legend: { show: false },
  tooltip: {
    theme: 'dark',
    y: { formatter: (val) => `$${val.toLocaleString()}` }
  },
  states: {
    hover: { filter: { type: 'lighten', value: 0.15 } },
    active: { filter: { type: 'none', value: 0 } }
  }
}));

</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] text-white p-6 md:p-10 overflow-x-hidden relative z-0">
    
    <div class="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
      
      <template v-if="currentConfig.theme === 'fauna'">
        <div class="macaw-wrapper">
          <svg viewBox="0 0 200 200" class="w-full h-full"><defs><linearGradient id="macaw-red" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ff0844" /><stop offset="100%" stop-color="#ffb199" /></linearGradient><linearGradient id="macaw-blue" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#00c6ff" /><stop offset="100%" stop-color="#0072ff" /></linearGradient></defs><path d="M40,180 L80,110 L95,130 Z" fill="url(#macaw-blue)"/><path d="M80,110 C 110,140 170,80 160,40 C 150,20 130,25 120,45 C 100,75 60,90 80,110 Z" fill="url(#macaw-red)"/><g class="macaw-wing"><path d="M110,65 C 145,85 160,145 130,125 C 110,105 95,85 110,65 Z" fill="#fceabb"/><path d="M120,75 C 150,95 150,135 130,115 C 120,95 110,85 120,75 Z" fill="url(#macaw-blue)"/></g><path d="M150,42 C 180,45 180,65 160,55 Z" fill="#1e293b"/></svg>
        </div>
        <div class="dolphin-wrapper">
          <svg viewBox="0 0 300 150" class="w-full h-full"><defs><linearGradient id="pink-dolphin" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#ff9a9e" /><stop offset="100%" stop-color="#fecfef" /></linearGradient></defs><path d="M20,100 C 50,130 90,100 130,110 C 200,125 250,70 290,95 C 280,60 220,50 170,60 C 140,50 150,20 130,40 C 100,65 50,75 20,100 Z" fill="url(#pink-dolphin)"/><path d="M150,85 C 170,120 135,125 150,85 Z" fill="#ff9a9e"/></svg>
        </div>
      </template>

      <template v-else-if="currentConfig.theme === 'turismo'">
        <div class="balloon-wrapper">
          <svg viewBox="0 0 200 200" class="w-full h-full opacity-60"><defs><linearGradient id="balloon-grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f59e0b" /><stop offset="100%" stop-color="#ea580c" /></linearGradient></defs><path d="M100,20 C 60,20 40,55 40,85 C 40,120 80,150 90,165 L110,165 C 120,150 160,120 160,85 C 160,55 140,20 100,20 Z" fill="url(#balloon-grad)"/><path d="M85,170 H115 V185 H85 Z" fill="#78350f"/><line x1="90" y1="165" x2="85" y2="170" stroke="#78350f" stroke-width="2"/><line x1="110" y1="165" x2="115" y2="170" stroke="#78350f" stroke-width="2"/></svg>
        </div>
        <div class="canoe-wrapper">
          <svg viewBox="0 0 300 150" class="w-full h-full opacity-50"><defs><linearGradient id="canoe-grad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#059669" /><stop offset="100%" stop-color="#10b981" /></linearGradient></defs><path d="M20,100 C 60,130 240,130 280,100 C 240,115 60,115 20,100 Z" fill="url(#canoe-grad)"/><path d="M120,70 L180,130" stroke="#b45309" stroke-width="4" stroke-linecap="round"/><ellipse cx="180" cy="130" rx="10" ry="5" fill="#b45309" transform="rotate(45 180 130)"/></svg>
        </div>
      </template>
    </div>

    <div ref="interactiveElRef" class="fixed top-0 left-0 w-[60px] h-[60px] pointer-events-none z-[9999]">
      <svg v-if="currentConfig.theme === 'fauna'" viewBox="0 0 100 100" class="morpho-wings w-full h-full drop-shadow-[0_10px_10px_rgba(0,180,255,0.3)]"><defs><linearGradient id="morpho-blue" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#00f2fe" /><stop offset="100%" stop-color="#4facfe" /></linearGradient></defs><path d="M50,40 C 30,10 10,20 15,50 C 30,55 45,45 50,40 Z" fill="url(#morpho-blue)"/><path d="M50,40 C 70,10 90,20 85,50 C 70,55 55,45 50,40 Z" fill="url(#morpho-blue)"/><path d="M50,45 C 35,60 20,80 30,90 C 40,80 48,60 50,45 Z" fill="url(#morpho-blue)"/><path d="M50,45 C 65,60 80,80 70,90 C 60,80 52,60 50,45 Z" fill="url(#morpho-blue)"/><ellipse cx="50" cy="45" rx="3" ry="15" fill="#1e293b"/></svg>
      <svg v-else viewBox="0 0 100 100" class="w-full h-full drop-shadow-[0_8px_15px_rgba(16,185,129,0.3)]"><circle cx="50" cy="50" r="45" fill="#0d2114" stroke="#10b981" stroke-width="3"/><circle cx="50" cy="50" r="38" fill="none" stroke="white" stroke-opacity="0.1" stroke-width="1"/><polygon points="50,15 40,50 60,50" fill="#ef4444"/><polygon points="50,85 40,50 60,50" fill="#475569"/><circle cx="50" cy="50" r="4" fill="#10b981"/></svg>
    </div>

    <main class="relative z-10 max-w-7xl mx-auto">
      
      <header class="mb-10 animate-fade-in-down flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 class="text-3xl font-bold text-white tracking-tight">{{ currentConfig.header.title }}</h1>
          <p class="text-white/45 mt-1">{{ currentConfig.header.subtitle }}</p>
        </div>
        
        <div class="flex items-center gap-3 bg-white/5 backdrop-blur-xl border border-white/10 p-2 rounded-2xl shadow-lg">
          <div class="flex flex-col px-2">
            <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-widest mb-1">Periodo</span>
            <div class="flex items-center gap-2">
              <select v-model="filterMonth" @change="fetchKPIs" class="bg-transparent text-sm font-bold text-white outline-none border-none cursor-pointer hover:text-emerald-400 transition-colors">
                <option v-for="(m, i) in ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']" 
                        :key="i" :value="i + 1" class="bg-[#0a1a0f]">{{ m }}</option>
              </select>
              <select v-model="filterYear" @change="fetchKPIs" class="bg-transparent text-sm font-bold text-white outline-none border-none cursor-pointer hover:text-emerald-400 transition-colors">
                <option v-for="y in [2024, 2025, 2026]" :key="y" :value="y" class="bg-[#0a1a0f]">{{ y }}</option>
              </select>
            </div>
          </div>
          <button @click="fetchKPIs" class="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl hover:bg-emerald-500 hover:text-white transition-all duration-300">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/>
            </svg>
          </button>
        </div>
      </header>

      <section class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6" :class="currentConfig.gridClass">
        
        <component :is="kpi.link ? 'router-link' : 'article'" 
                 v-for="(kpi, index) in currentConfig.kpis" :key="index" 
                 :to="kpi.link"
                 class="group relative overflow-hidden bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:bg-white/10 animate-fade-in-up block no-underline" 
                 :style="{ animationDelay: `${0.1 * (index + 1)}s` }">
          
          <svg class="absolute -bottom-4 -right-4 w-[120px] h-[120px] opacity-[0.08] z-0 pointer-events-none fill-white transition-all duration-400 group-hover:fill-emerald-400 group-hover:opacity-20 group-hover:-translate-x-2 group-hover:-translate-y-2 group-hover:scale-105" 
               viewBox="0 0 24 24" v-html="kpi.watermark"></svg>
          
          <div class="relative z-10 flex flex-col h-full justify-between">
            <div class="flex justify-between items-start mb-2">
                <h3 class="text-sm font-semibold text-white/70">{{ kpi.title }}</h3>
                <svg class="w-5 h-5 text-white/30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" v-html="kpi.icon"></svg>
            </div>
            
            <div class="text-3xl font-bold text-white my-2">{{ kpi.value }}</div>
            
            <div class="text-sm font-medium mt-auto" 
                 :class="{
                   'text-emerald-400': kpi.trendType === 'up',
                   'text-rose-400': kpi.trendType === 'down',
                   'text-slate-400': kpi.trendType === 'neutral'
                 }">
              {{ kpi.trend }}
            </div>
          </div>
        </component>

      </section>

      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up" style="animation-delay: 0.8s;">
        <div class="lg:col-span-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-white mb-4 pb-4 border-b border-white/5 relative z-10">Rendimiento Mensual</h2>
          <div class="relative z-10 h-[300px]">
             <VueApexCharts
              v-if="!isLoading && chartData.labels.length > 0"
              width="100%"
              height="100%"
              :options="chartOptions"
              :series="chartData.series"
            />
            <div v-else-if="isLoading" class="w-full h-full flex items-center justify-center text-slate-400">
              Cargando gráfico...
            </div>
            <div v-else class="w-full h-full flex items-center justify-center text-white/20 bg-white/5 rounded-xl border border-dashed border-white/10">
              No hay datos disponibles para el gráfico
            </div>
          </div>

          <!-- Nuevo Gráfico de Ganancias Mensuales -->
          <div class="mt-12 pt-8 border-t border-white/5">
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
              <div class="flex items-center gap-2">
                <h2 class="text-lg font-semibold text-white relative z-10 flex items-center gap-2">
                  <span class="w-2 h-6 bg-emerald-500 rounded-full"></span>
                  Ganancias Mensuales
                </h2>
              </div>
              
              <div class="flex items-center gap-3 bg-white/5 p-1 rounded-xl border border-white/10 relative z-20">
                <button v-for="range in [6, 12, 24, 36]" :key="range"
                        @click="selectedMonths = range; fetchKPIs()"
                        class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200"
                        :class="selectedMonths === range ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'text-white/40 hover:text-white/70 hover:bg-white/5'">
                  {{ range }}M
                </button>
              </div>
            </div>
            <div class="relative z-10 h-[320px]">
              <VueApexCharts
                v-if="!isLoading && monthlyChartData.labels.length > 0"
                width="100%"
                height="100%"
                :options="monthlyChartOptions"
                :series="monthlyChartSeries"
              />
              <div v-else-if="isLoading" class="w-full h-full flex items-center justify-center text-slate-400">
                Cargando datos mensuales...
              </div>
              <div v-else class="w-full h-full flex items-center justify-center text-white/20 bg-white/5 rounded-xl border border-dashed border-white/10">
                No hay suficientes datos históricos
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-white mb-4 pb-4 border-b border-white/5 relative z-10">Acciones Rápidas</h2>
          <div class="flex flex-col gap-3 relative z-10">
            <router-link v-if="userRole === 'agencia'" to="/panel/gestion-paquetes" class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl font-semibold text-white/80 text-sm transition-all duration-200 hover:bg-white/10 hover:border-emerald-500 hover:text-emerald-400 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
              Gestionar Catálogo
            </router-link>
            <router-link v-if="userRole === 'proveedor'" to="/panel/productos" class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl font-semibold text-white/80 text-sm transition-all duration-200 hover:bg-white/10 hover:border-emerald-500 hover:text-emerald-400 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
              Gestión de Productos
            </router-link>
            <router-link v-if="userRole === 'agencia' || userRole === 'proveedor'" to="/panel/gestion-reservas" class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl font-semibold text-white/80 text-sm transition-all duration-200 hover:bg-white/10 hover:border-emerald-500 hover:text-emerald-400 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
              Ver Ventas
            </router-link>
            <router-link v-if="userRole === 'agencia'" to="/panel/experiencias" class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl font-semibold text-white/80 text-sm transition-all duration-200 hover:bg-white/10 hover:border-emerald-500 hover:text-emerald-400 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
              Experiencias
            </router-link>
            <router-link v-if="userRole === 'turista'" to="/panel/mis-experiencias" class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl font-semibold text-white/80 text-sm transition-all duration-200 hover:bg-white/10 hover:border-emerald-500 hover:text-emerald-400 hover:translate-x-1">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
              Mis Experiencias
            </router-link>
            <!-- ── Liquidación / Billetera Virtual ── -->
            <router-link
              v-if="userRole === 'agencia' || userRole === 'proveedor'"
              to="/panel/liquidacion"
              class="flex items-center gap-3 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl font-semibold text-emerald-400 text-sm transition-all duration-200 hover:bg-emerald-500/20 hover:border-emerald-500 hover:text-emerald-300 hover:translate-x-1 shadow-sm shadow-emerald-500/10"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3z"/>
              </svg>
              Liquidación
            </router-link>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
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

.macaw-wrapper {
  position: absolute; width: 350px; height: 350px; animation: flyAcross 30s linear infinite; filter: drop-shadow(0 20px 30px rgba(0,0,0,0.15)); opacity: 0.8;
}
.macaw-wing { transform-origin: 50% 50%; animation: flapWing 0.4s ease-in-out infinite alternate; }
@keyframes flyAcross { 0% { transform: translate(-20vw, 110vh) scale(0.8) rotate(15deg); } 100% { transform: translate(110vw, -20vh) scale(1.2) rotate(-5deg); } }
@keyframes flapWing { 0% { transform: rotate(0deg) scaleY(1); } 100% { transform: rotate(-35deg) scaleY(0.6); } }

.dolphin-wrapper {
  position: absolute; width: 450px; height: 250px; bottom: 5%; left: -500px; animation: swimWave 35s ease-in-out infinite; opacity: 0.7; filter: blur(1px);
}
@keyframes swimWave { 0% { transform: translateX(0) translateY(0) rotate(5deg); } 25% { transform: translateX(40vw) translateY(-50px) rotate(-5deg); } 50% { transform: translateX(80vw) translateY(30px) rotate(5deg); } 100% { transform: translateX(120vw) translateY(-20px) rotate(-5deg); } }

.morpho-wings { transform-origin: center; animation: flutterFast 0.15s ease-in-out infinite alternate; }
@keyframes flutterFast { 0% { transform: scaleX(1); } 100% { transform: scaleX(0.2); } }

.balloon-wrapper {
  position: absolute; width: 250px; height: 250px; top: 10%; right: -300px; animation: floatBalloon 45s linear infinite; filter: drop-shadow(0 20px 30px rgba(0,0,0,0.1));
}
@keyframes floatBalloon { 0% { transform: translateX(0) translateY(0) rotate(-2deg); } 50% { transform: translateX(-60vw) translateY(-20px) rotate(2deg); } 100% { transform: translateX(-120vw) translateY(0) rotate(-2deg); } }

.canoe-wrapper {
  position: absolute; width: 350px; height: 150px; bottom: 10%; right: -400px; animation: rowCanoe 40s ease-in-out infinite; filter: blur(1px);
}
@keyframes rowCanoe { 0% { transform: translateX(0) translateY(0); } 50% { transform: translateX(-50vw) translateY(15px); } 100% { transform: translateX(-120vw) translateY(0); } }
</style>