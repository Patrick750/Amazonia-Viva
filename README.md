# 🌿 Amazonia Viva

Versión: **5.0.6**

Plataforma web para la gestión y oferta de turismo amazónico. Conecta agencias, proveedores y turistas mediante una interfaz multi-rol con autenticación, paquetes turísticos y gestión de ventas.

## Problema y objetivos
Amazonia viva nace de la idea de integrar uns plataforma donde los turistas puedan encontrar paquetes turísticos y productos relacionados con el turismo amazónico, y las agencias puedan ofrecer sus servicios y productos a los turistas. Existen muchas agencias turisticas poco conocidas en el sur del pais, por lo que se busca darles visibilidad y ofrecer sus servicios a los turistas.



## 🛠️ Stack Tecnológico

- **Backend:** Django (Python 3.12) + Django REST Framework
- **Frontend:** Vue 3 + Vite + Vue Router
- **Base de datos:** PostgreSQL
- **Autenticación:** JWT / Sesiones Django
- **Servicios en la nube:** Cloudinary (Imágenes) + Github + Render + Neon 
- **Control de versiones:** Git
- **Despliegue:** Render

---

## 📦 Historial de Versiones

Ver [CHANGELOG.md](./CHANGELOG.md) para el historial completo.

## 🚀 Instalación y Ejecución

### Backend (Django)
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env a partir de .env.example (SECRET_KEY nueva y PostgreSQL).
# Para desarrollo local: DEBUG=true. Compras y retiros deshabilitados por defecto.
python manage.py migrate
python manage.py check
python manage.py test autenticacion
python manage.py runserver
```

### Frontend (Vue + Vite)
```bash
cd frontend_project

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

---

## 📄 Licencia

Este proyecto fue desarrollado como parte de un proyecto académico/estudiantil.

## Seguridad y operación

Ver [implementación y procedimiento operativo](documentacion/seguridad-implementada.md). El despliegue no carga datos de prueba. Wompi está integrado con checkout firmado y webhook verificado; su activación requiere claves de comercio y una validación real en sandbox. Para una demo aislada, usar DEBUG=true y CHECKOUT_MODE=demo y ejecutar `python manage.py setup_demo` explícitamente.

## Versionamiento automático

`VERSION` es la fuente de verdad. Los PR a main/master se integran con merge commit o rebase, sin squash. El bot incrementa por commit, sincroniza los archivos de versión y el changelog, y crea tags anotados:

| Declaración en commit | Incremento |
| --- | --- |
| `high [1.0.0]` | Mayor |
| `low [0.1.0]` | Menor |
| `parch [0.0.1]` o `patch [0.0.1]` | Parche |

Ejemplo: `feat(api): low [0.1.0] añadir búsquedas`. Los commits sin declaración no incrementan la versión. Ver [flujo, configuración y verificación](documentacion/versionamiento.md).
