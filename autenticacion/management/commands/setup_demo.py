from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Ejecuta todos los comandos de sembrado para una configuración completa de la demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== INICIANDO CONFIGURACIÓN COMPLETA DE DEMO ==="))
        
        self.stdout.write("\n--- Paso 1: Sembrado de Usuarios ---")
        call_command('seed_users')

        self.stdout.write("\n--- Paso 2: Sembrado de Actividades ---")
        call_command('seed_actividades')      

        self.stdout.write("\n--- Paso 3: Sembrado de Categorías de paquetes ---")
        call_command('seed_categorias_paquetes')      

        self.stdout.write("\n--- Paso 4: Sembrado de Categorías de productos ---")
        call_command('seed_categorias_productos')  
        
        self.stdout.write("\n--- Paso 5: Sembrado de Productos ---")
        call_command('seed_products')
        
        self.stdout.write("\n--- Paso 6: Enriquecimiento de Datos ---")
        call_command('enrich_data')

        self.stdout.write("\n--- Paso 7: Sembrado de paquetes ---")
        call_command('seed_paquetes')

        self.stdout.write("\n--- Paso 8: Sembrado de ventas ---")
        call_command('seed_ventas')

        self.stdout.write("\n--- Paso 9: Sembrado de compras de agencias ---")
        call_command('seed_compras_agencias')
        
        self.stdout.write(self.style.SUCCESS("\n=== CONFIGURACIÓN DE DEMO FINALIZADA CON ÉXITO ==="))
