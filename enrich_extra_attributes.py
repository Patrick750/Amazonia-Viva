import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazoniaviva.settings')
django.setup()

from autenticacion.models import Productos, Categorias

def enrich_extras():
    print("Enriching category attributes...", flush=True)
    # 1. Enriquecer Categorías
    schema_map = {
        "Indumentaria": {"tallas": ["S", "M", "L", "XL"], "lavado": "Agua fría"},
        "Supervivencia": {"material": "Acero inoxidable", "filo": "Doble"},
        "Óptica": {"zoom": "10x", "lentes": "Anti-reflejo"},
        "Alimentación": {"vencimiento": "12 meses", "calorías": "500kcal"},
        "Campamento": {"personas": "2-4", "estaciones": "3"},
        "Fotografía": {"sensor": "CMOS", "resolución": "20MP"}
    }

    for c in Categorias.objects.all():
        for key, data in schema_map.items():
            if key in c.nombre:
                if not c.caracteristicas: c.caracteristicas = {}
                c.caracteristicas.update(data)
                c.save()
                print(f"  Updated Category: {c.nombre}", flush=True)

    # 2. Enriquecer Productos
    email_proveedor = "proveer@gmail.com"
    products = Productos.objects.filter(proveedor__email=email_proveedor)
    print(f"Enriching product extra attributes for {products.count()} products...", flush=True)

    for p in products:
        if not p.caracteristicas: p.caracteristicas = {}
        
        # Atributos comunes adicionales
        extra_info = {
            "Marca": "Amazonia Pro Gear",
            "Garantía": "12 meses",
            "Estado": "Nuevo",
            "Peso": f"{random.uniform(0.5, 3.0):.1f}kg",
            "Dimensiones": f"{random.randint(10,40)}x{random.randint(10,40)}x{random.randint(5,20)}cm",
            "Color": random.choice(["Ocre", "Verde Musgo", "Gris Piedra", "Negro"]),
            "Origen": "Amazonas, Colombia"
        }
        p.caracteristicas.update(extra_info)
        p.save()
        print(f"  Enriched Product: {p.nombre}", flush=True)

if __name__ == "__main__":
    enrich_extras()
    print("Done!", flush=True)
