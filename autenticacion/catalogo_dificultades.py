"""Catálogo de opciones seleccionables para la dificultad por actividad.

Las escalas normativas conservan su nombre propio. Para actividades sin una
escala sectorial cargada se usa una referencia operativa interna, claramente
identificada como tal, para no presentarla como una certificación técnica.
"""

from copy import deepcopy


OPCIONES_EXIGENCIA_INTERNA = [
    {
        "value": "baja",
        "label": "Baja",
        "description": "Ritmo tranquilo, pausas frecuentes y esfuerzo ligero.",
    },
    {
        "value": "media",
        "label": "Media",
        "description": "Actividad continua y condición física básica.",
    },
    {
        "value": "alta",
        "label": "Alta",
        "description": "Esfuerzo sostenido, experiencia o preparación previa.",
    },
]


DIFICULTADES_ESPECIFICAS = {
    "Rafting / Canotaje": {
        "norma": "NTS-AV 010",
        "sistema": "Clase internacional del tramo de río",
        "opciones": [
            {"value": "I", "label": "Clase I · Fácil", "description": "Corriente suave y maniobras básicas."},
            {"value": "II", "label": "Clase II · Novato", "description": "Rápidos amplios con obstáculos sencillos."},
            {"value": "III", "label": "Clase III · Intermedio", "description": "Rápidos moderados que requieren maniobra activa."},
            {"value": "IV", "label": "Clase IV · Avanzado", "description": "Rápidos intensos y maniobras precisas."},
            {"value": "V", "label": "Clase V · Experto", "description": "Tramos muy exigentes para participantes expertos."},
        ],
    },
    "Rappel en cascadas": {
        "norma": "NTS-AV 011",
        "sistema": "Configuración técnica del descenso",
        "opciones": [
            {"value": "iniciacion", "label": "Iniciación", "description": "Descenso corto, guiado y con técnica básica."},
            {"value": "intermedio", "label": "Intermedio", "description": "Mayor altura o exposición y maniobras encadenadas."},
            {"value": "avanzado", "label": "Avanzado", "description": "Descenso técnico para personas con experiencia."},
        ],
    },
    "Espeleología (Exploración de cuevas)": {
        "norma": "NTS-AV 012",
        "sistema": "Características técnicas del recorrido",
        "opciones": [
            {"value": "horizontal", "label": "Recorrido horizontal", "description": "Progresión sin técnicas verticales."},
            {"value": "vertical", "label": "Recorrido vertical", "description": "Incluye técnicas de progresión vertical."},
        ],
    },
    "Parapente": {
        "norma": "NTS-AV 013",
        "sistema": "Modalidad operativa del vuelo",
        "opciones": [
            {"value": "contemplativo", "label": "Vuelo contemplativo", "description": "Vuelo biplaza de duración corta y condiciones estables."},
            {"value": "termico", "label": "Vuelo térmico", "description": "Aprovecha corrientes térmicas para ganar altura."},
            {"value": "travesia", "label": "Vuelo de travesía", "description": "Recorrido aéreo prolongado sujeto a condiciones técnicas."},
        ],
    },
    "Cabalgata": {
        "norma": "NTS-AV 014",
        "sistema": "Exigencia técnica de la ruta ecuestre",
        "opciones": [
            {"value": "iniciacion", "label": "Iniciación", "description": "Ruta corta y controlada para personas sin experiencia."},
            {"value": "intermedia", "label": "Intermedia", "description": "Terreno mixto y mayor tiempo de monta."},
            {"value": "travesia", "label": "Travesía", "description": "Ruta prolongada que requiere experiencia previa."},
        ],
    },
    "Torrentismo / Canyoning": {
        "norma": "NTS-AV 015",
        "sistema": "Nivel técnico vertical y acuático",
        "opciones": [
            {"value": "1", "label": "Nivel 1 · Muy fácil"},
            {"value": "2", "label": "Nivel 2 · Fácil"},
            {"value": "3", "label": "Nivel 3 · Poco difícil"},
            {"value": "4", "label": "Nivel 4 · Bastante difícil"},
            {"value": "5", "label": "Nivel 5 · Difícil"},
            {"value": "6", "label": "Nivel 6 · Muy difícil"},
            {"value": "7", "label": "Nivel 7 · Extremadamente difícil"},
        ],
    },
}


def obtener_dificultad(nombre_actividad):
    """Devuelve una copia segura de la configuración aplicable."""
    especifica = DIFICULTADES_ESPECIFICAS.get(nombre_actividad)
    if especifica:
        return deepcopy(especifica)
    return {
        "norma": "",
        "sistema": "Nivel de exigencia del recorrido (referencia interna)",
        "opciones": deepcopy(OPCIONES_EXIGENCIA_INTERNA),
    }
