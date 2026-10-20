"""Catálogo verificable que respalda la ficha técnica de paquetes de MEJ-003.

Las escalas se mantienen separadas por actividad. ``nivel_riesgo`` continúa siendo
una referencia interna del catálogo y no se presenta como clasificación normativa.
"""

VERSION_ESTANDAR = "2026-10-16"

MODALIDADES_TURISMO = [
    {"value": "naturaleza", "label": "Naturaleza y ecoturismo"},
    {"value": "aventura", "label": "Turismo de aventura"},
    {"value": "cultural", "label": "Turismo cultural"},
    {"value": "rural", "label": "Turismo rural"},
    {"value": "agroturismo", "label": "Agroturismo"},
    {"value": "bienestar", "label": "Bienestar"},
    {"value": "nautico", "label": "Turismo náutico"},
    {"value": "reuniones", "label": "Reuniones y eventos"},
]

FUENTES_ESTANDAR = [
    {
        "titulo": "Resolución 0612 de 2024",
        "entidad": "Ministerio de Comercio, Industria y Turismo",
        "alcance": "Programa Nacional de Calidad Turística y niveles de certificación.",
        "url": "https://www.mincit.gov.co/prensa/noticias/turismo/servicios-turismo-aventura-certificacion-seguridad",
        "verificada": True,
    },
    {
        "titulo": "Normas Técnicas Sectoriales para agencias de viajes",
        "entidad": "Ministerio de Comercio, Industria y Turismo",
        "alcance": "Índice oficial de las NTS-AV 010 a 015 por actividad de aventura.",
        "url": "https://www.mincit.gov.co/minturismo/calidad-y-desarrollo-sostenible/calidad-turistica/normas-tecnicas-sectoriales/nts-agencias-de-viajes-1",
        "verificada": True,
    },
    {
        "titulo": "Directorio Oficial de Acreditados",
        "entidad": "Organismo Nacional de Acreditación de Colombia",
        "alcance": "Consulta del estado de los organismos evaluadores de la conformidad.",
        "url": "https://onac.org.co/directorio-de-acreditados/sectores/turismo-y-ocio/",
        "verificada": True,
    },
    {
        "titulo": "Documento funcional aportado al proyecto",
        "entidad": "Referencia de planeación de Amazonía Viva",
        "alcance": "Sirve de guía funcional; no reemplaza las normas ni acredita cumplimiento.",
        "url": "",
        "verificada": False,
    },
]


def construir_resumen_estandar():
    return {
        "version": VERSION_ESTANDAR,
        "nombre": "Ficha técnica de seguridad y dificultad por actividad",
        "proposito": (
            "Registrar información clara para el viajero y conservar la clasificación "
            "técnica propia de cada actividad sin mezclar escalas diferentes."
        ),
        "modalidades": MODALIDADES_TURISMO,
        "principios": [
            "La dificultad se registra por actividad y conserva el nombre de su sistema.",
            "El riesgo interno 1–10 orienta el catálogo, pero no sustituye una NTS.",
            "Los tours de aventura activos deben registrar certificación vigente y medidas operativas.",
            "La ficha informa; la publicación en la plataforma no constituye una certificación.",
        ],
        "fuentes": FUENTES_ESTANDAR,
    }
