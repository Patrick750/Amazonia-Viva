import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazoniaviva.settings')
django.setup()

from autenticacion.models import Productos, Categorias, Proveedor, ProductoImagen

def update_products():
    email_proveedor = "proveer@gmail.com"
    try:
        proveedor = Proveedor.objects.get(email=email_proveedor)
        # Completar información del proveedor
        proveedor.nit = "900654321-5"
        proveedor.rut = "RUT-PROV-123"
        proveedor.descripcion = "Suministramos los mejores equipos para la exploración del Amazonas. Calidad garantizada para agencias y turistas."
        proveedor.horario_atencion = "Lunes a Viernes 8:00 AM - 6:00 PM"
        proveedor.informacion_contacto = {
            "whatsapp": "+573001234567",
            "instagram": "@amazonia_suministros",
            "facebook": "Amazonia Suministros Pro"
        }
        proveedor.save()
        print(f"Updated provider info for: {email_proveedor}", flush=True)
    except Proveedor.DoesNotExist:
        print(f"Provider {email_proveedor} not found.", flush=True)
        return

    # Características genéricas para enriquecer los productos
    specs_pool = {
        "Mochilas": {"material": "Nylon Ripstop", "impermeabilidad": "10000mm", "peso": "1.2kg"},
        "Calzado": {"suela": "Vibram", "transpirabilidad": "Alta", "ajuste": "Cordones rápidos"},
        "Iluminación": {"lúmenes": "500lm", "batería": "Recargable USB-C", "autonomía": "12h"},
        "Repelentes": {"componente": "Natural / Citronela", "duración": "4h por aplicación"},
        "Óptica": {"aumento": "10x", "lente": "42mm Multi-coated", "campo_vision": "110m/1000m"},
        "Camping": {"capacidad": "2-4 personas", "montaje": "Automático < 5 min", "protección_uv": "UPF 50+"},
        "Hidratación": {"capacidad": "1L", "filtro": "Carbón activado", "material": "Tritan libre de BPA"},
        "Seguridad": {"certificación": "ISO 9001", "contenido": "80 piezas", "empaque": "Estuche rígido"}
    }

    products = Productos.objects.filter(proveedor=proveedor)
    print(f"Updating {products.count()} products with detailed info...", flush=True)

    for p in products:
        # Asignar características según el nombre/SKU
        if "Mochila" in p.nombre: p.caracteristicas = specs_pool["Mochilas"]
        elif "Bota" in p.nombre: p.caracteristicas = specs_pool["Calzado"]
        elif "Linterna" in p.nombre: p.caracteristicas = specs_pool["Iluminación"]
        elif "Repelente" in p.nombre: p.caracteristicas = specs_pool["Repelentes"]
        elif "Binoculares" in p.nombre: p.caracteristicas = specs_pool["Óptica"]
        elif "Carpa" in p.nombre: p.caracteristicas = specs_pool["Camping"]
        elif "Kit" in p.nombre: p.caracteristicas = specs_pool["Seguridad"]
        elif "Botella" in p.nombre: p.caracteristicas = specs_pool["Hidratación"]
        else: p.caracteristicas = {"tipo": "General", "marca": "Amazonia Viva", "origen": "Nacional"}

        p.rating = random.choice([4.0, 4.5, 5.0, 4.8])
        p.save()

        # Añadir imagen (placeholder de Cloudinary o referencia dummy)
        # Nota: CloudinaryField espera un valor que se pueda convertir en CloudinaryResource
        if not ProductoImagen.objects.filter(producto=p).exists():
            ProductoImagen.objects.create(
                producto=p,
                es_portada=True,
                # Usaremos un ID de imagen genérico si Cloudinary está configurado
                # Si no, esto al menos deja la entrada en DB
                imagen="v1234567/sample_product_image" 
            )

    print("All products updated with specs, ratings, and dummy image records.", flush=True)

if __name__ == "__main__":
    update_products()
    print("Done!", flush=True)
