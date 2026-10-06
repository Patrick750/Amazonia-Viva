import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'https://api.adsoproject.dev/';
const clienteAxios = axios.create({ baseURL });
const tokenClient = axios.create({ baseURL });
let renovacion = null;

clienteAxios.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

clienteAxios.interceptors.response.use(response => response, async error => {
    const original = error.config;
    if (error.response?.status !== 401 || !original ||
        /(?:login|confirmar-password|token\/refresh)\//.test(original.url || '')) {
        return Promise.reject(error);
    }
    const refresh = localStorage.getItem('refresh_token');
    if (refresh && !original._reintentado) {
        original._reintentado = true;
        try {
            if (!renovacion) {
                renovacion = tokenClient.post('api/token/refresh/', { refresh }).then(({ data }) => {
                    localStorage.setItem('token', data.access);
                    localStorage.setItem('refresh_token', data.refresh);
                    return data.access;
                }).finally(() => { renovacion = null; });
            }
            const access = await renovacion;
            original.headers.Authorization = `Bearer ${access}`;
            // Logout debe invalidar el refresh recién rotado.
            if ((original.url || '').includes('/logout/')) {
                original.data = { refresh_token: localStorage.getItem('refresh_token') };
            }
            return clienteAxios(original);
        } catch {
            // La renovación inválida requiere un nuevo inicio de sesión.
        }
    }
    ['token', 'refresh_token', 'rol'].forEach(key => localStorage.removeItem(key));
    window.location.href = '/auth/login';
    return Promise.reject(error);
});

export default clienteAxios;
