from django.core.management.base import BaseCommand
from autenticacion.models import Categorias

class Command(BaseCommand):
    help = 'Actualiza las categorías base a implementos de seguridad y turismo'

    def handle(self, *args, **kwargs):
        categorias = [
            (1, 'Equipos de Supervivencia', 'Implementos críticos para expediciones en la selva, como kits de fuego, purificadores de agua y mantas térmicas.'),
            (2, 'Seguridad y Primeros Auxilios', 'Kits médicos, antivenenos básicos, repelentes industriales y equipos de señalización de emergencia.'),
            (3, 'Indumentaria Outdoor', 'Ropa técnica, botas de trekking, ponchos impermeables y protectores para entornos húmedos.'),
            (4, 'Accesorios de Viaje', 'Mochilas tácticas, linternas frontales, cantimploras, brújulas y binoculares de campo exploratorio.'),
            (5, 'Tecnología y Navegación', 'Dispositivos GPS, localizadores satelitales (SPOT), walkie-talkies y baterías solares portátiles.'),
        ]

        # Eliminar si hay sobrantes
        Categorias.objects.filter(id__gt=5).delete()

        count = 0
        for cat_id, nombre, desc in categorias:
            obj, created = Categorias.objects.update_or_create(
                id=cat_id,
                defaults={
                    'nombre': nombre,
                    'caracteristicas': {'descripcion': desc}
                }
            )
            count += 1
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Categoría creada: {nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'🔄 Categoría actualizada: {nombre}'))

        self.stdout.write(self.style.SUCCESS(f'¡Proceso completado! Se sincronizaron {count} categorías de seguridad turística.'))
