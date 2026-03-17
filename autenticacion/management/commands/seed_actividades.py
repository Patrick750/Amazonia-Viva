from django.core.management.base import BaseCommand
from autenticacion.models import Categoria, Actividad  # <-- CAMBIA 'tu_app' por el nombre de tu app

class Command(BaseCommand):
    help = 'Puebla la base de datos con el catálogo inicial de categorías y actividades turísticas'

    def handle(self, *args, **kwargs):
        # Datos extraídos y adaptados del frontend
        actividades_data = [
            {"id": 1, "category": "Ecoturismo y Naturaleza", "name": "Avistamiento de aves", "risk": 2},
            {"id": 2, "category": "Ecoturismo y Naturaleza", "name": "Avistamiento de fauna silvestre", "risk": 3},
            {"id": 3, "category": "Ecoturismo y Naturaleza", "name": "Senderismo interpretativo", "risk": 3},
            {"id": 4, "category": "Ecoturismo y Naturaleza", "name": "Safaris fotográficos", "risk": 2},
            {"id": 5, "category": "Ecoturismo y Naturaleza", "name": "Caminatas nocturnas", "risk": 4},
            {"id": 6, "category": "Ecoturismo y Naturaleza", "name": "Visitas a reservas naturales", "risk": 2},
            {"id": 7, "category": "Fluvial y Acuático", "name": "Navegación tradicional en bote", "risk": 2},
            {"id": 8, "category": "Fluvial y Acuático", "name": "Kayak de travesía", "risk": 4},
            {"id": 9, "category": "Fluvial y Acuático", "name": "Rafting / Canotaje", "risk": 7},
            {"id": 10, "category": "Fluvial y Acuático", "name": "Tubing (descenso en neumáticos)", "risk": 5},
            {"id": 11, "category": "Fluvial y Acuático", "name": "Pesca deportiva (Catch & Release)", "risk": 3},
            {"id": 12, "category": "Fluvial y Acuático", "name": "Nado en cascadas y pozos naturales", "risk": 4},
            {"id": 13, "category": "Aventura y Reto Físico", "name": "Trekking de alta exigencia", "risk": 6},
            {"id": 14, "category": "Aventura y Reto Físico", "name": "Canopy / Tirolesa", "risk": 6},
            {"id": 15, "category": "Aventura y Reto Físico", "name": "Escalada en árboles (Tree climbing)", "risk": 6},
            {"id": 16, "category": "Aventura y Reto Físico", "name": "Espeleología (Exploración de cuevas)", "risk": 7},
            {"id": 17, "category": "Aventura y Reto Físico", "name": "Ciclomontañismo (MTB)", "risk": 5},
            {"id": 18, "category": "Aventura y Reto Físico", "name": "Cursos de supervivencia", "risk": 8},
            {"id": 19, "category": "Aventura y Reto Físico", "name": "Rappel en cascadas", "risk": 7},
            {"id": 20, "category": "Cultura y Comunidad", "name": "Convivencia con comunidades locales", "risk": 1},
            {"id": 21, "category": "Cultura y Comunidad", "name": "Talleres de artesanías locales", "risk": 1},
            {"id": 22, "category": "Cultura y Comunidad", "name": "Medicina tradicional y saberes", "risk": 1},
            {"id": 23, "category": "Cultura y Comunidad", "name": "Agroturismo (Rutas productivas)", "risk": 2},
            {"id": 24, "category": "Cultura y Comunidad", "name": "Gastronomía y clases de cocina", "risk": 1},
            {"id": 25, "category": "Cultura y Comunidad", "name": "Muestras folclóricas y mitos", "risk": 1},
            {"id": 26, "category": "Bienestar y Retiro", "name": "Retiros de yoga y meditación", "risk": 1},
            {"id": 27, "category": "Bienestar y Retiro", "name": "Terapias de bosque (Shinrin-yoku)", "risk": 1},
            {"id": 28, "category": "Bienestar y Retiro", "name": "Baños termales o lodoterapias", "risk": 2},
            {"id": 29, "category": "Urbano y Logístico", "name": "City tours históricos", "risk": 1},
            {"id": 30, "category": "Urbano y Logístico", "name": "Visitas a museos y centros de memoria", "risk": 1},
            {"id": 31, "category": "Urbano y Logístico", "name": "Recorridos de compras y mercados", "risk": 1}
        ]

        categorias_creadas = 0
        actividades_creadas = 0

        self.stdout.write(self.style.WARNING('Iniciando migración de datos...'))

        for item in actividades_data:
            # 1. Obtener o crear la Categoría
            categoria_obj, cat_created = Categoria.objects.get_or_create(
                nombre=item["category"]
            )
            if cat_created:
                categorias_creadas += 1

            # 2. Actualizar o crear la Actividad
            # Usamos update_or_create para que si ejecutas el script dos veces, 
            # no duplique las actividades, sino que las actualice si hubo cambios.
            actividad_obj, act_created = Actividad.objects.update_or_create(
                id=item["id"],
                defaults={
                    "nombre": item["name"],
                    "nivel_riesgo": item["risk"],
                    "categoria": categoria_obj
                }
            )
            if act_created:
                actividades_creadas += 1

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se crearon/verificaron {categorias_creadas} categorías y {actividades_creadas} actividades.'))