from django.conf import settings
from django.core.management.base import CommandError
import random
import cloudinary.uploader
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from autenticacion.models import (
    Agencia, PaqueteTuristico, Actividad, CategoriaPaquete, DestinoTuristico,
    ModalidadTurismo,
)

TOURS_DATA = [
    {
        "nombre": "Expedición Selva Profunda", "descripcion": "5 días en el corazón de la Amazonía.",
        "precio": 1250000, "duracion": "5 días", "capacidad": 12, "ubicacion": "Leticia",
        "modalidades": ["naturaleza"],
        "requisitos": "Condición física básica y mayores de 12 años. Vacunación de fiebre amarilla al día.",
        "condiciones": "Sujeto al nivel de los ríos y al pronóstico meteorológico; el guía puede ajustar la ruta.",
        "medidas": "Guía acreditado, botiquín, comunicación satelital y protocolo de evacuación fluvial.",
        "sostenibilidad": "Grupos reducidos, manejo de residuos y respeto de las zonas de fauna.",
    },
    {
        "nombre": "Aventura en el Río Yavari", "descripcion": "Navegación y avistamiento de delfines.",
        "precio": 850000, "duracion": "3 días", "capacidad": 15, "ubicacion": "Puerto Nariño",
        "modalidades": ["nautico", "naturaleza"],
        "requisitos": "Saber nadar o usar chaleco durante todo el recorrido. Mayores de 8 años.",
        "condiciones": "El recorrido depende del caudal y de la visibilidad del río.",
        "medidas": "Chalecos salvavidas por participante, lancha con motor de respaldo y guía con primeros auxilios.",
        "sostenibilidad": "Velocidad reducida cerca de la fauna y prohibición de alimentar animales.",
    },
    {
        "nombre": "Caminata Ancestral Tikuna", "descripcion": "Cultura y leyendas locales.",
        "precio": 450000, "duracion": "2 días", "capacidad": 10, "ubicacion": "Resguardo Tikuna",
        "modalidades": ["cultural", "rural"],
        "requisitos": "Respeto por las normas de la comunidad. Calzado cerrado para caminata ligera.",
        "condiciones": "La visita se coordina con la autoridad del resguardo y puede reprogramarse.",
        "medidas": "Acompañamiento de guía local, hidratación y punto de descanso durante la caminata.",
        "sostenibilidad": "Beneficio directo para la comunidad y consumo de productos locales.",
    },
    {
        "nombre": "Safari Fotográfico", "descripcion": "Búsqueda de jaguares y fauna.",
        "precio": 2100000, "duracion": "4 días", "capacidad": 6, "ubicacion": "Palmarí",
        "modalidades": ["naturaleza"],
        "requisitos": "Paciencia y capacidad para caminar en terreno irregular. Mayores de 14 años.",
        "condiciones": "El avistamiento de fauna no está garantizado y depende de las condiciones del día.",
        "medidas": "Distancia mínima de seguridad con la fauna, guía especializado y botiquín.",
        "sostenibilidad": "Sin cebos ni llamadas artificiales; observación a distancia.",
    },
    {
        "nombre": "Birdwatching Amacayacu", "descripcion": "Observación de aves exóticas.",
        "precio": 600000, "duracion": "1 día", "capacidad": 8, "ubicacion": "Amacayacu",
        "modalidades": ["naturaleza"],
        "requisitos": "Sin requisitos físicos especiales. Se recomienda llevar binoculares.",
        "condiciones": "Salida al amanecer; se cancela con lluvia fuerte.",
        "medidas": "Guía ornitólogo, ruta señalizada y hora de regreso definida.",
        "sostenibilidad": "Silencio en los puntos de observación y no perturbar los nidos.",
    },
]

BASE_GENERICA = {
    "modalidades": ["naturaleza"],
    "requisitos": "Condición física básica. Consulta con la agencia antes de reservar.",
    "condiciones": "Sujeto a las condiciones climáticas y de seguridad del día.",
    "medidas": "Guía acreditado, botiquín de primeros auxilios y protocolo de respuesta.",
    "sostenibilidad": "Manejo responsable de residuos y respeto por la fauna y la flora.",
}


