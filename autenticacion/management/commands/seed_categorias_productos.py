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
            (6, 'Campamento y pernocta', 'Carpas, sacos de dormir, aislantes y equipos para acampar.'),
            (7, 'Actividades acuáticas', 'Chalecos salvavidas, kayaks, balsas y equipo acuático.'),
            (8, 'Senderismo y exploración', 'Bastones de trekking y equipo para caminatas largas.'),
            (9, 'Observación de flora y fauna', 'Binoculares, lentes especiales y guías de campo.'),
            (10, 'Seguridad y primeros aux', 'Botiquines, repelentes y equipo médico de emergencia.'),
            (11, 'Indumentaria y calzado', 'Ropa de secado rápido, botas y protección climática.'),
            (12, 'Alimentación e hidratación', 'Filtros de agua, cocinillas y provisiones de expedición.'),
            (13, 'Fotografía y óptica', 'Cámaras, protectores contra agua y trípodes.'),
            (14, 'Comunicaciones y orientación', 'Radios, brújulas y mapas topográficos.'),
            (15, 'Transporte y logística', 'Mochilas de transporte, cuerdas y fundas impermeables.'),
            (16, 'Supervivencia y herramientas', 'Cuchillos, machetes, herramientas multiuso y cuerda.'),
        ]

        # Eliminar si hay sobrantes
        Categorias.objects.filter(id__gt=16).delete()

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
