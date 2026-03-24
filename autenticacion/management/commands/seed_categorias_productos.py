from django.core.management.base import BaseCommand
from autenticacion.models import Categorias

class Command(BaseCommand):
    help = 'Carga categorías base para los productos de Amazonía Viva'

    def handle(self, *args, **kwargs):
        categorias = [
            {'nombre': 'Artesanías', 'caracteristicas': {'descripcion': 'Productos elaborados a mano por artesanos locales, incluyendo tallas, tejidos y cerámicas.'}},
            {'nombre': 'Arte y Decoración', 'caracteristicas': {'descripcion': 'Obras de arte y elementos decorativos elaborados con materiales orgánicos locales.'}},
            {'nombre': 'Salud y Bienestar', 'caracteristicas': {'descripcion': 'Aceites esenciales, cremas y medicinas tradicionales basadas en plantas nativas.'}},
            {'nombre': 'Souvenirs y Recuerdos', 'caracteristicas': {'descripcion': 'Artículos pequeños para llevar como recuerdo del viaje (llaveros, postales, imanes).'}},
            {'nombre': 'Ropa y Textiles', 'caracteristicas': {'descripcion': 'Prendas con diseños autóctonos, camisetas, sombreros e indumentaria local.'}},
        ]

        count = 0
        for cat in categorias:
            obj, created = Categorias.objects.get_or_create(
                nombre=cat['nombre'],
                defaults={'caracteristicas': cat['caracteristicas']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Categoría creada: {obj.nombre}'))
                count += 1
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ La categoría {obj.nombre} ya existe.'))

        self.stdout.write(self.style.SUCCESS(f'¡Proceso completado! Se crearon {count} nuevas categorías.'))
