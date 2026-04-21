from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Ejecuta todos los comandos de sembrado para una configuración completa de la demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== INICIANDO CONFIGURACIÓN COMPLETA DE DEMO ==="))
        
        self.stdout.write("\n--- Paso 1: Sembrado de Usuarios ---")
        call_command('seed_users')
        
        self.stdout.write("\n--- Paso 2: Sembrado de Productos ---")
        call_command('seed_products')
        
        self.stdout.write("\n--- Paso 3: Enriquecimiento de Datos ---")
        call_command('enrich_data')
        
        self.stdout.write(self.style.SUCCESS("\n=== CONFIGURACIÓN DE DEMO FINALIZADA CON ÉXITO ==="))
