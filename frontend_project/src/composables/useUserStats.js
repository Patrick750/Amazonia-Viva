import { ref } from 'vue';
import axios from '@/api/axios';

// Estado global reactivo
const cartCount = ref(0);
const favoritesCount = ref(0);

export function useUserStats() {
    
    const updateStats = async () => {
        const token = localStorage.getItem('token');
        const rol = localStorage.getItem('rol');
        
        if (!token || (rol !== 'turista' && rol !== 'agencia')) {
            console.log('useUserStats: No hay token o el rol no es válido:', { token: !!token, rol });
            cartCount.value = 0;
            favoritesCount.value = 0;
            return;
        }

        try {
            console.log('useUserStats: Obteniendo estadísticas...');
            const response = await axios.get('api/user/stats/');
            console.log('useUserStats: Respuesta recibida:', response.data);
            cartCount.value = response.data.cart_count || 0;
            favoritesCount.value = response.data.favorites_count || 0;
        } catch (error) {
            console.error('Error al obtener estadísticas de usuario:', error);
        }
    };

    return {
        cartCount,
        favoritesCount,
        updateStats
    };
}
