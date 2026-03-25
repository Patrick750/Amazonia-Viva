from django.core.management.base import BaseCommand
from autenticacion.models import CategoriaPaquete

CATEGORIAS = {
    "Naturaleza y Conservación": [
        "Ecoturismo general",
        "Avistamiento de aves (Birdwatching)",
        "Safaris fotográficos (Observación de flora y fauna endémica)",
        "Expediciones botánicas",
        "Turismo de conservación y voluntariado ecológico",
    ],
    "Aventura Acuática": [
        "Navegación fluvial y cruceros de río",
        "Canotaje y Kayak",
        "Rafting / Rápidos",
        "Pesca deportiva y artesanal",
        "Tubing (Descenso en neumáticos)",
    ],
    "Aventura Terrestre y Extrema": [
        "Senderismo y Trekking (Caminatas ecológicas)",
        "Supervivencia y expedición extrema",
        "Canopy / Tirolesa y puentes colgantes",
        "Ciclomontañismo (Mountain Bike)",
        "Espeleología (Exploración de cuevas y cavernas)",
    ],
    "Cultura y Comunidad": [
        "Etnoturismo (Inmersión en comunidades indígenas o locales)",
        "Rutas históricas y arqueológicas",
        "Talleres artesanales y aprendizaje de saberes ancestrales",
        "Turismo rural comunitario",
    ],
    "Gastronomía y Agroturismo": [
        "Rutas gastronómicas y degustación de ingredientes típicos",
        "Agroturismo (Recorridos por cultivos tradicionales, rutas del cacao, café, etc.)",
        "Clases de cocina tradicional en origen",
    ],
    "Bienestar y Conexión": [
        "Turismo místico y chamanismo (Medicina tradicional)",
        "Retiros de conexión natural (Yoga, meditación en la selva)",
        "Estancias en Ecolodges y Glamping",
        "Termales, cascadas y spas naturales",
    ],
    "Especializados y de Nicho": [
        "Turismo científico y de investigación",
        "Turismo astronómico (Observación de cielos nocturnos)",
        "Fotografía nocturna y paisajística",
    ],
}


class Command(BaseCommand):
    help = "Pobla la tabla CategoriaPaquete con las categorías y subcategorías de paquetes turísticos."

    def handle(self, *args, **kwargs):
        creadas = 0
        existentes = 0

        for grupo, subcategorias in CATEGORIAS.items():
            for nombre in subcategorias:
                obj, created = CategoriaPaquete.objects.get_or_create(
                    nombre=nombre,
                    defaults={"grupo": grupo}
                )
                if created:
                    creadas += 1
                    self.stdout.write(self.style.SUCCESS(f"  [+] {grupo} > {nombre}"))
                else:
                    existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeed completado: {creadas} categorias creadas, {existentes} ya existian."
            )
        )
