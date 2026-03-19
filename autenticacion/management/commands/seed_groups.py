from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crea los grupos base de usuarios (Roles) para la plataforma: Turista, Agencia y Proveedor'

    def handle(self, *args, **kwargs):
        # Lista de los roles que necesita tu plataforma
        roles_base = ['turista', 'agencia', 'proveedor']
        grupos_creados = 0

        self.stdout.write(self.style.WARNING('Iniciando creación de grupos (Roles)...'))

        for nombre_rol in roles_base:
            # get_or_create busca el grupo, si no existe, lo crea automáticamente
            grupo, creado = Group.objects.get_or_create(name=nombre_rol)
            
            if creado:
                self.stdout.write(self.style.SUCCESS(f'✅ Grupo "{nombre_rol}" creado exitosamente.'))
                grupos_creados += 1
            else:
                self.stdout.write(self.style.NOTICE(f'ℹ️ El grupo "{nombre_rol}" ya existía.'))

        self.stdout.write(self.style.SUCCESS(f'¡Proceso completado! Se crearon {grupos_creados} grupos nuevos.'))