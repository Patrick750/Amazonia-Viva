import json
import random
from django.core.management.base import BaseCommand
from autenticacion.models import Productos, Categorias, Proveedor, ProductoImagen

class Command(BaseCommand):
    help = 'Enriquece las categorías y productos con atributos detallados, valoraciones e imágenes'

    def handle(self, *args, **options):
        email_proveedor = "proveer@gmail.com"
        
        # 1. Enriquecer Categorías
        self.stdout.write(self.style.SUCCESS("Enriqueciendo atributos de categorías..."))
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
                    self.stdout.write(f"  - Categoría actualizada: {c.nombre}")

        # 2. Actualizar Información del Proveedor
        self.stdout.write(self.style.SUCCESS("\nActualizando información detallada del proveedor..."))
        try:
            proveedor = Proveedor.objects.get(email=email_proveedor)
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
            self.stdout.write(f"  - Perfil de proveedor actualizado: {email_proveedor}")
        except Proveedor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"  - Error: Proveedor {email_proveedor} no encontrado. Salteando paso de proveedor."))
            return

        # 3. Enriquecer Productos
        self.stdout.write(self.style.SUCCESS("\nEnriqueciendo productos con especificaciones y valoraciones..."))
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
        for p in products:
            # Atributos básicos generados dinámicamente
            if not p.caracteristicas: p.caracteristicas = {}
            
            # Asignar características específicas según el nombre
            if "Mochila" in p.nombre: p.caracteristicas.update(specs_pool["Mochilas"])
            elif "Bota" in p.nombre: p.caracteristicas.update(specs_pool["Calzado"])
            elif "Linterna" in p.nombre: p.caracteristicas.update(specs_pool["Iluminación"])
            elif "Repelente" in p.nombre: p.caracteristicas.update(specs_pool["Repelentes"])
            elif "Binoculares" in p.nombre: p.caracteristicas.update(specs_pool["Óptica"])
            elif "Carpa" in p.nombre: p.caracteristicas.update(specs_pool["Camping"])
            elif "Kit" in p.nombre: p.caracteristicas.update(specs_pool["Seguridad"])
            elif "Botella" in p.nombre: p.caracteristicas.update(specs_pool["Hidratación"])
            
            # Extra info global
            extra_info = {
                "Marca": "Amazonia Pro Gear",
                "Garantía": "12 meses",
                "Estado": "Nuevo",
                "Peso": f"{random.uniform(0.5, 3.0):.1f}kg",
                "Origen": "Amazonas, Colombia"
            }
            p.caracteristicas.update(extra_info)
            # p.rating = random.choice([4.0, 4.5, 5.0, 4.8])
            p.save()

            # 4. Imágenes dummy
            if not ProductoImagen.objects.filter(producto=p).exists():
                ProductoImagen.objects.create(
                    producto=p,
                    es_portada=True,
                    imagen="v1234567/sample_product_image" 
                )
            self.stdout.write(f"  - Producto enriquecido: {p.nombre}")

        self.stdout.write(self.style.SUCCESS("\n¡Enriquecimiento de datos completado con éxito!"))
