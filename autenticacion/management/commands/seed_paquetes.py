import random
import cloudinary.uploader
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from autenticacion.models import (
    Agencia, PaqueteTuristico, Actividad, CategoriaPaquete, DestinoTuristico
)

class Command(BaseCommand):
    help = 'Seeds the PaqueteTuristico table with realistic data and real Cloudinary uploads.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando sembrado de paquetes turísticos con carga a Cloudinary..."))

        # 1. Limpiar datos previos si es necesario (opcional, para evitar saturación de Cloudinary)
        # self.stdout.write("Limpiando paquetes previos...")
        # PaqueteTuristico.objects.all().delete()

        agencias = Agencia.objects.all()
        actividades = list(Actividad.objects.all())
        categorias_paquete = list(CategoriaPaquete.objects.all())

        if not agencias:
            self.stdout.write(self.style.ERROR("No hay agencias en la base de datos."))
            return

        if not actividades or not categorias_paquete:
            self.stdout.write(self.style.ERROR("No hay actividades o categorías. Verifica la inicialización."))
            return

        # 2. Pool de imágenes reales de Unsplash para subir a Cloudinary
        source_images = [
            "https://images.unsplash.com/photo-1590603740183-980e7f6920eb", # Amazon Jungle
            "https://images.unsplash.com/photo-1516426122078-c23e76319801", # River
            "https://images.unsplash.com/photo-1504618223053-559bdef9dd5a", # Birds
            "https://images.unsplash.com/photo-1520110120835-c9653da59030", # Dolphin
            "https://images.unsplash.com/photo-1518709268805-4e9042af9f23"  # Adventure
        ]

        self.stdout.write("Subiendo pool de imágenes a Cloudinary...")
        uploaded_images = []
        for i, url in enumerate(source_images):
            try:
                result = cloudinary.uploader.upload(
                    url,
                    folder="amazonia_viva/seeds/paquetes",
                    public_id=f"seed_tour_{i}_{random.randint(100, 999)}",
                    overwrite=True
                )
                uploaded_images.append(result['secure_url'])
                self.stdout.write(f"Imagen {i+1} subida: {result['secure_url']}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error subiendo imagen {i+1}: {e}"))

        if not uploaded_images:
            self.stdout.write(self.style.ERROR("No se pudo subir ninguna imagen a Cloudinary. Abortando."))
            return

        tours_data = [
            {"nombre": "Expedición Selva Profunda", "descripcion": "5 días en el corazón de la Amazonía.", "precio": 1250000, "duracion": "5 días", "capacidad": 12, "ubicacion": "Leticia"},
            {"nombre": "Aventura en el Río Yavari", "descripcion": "Navegación y avistamiento de delfines.", "precio": 850000, "duracion": "3 días", "capacidad": 15, "ubicacion": "Puerto Nariño"},
            {"nombre": "Caminata Ancestral Tikuna", "descripcion": "Cultura y leyendas locales.", "precio": 450000, "duracion": "2 días", "capacidad": 10, "ubicacion": "Resguardo Tikuna"},
            {"nombre": "Safari Fotográfico", "descripcion": "Búsqueda de jaguares y fauna.", "precio": 2100000, "duracion": "4 días", "capacidad": 6, "ubicacion": "Palmarí"},
            {"nombre": "Birdwatching Amacayacu", "descripcion": "Observación de aves exóticas.", "precio": 600000, "duracion": "1 día", "capacidad": 8, "ubicacion": "Amacayacu"}
        ]

        for agencia in agencias:
            self.stdout.write(f"Procesando agencia: {agencia.nombre_agencia}")
            num_paquetes = random.randint(2, 3) # Reducimos para no saturar
            
            for _ in range(num_paquetes):
                base = random.choice(tours_data)
                fecha = date.today() + timedelta(days=random.randint(10, 60)) if random.random() > 0.5 else None

                paquete = PaqueteTuristico.objects.create(
                    nombre=f"{base['nombre']} - {agencia.nombre_agencia[:10]}",
                    descripcion=base['descripcion'],
                    precio=Decimal(base['precio'] + random.randint(-50000, 50000)),
                    duracion=base['duracion'],
                    capacidad=base['capacidad'],
                    ubicacion=base['ubicacion'],
                    latitud=Decimal(random.uniform(-4.5, -3.5)),
                    longitud=Decimal(random.uniform(-70.5, -69.5)),
                    fecha_realizacion=fecha,
                    agencia=agencia,
                    categoria_paquete=random.choice(categorias_paquete),
                    itinerario=[{"time": "08:00", "activity": "Inicio del tour"}],
                    incluido=[{"item": "Todo incluido"}],
                    # rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.0')),
                    activo=True
                )
                paquete.actividades.set(random.sample(actividades, k=3))

                # Asignar imagen del pool subido
                DestinoTuristico.objects.create(
                    paquete=paquete,
                    imagen=random.choice(uploaded_images),
                    es_portada=True
                )

        self.stdout.write(self.style.SUCCESS("Sembrado con Cloudinary completado con éxito."))
