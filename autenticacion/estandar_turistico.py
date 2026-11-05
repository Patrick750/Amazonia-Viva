"""Catálogo verificable que respalda la ficha técnica de paquetes de MEJ-003.

Las escalas se mantienen separadas por actividad. ``nivel_riesgo`` continúa siendo
una referencia interna del catálogo y no se presenta como clasificación normativa.
"""

ESTANDAR_PAQUETES = {
    "clave": "mej-003",
    "version": "2026-10-16",
    "nombre": "Ficha técnica de seguridad y dificultad por actividad",
    "proposito": (
        "Registrar información clara para el viajero y conservar la clasificación "
        "técnica propia de cada actividad sin mezclar escalas diferentes."
    ),
}

MODALIDADES_TURISMO = [
    {"value": "naturaleza", "label": "Naturaleza y ecoturismo", "description": "Fauna, flora silvestre, avistamiento de aves y reservas naturales."},
    {"value": "aventura", "label": "Turismo de aventura", "description": "Rafting, canopy, rappel y actividades de reto físico o técnico."},
    {"value": "cultural", "label": "Turismo cultural", "description": "Pueblos originarios, artesanías, memoria y saberes ancestrales."},
    {"value": "rural", "label": "Turismo rural", "description": "Convivencia con comunidades locales y vida tradicional del campo."},
    {"value": "agroturismo", "label": "Agroturismo", "description": "Fincas productivas, cosechas, cacao y frutos amazónicos."},
    {"value": "bienestar", "label": "Bienestar y reconexión", "description": "Retiros, descanso, baños de bosque y experiencias de reconexión."},
    {"value": "nautico", "label": "Turismo náutico", "description": "Kayak, navegación en botes tradicionales y pesca deportiva."},
    {"value": "reuniones", "label": "Reuniones y eventos", "description": "Encuentros corporativos, expediciones guiadas y talleres grupales."},
]

FUENTES_ESTANDAR = [
    {
        "codigo": "resolucion-0612-2024",
        "titulo": "Resolución 0612 de 2024",
        "entidad": "Ministerio de Comercio, Industria y Turismo",
        "alcance": "Programa Nacional de Calidad Turística y niveles de certificación.",
        "url": "https://www.mincit.gov.co/prensa/noticias/turismo/servicios-turismo-aventura-certificacion-seguridad",
        "verificada": True,
    },
    {
        "codigo": "nts-agencias-viajes",
        "titulo": "Normas Técnicas Sectoriales para agencias de viajes",
        "entidad": "Ministerio de Comercio, Industria y Turismo",
        "alcance": "Índice oficial de las NTS-AV 010 a 015 por actividad de aventura.",
        "url": "https://www.mincit.gov.co/minturismo/calidad-y-desarrollo-sostenible/calidad-turistica/normas-tecnicas-sectoriales/nts-agencias-de-viajes-1",
        "verificada": True,
    },
    {
        "codigo": "directorio-onac",
        "titulo": "Directorio Oficial de Acreditados",
        "entidad": "Organismo Nacional de Acreditación de Colombia",
        "alcance": "Consulta del estado de los organismos evaluadores de la conformidad.",
        "url": "https://onac.org.co/directorio-de-acreditados/sectores/turismo-y-ocio/",
        "verificada": True,
    },
    {
        "codigo": "documento-funcional-proyecto",
        "titulo": "Documento funcional aportado al proyecto",
        "entidad": "Referencia de planeación de Amazonía Viva",
        "alcance": "Sirve de guía funcional; no reemplaza las normas ni acredita cumplimiento.",
        "url": "",
        "verificada": False,
    },
]

PRINCIPIOS_ESTANDAR = [
    {
        "codigo": "dificultad-por-actividad",
        "descripcion": "La dificultad se registra por actividad y conserva el nombre de su sistema.",
    },
    {
        "codigo": "riesgo-interno",
        "descripcion": "El riesgo interno 1–10 orienta el catálogo, pero no sustituye una NTS.",
    },
    {
        "codigo": "certificacion-vigente",
        "descripcion": "Los tours de aventura activos deben registrar certificación vigente y medidas operativas.",
    },
    {
        "codigo": "caracter-informativo",
        "descripcion": "La ficha informa; la publicación en la plataforma no constituye una certificación.",
    },
]


def construir_resumen_estandar():
    """Construye la respuesta pública desde el catálogo persistido en la DB."""
    from .models import EstandarPaquete

    estandar = (
        EstandarPaquete.objects.filter(activo=True)
        .prefetch_related('modalidades', 'principios', 'fuentes')
        .order_by('clave')
        .first()
    )
    if not estandar:
        return {
            "configurado": False,
            "version": "",
            "nombre": "Estándar de paquetes sin configurar",
            "proposito": "Ejecuta python manage.py seed_estandar_paquetes.",
            "modalidades": [],
            "principios": [],
            "fuentes": [],
        }

    return {
        "configurado": True,
        "version": estandar.version,
        "nombre": estandar.nombre,
        "proposito": estandar.proposito,
        "modalidades": [
            {
                "value": modalidad.codigo,
                "label": modalidad.nombre,
                "description": modalidad.descripcion,
            }
            for modalidad in estandar.modalidades.filter(activa=True)
        ],
        "principios": list(
            estandar.principios.filter(activo=True).values_list('descripcion', flat=True)
        ),
        "fuentes": [
            {
                "titulo": fuente.titulo,
                "entidad": fuente.entidad,
                "alcance": fuente.alcance,
                "url": fuente.url,
                "verificada": fuente.verificada,
            }
            for fuente in estandar.fuentes.filter(activa=True)
        ],
    }
