import axios from 'axios';
console.log("Intentando conectar a:", import.meta.env.VITE_API_URL);

// 1. Configuramos la URL base para no tener que escribir 'http://127.0.0.1:8000' en cada petición
const baseURL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:9000/';
const clienteAxios = axios.create({
    baseURL: baseURL
});
// 2. Aquí creamos el "Guardia de Seguridad" (El Interceptor)
clienteAxios.interceptors.request.use(
    (config) => {
        // Buscamos el token en la memoria del navegador
        const token = localStorage.getItem('token');

        // Si el usuario tiene un token guardado, se lo pegamos a la petición
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
    },
    (error) => {
        // Si algo sale mal antes de enviar la petición, lo rechazamos
        return Promise.reject(error);
    }
);

// 3. Interceptor para manejar errores (como el token vencido)
clienteAxios.interceptors.response.use(
    (response) => {
        // Si la respuesta es exitosa, la pasamos tal cual
        return response;
    },
    (error) => {
        // Si el servidor responde con 401 (No autorizado), significa que el token expiró o es inválido
        // IMPORTANTE: No interceptamos errores del endpoint de login para permitir
        // que el componente login.vue muestre el mensaje de error al usuario
        if (error.response && error.response.status === 401) {
            const url = error.config?.url || '';
            
            // Saltar la redirección si es una petición al login
            if (url.includes('/login/')) {
                return Promise.reject(error);
            }
            
            console.warn("Sesión expirada. Redirigiendo al inicio de sesión...");
            
            // Limpiamos los datos de autenticación del navegador
            localStorage.clear();
            
            // Redirigimos al usuario al login
            // Usamos window.location.href para resetear completamente el estado de la aplicación
            window.location.href = '/auth/login';
        }
        
        return Promise.reject(error);
    }
);

export default clienteAxios;