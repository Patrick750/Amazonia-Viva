import axios from 'axios';

// 1. Configuramos la URL base para no tener que escribir 'http://127.0.0.1:8000' en cada petición
const clienteAxios = axios.create({
    baseURL: 'http://127.0.0.1:8000/'
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

export default clienteAxios;