# 🌿 Amazonia Viva

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

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Iniciar servidor
python manage.py seed_actividades
python manage.py seed_groups
python manage.py seed_categorias_paquetes
python manage.py seed_users
python manage.py seed_productos
python manage.py seed_paquetes
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
