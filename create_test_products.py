import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazoniaviva.settings')
django.setup()

from autenticacion.models import Productos, Categorias, Proveedor, Usuario

def create_products():
    email_proveedor = "proveer@gmail.com"
    try:
        proveedor = Proveedor.objects.get(email=email_proveedor)
        print(f"Found provider: {proveedor.nombre_empresa}", flush=True)
    except Proveedor.DoesNotExist:
        print(f"Provider {email_proveedor} not found. Creating a dummy provider...", flush=True)
        # Create provider if it doesn't exist
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
        print("No categories found. Please run migrations or create categories first.", flush=True)
        return

    # List of realistic products for Tourists
    tourist_products = [
        ("Mochila Impermeable 40L", "MOCH-001", 120000, 30, 1), # (Name, SKU, Price, Stock, CategoryID)
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

    # List of realistic products for Agencies
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

    print("Creating products for Tourists...", flush=True)
    for name, sku, price, stock, cat_id in tourist_products:
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
            print(f"  Created: {name}", flush=True)

    print("Creating products for Agencies...", flush=True)
    for name, sku, price, stock, cat_id in agency_products:
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
            print(f"  Created: {name}", flush=True)

if __name__ == "__main__":
    create_products()
    print("Done!", flush=True)