def construir_estandar(base, actividades, referencia):
    """Devuelve los campos de MEJ-003 con la misma forma que guarda la API.

    ``objects.create`` no pasa por el serializer, por lo que aquí se aplican las
    mismas reglas: una ficha por actividad con un nivel de su propia escala y,
    para turismo de aventura, la modalidad y la certificación de demostración.
    """
    aventura = [actividad for actividad in actividades if actividad.es_turismo_aventura]
    modalidades = list(base["modalidades"])
    if aventura and "aventura" not in modalidades:
        modalidades.append("aventura")

    clasificacion = []
    for actividad in actividades:
        opciones = [o for o in actividad.opciones_dificultad if isinstance(o, dict) and "value" in o]
        nivel = str(opciones[len(opciones) // 2]["value"]) if opciones else ""
        clasificacion.append({
            "actividad_id": actividad.pk,
            "sistema": actividad.sistema_dificultad,
            "nivel": nivel,
            "descripcion": f"Dato de demostración para {actividad.nombre}.",
        })

    if aventura:
        certificacion = {
            "estado": "vigente",
            "organismo": "Organismo evaluador de demostración",
            "codigo": f"DEMO-{referencia}",
            "vigente_hasta": (date.today() + timedelta(days=365)).isoformat(),
        }
    else:
        certificacion = {"estado": "no_aplica", "organismo": "", "codigo": "", "vigente_hasta": ""}

    return {
        "modalidades_turismo": modalidades,
        "clasificacion_actividades": clasificacion,
        "requisitos_participantes": base["requisitos"],
        "condiciones_operacion": base["condiciones"],
        "medidas_seguridad": base["medidas"],
        "informacion_sostenibilidad": base["sostenibilidad"],
        "certificacion_aventura": certificacion,
    }


class Command(BaseCommand):
    help = (
        'Seeds the PaqueteTuristico table with realistic data and real Cloudinary uploads. '
        'Con --completar-existentes solo rellena los campos del estándar MEJ-003.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--completar-existentes',
            action='store_true',
            help='Completa modalidades, fichas técnicas y soportes de los paquetes sin crear ni subir imágenes.',
        )

    def verificar_catalogo(self):
        existentes = set(ModalidadTurismo.objects.filter(activa=True).values_list('codigo', flat=True))
        requeridas = {codigo for base in TOURS_DATA for codigo in base["modalidades"]} | {"aventura"}
        faltantes = requeridas - existentes
        if faltantes:
            raise CommandError(
                f"Faltan modalidades en el catálogo ({', '.join(sorted(faltantes))}). "
                "Ejecuta primero: python manage.py seed_estandar_paquetes"
            )

    def completar_existentes(self):
        self.verificar_catalogo()
        actualizados = 0
        for paquete in PaqueteTuristico.objects.prefetch_related('actividades'):
            if paquete.modalidades_turismo:
                continue
            base = next((b for b in TOURS_DATA if paquete.nombre.startswith(b["nombre"])), BASE_GENERICA)
            campos = construir_estandar(base, list(paquete.actividades.all()), paquete.pk)
            # update() evita que save() reactive o desactive el paquete por su fecha.
            PaqueteTuristico.objects.filter(pk=paquete.pk).update(**campos)
            actualizados += 1
        self.stdout.write(self.style.SUCCESS(f"Paquetes completados con el estándar MEJ-003: {actualizados}."))

    def handle(self, *args, **options):
        if not settings.DEBUG or settings.CHECKOUT_MODE != 'demo':
            raise CommandError('Datos de demostración requieren DEBUG=true y CHECKOUT_MODE=demo en una base aislada.')
        if options['completar_existentes']:
            self.completar_existentes()
            return
        self.verificar_catalogo()
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

        for agencia in agencias:
            self.stdout.write(f"Procesando agencia: {agencia.nombre_agencia}")
            num_paquetes = random.randint(2, 3) # Reducimos para no saturar

            for _ in range(num_paquetes):
                base = random.choice(TOURS_DATA)
                fecha = date.today() + timedelta(days=random.randint(10, 60)) if random.random() > 0.5 else None
                seleccion = random.sample(actividades, k=3)

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
                    rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.0')),
                    activo=True,
                    **construir_estandar(base, seleccion, f"{agencia.pk}-{random.randint(1000, 9999)}"),
                )
                paquete.actividades.set(seleccion)

                # Asignar imagen del pool subido
                DestinoTuristico.objects.create(
                    paquete=paquete,
                    imagen=random.choice(uploaded_images),
                    es_portada=True
                )

        self.stdout.write(self.style.SUCCESS("Sembrado con Cloudinary completado con éxito."))
