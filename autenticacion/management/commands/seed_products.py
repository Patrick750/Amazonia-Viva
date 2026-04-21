import random
from django.core.management.base import BaseCommand
from autenticacion.models import Productos, Categorias, Proveedor, Usuario

class Command(BaseCommand):
    help = 'Crea un proveedor de prueba y puebla el catálogo de productos'

    def handle(self, *args, **options):
        email_proveedor = "proveer@gmail.com"
        try:
            proveedor = Proveedor.objects.get(email=email_proveedor)
            self.stdout.write(self.style.SUCCESS(f"Proveedor encontrado: {proveedor.nombre_empresa}"))
        except Proveedor.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Proveedor {email_proveedor} no encontrado. Creando proveedor de prueba..."))
            proveedor = Proveedor.objects.create(
                email=email_proveedor,
                username="proveedor_test",
                nombre_empresa="Suministros Amazonia",
                numero_telefonico="3001234567"
            )
            proveedor.set_password("pac131pap")
            proveedor.save()

        categorias = list(Categorias.objects.all())
        if not categorias:
            self.stdout.write(self.style.ERROR("No se encontraron categorías. Por favor, asegúrate de haber corrido las migraciones o creado categorías."))
            return

        # Listado de productos realistas para Turistas
        tourist_products = [
            ("Mochila Impermeable 40L", "MOCH-001", 120000, 30, 1),
            ("Botas de Trekking Selva", "BOTA-002", 250000, 20, 3),
            ("Linterna Frontal LED", "LINT-003", 45000, 50, 5),
            ("Repelente Natural 200ml", "REPE-004", 15000, 100, 4),
            ("Binoculares 10x42", "BINO-005", 350000, 15, 13),
            ("Hamaca con Mosquitero", "HAMA-006", 85000, 25, 6),
            ("Botella de Agua Filtrante", "BOTE-007", 95000, 40, 12),
            ("Sombrero de Explorador", "SOMB-008", 30000, 60, 11),
            ("Brújula de Alta Precisión", "BRUJ-009", 55000, 20, 14),
            ("Jersey de Secado Rápido", "ROPA-010", 65000, 45, 3)
        ]

        # Listado de productos realistas para Agencias
        agency_products = [
            ("Kit de Primeros Auxilios Grupal", "KIT-AG-001", 1200000, 5, 2),
            ("Carpa para 6 Personas", "CARP-AG-002", 850000, 10, 6),
            ("Balsa Inflable 8 pax", "BALS-AG-003", 4500000, 3, 7),
            ("Radio Satelital Pro", "RADI-AG-004", 2800000, 8, 14),
            ("Generador Eléctrico Portátil", "GENE-AG-005", 1500000, 4, 16),
            ("Chalecos Salvavidas Grupal (x10)", "CHAL-AG-006", 950000, 12, 10),
            ("Cocina de Campamento Pro", "COCI-AG-007", 450000, 15, 6),
            ("Set de Herramientas Supervivencia", "HERR-AG-008", 320000, 20, 16)
        ]

        self.stdout.write(self.style.SUCCESS("\nCreando productos para Turistas..."))
        for name, sku, price, stock, cat_id in tourist_products:
            try:
                cat = Categorias.objects.get(id=cat_id)
                if not Productos.objects.filter(sku=sku).exists():
                    Productos.objects.create(
                        nombre=name,
                        sku=sku,
                        precio=price,
                        stock=stock,
                        categorias=cat,
                        proveedor=proveedor,
                        tipo_catalogo='turistas',
                        disponible=True
                    )
                    self.stdout.write(f"  - Creado: {name}")
            except Categorias.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  - Error: Categoría ID {cat_id} no existe."))

        self.stdout.write(self.style.SUCCESS("\nCreando productos para Agencias..."))
        for name, sku, price, stock, cat_id in agency_products:
            try:
                cat = Categorias.objects.get(id=cat_id)
                if not Productos.objects.filter(sku=sku).exists():
                    Productos.objects.create(
                        nombre=name,
                        sku=sku,
                        precio=price,
                        stock=stock,
                        categorias=cat,
                        proveedor=proveedor,
                        tipo_catalogo='agencias',
                        disponible=True
                    )
                    self.stdout.write(f"  - Creado: {name}")
            except Categorias.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  - Error: Categoría ID {cat_id} no existe."))

        self.stdout.write(self.style.SUCCESS("\n¡Sembrado de productos completado con éxito!"))
