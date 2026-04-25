from django.core.management.base import BaseCommand
from autenticacion.models import PaqueteTuristico, Productos, ExperienciaCalificacion

class Command(BaseCommand):
    help = 'Elimina las reseñas falsas y resetea las valoraciones de paquetes y productos.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando limpieza de reseñas...")

        # 1. Resetear ratings de Paquetes
        paquetes_count = PaqueteTuristico.objects.filter(rating__gt=0).count()
        PaqueteTuristico.objects.all().update(rating=0)
        self.stdout.write(self.style.SUCCESS(f"Se resetearon los ratings de {paquetes_count} paquetes."))

        # 2. Resetear ratings de Productos
        productos_count = Productos.objects.filter(rating__gt=0).count()
        Productos.objects.all().update(rating=0)
        self.stdout.write(self.style.SUCCESS(f"Se resetearon los ratings de {productos_count} productos."))

        # 3. Eliminar registros de ExperienciaCalificacion
        calif_count = ExperienciaCalificacion.objects.count()
        ExperienciaCalificacion.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Se eliminaron {calif_count} reseñas del sistema."))

        self.stdout.write(self.style.SUCCESS("¡Limpieza completada con éxito!"))
