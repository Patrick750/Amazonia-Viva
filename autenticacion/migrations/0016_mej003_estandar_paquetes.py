from django.db import migrations, models


ACTIVIDADES_ESTANDAR = {
    "Rafting / Canotaje": {
        "norma": "NTS-AV 010",
        "sistema": "Clase internacional del tramo de río",
        "opciones": [
            {"value": "I", "label": "Clase I · Fácil"},
            {"value": "II", "label": "Clase II · Novato"},
            {"value": "III", "label": "Clase III · Intermedio"},
            {"value": "IV", "label": "Clase IV · Avanzado"},
            {"value": "V", "label": "Clase V · Experto"},
        ],
    },
    "Rappel en cascadas": {
        "norma": "NTS-AV 011",
        "sistema": "Ficha técnica del descenso",
        "opciones": [],
    },
    "Espeleología (Exploración de cuevas)": {
        "norma": "NTS-AV 012",
        "sistema": "Características técnicas del recorrido",
        "opciones": [
            {"value": "horizontal", "label": "Recorrido horizontal"},
            {"value": "vertical", "label": "Recorrido vertical con técnicas de progresión"},
        ],
    },
}


def completar_actividades(apps, schema_editor):
    Actividad = apps.get_model("autenticacion", "Actividad")
    Categoria = apps.get_model("autenticacion", "Categoria")
    for nombre, datos in ACTIVIDADES_ESTANDAR.items():
        Actividad.objects.filter(nombre=nombre).update(
            es_turismo_aventura=True,
            norma_tecnica=datos["norma"],
            sistema_dificultad=datos["sistema"],
            opciones_dificultad=datos["opciones"],
        )

    categoria, _ = Categoria.objects.get_or_create(nombre="Aventura y Reto Físico")
    adicionales = [
        ("Parapente", 8, "NTS-AV 013", "Condiciones del vuelo y habilitación del piloto", []),
        ("Cabalgata", 4, "NTS-AV 014", "Perfil del jinete y asignación del equino", []),
        ("Torrentismo / Canyoning", 8, "NTS-AV 015", "Nivel técnico vertical y acuático", [
            {"value": str(nivel), "label": etiqueta}
            for nivel, etiqueta in (
                (1, "Nivel 1 · Muy fácil"), (2, "Nivel 2 · Fácil"),
                (3, "Nivel 3 · Poco difícil"), (4, "Nivel 4 · Bastante difícil"),
                (5, "Nivel 5 · Difícil"), (6, "Nivel 6 · Muy difícil"),
                (7, "Nivel 7 · Extremadamente difícil"),
            )
        ]),
    ]
    for nombre, riesgo, norma, sistema, opciones in adicionales:
        if not Actividad.objects.filter(nombre=nombre).exists():
            Actividad.objects.create(
                nombre=nombre,
                nivel_riesgo=riesgo,
                categoria=categoria,
                es_turismo_aventura=True,
                norma_tecnica=norma,
                sistema_dificultad=sistema,
                opciones_dificultad=opciones,
            )


class Migration(migrations.Migration):
    dependencies = [("autenticacion", "0015_venta_ambiente_pago_venta_referencia_pago_and_more")]

    operations = [
        migrations.AddField(
            model_name="actividad",
            name="es_turismo_aventura",
            field=models.BooleanField(default=False, verbose_name="Actividad de turismo de aventura"),
        ),
        migrations.AddField(
            model_name="actividad",
            name="norma_tecnica",
            field=models.CharField(blank=True, max_length=30, verbose_name="Norma técnica aplicable"),
        ),
        migrations.AddField(
            model_name="actividad",
            name="opciones_dificultad",
            field=models.JSONField(blank=True, default=list, help_text="Opciones propias de la actividad; no se comparan entre normas distintas.", verbose_name="Opciones de dificultad"),
        ),
        migrations.AddField(
            model_name="actividad",
            name="sistema_dificultad",
            field=models.CharField(blank=True, max_length=120, verbose_name="Sistema de clasificación técnica"),
        ),
        migrations.AddField(model_name="paqueteturistico", name="modalidades_turismo", field=models.JSONField(blank=True, default=list, verbose_name="Modalidades de turismo")),
        migrations.AddField(model_name="paqueteturistico", name="clasificacion_actividades", field=models.JSONField(blank=True, default=list, help_text="Cada elemento identifica la actividad, su sistema y el nivel o descripción aplicable.", verbose_name="Clasificación técnica por actividad")),
        migrations.AddField(model_name="paqueteturistico", name="requisitos_participantes", field=models.TextField(blank=True, verbose_name="Requisitos y restricciones para participantes")),
        migrations.AddField(model_name="paqueteturistico", name="condiciones_operacion", field=models.TextField(blank=True, verbose_name="Condiciones de operación")),
        migrations.AddField(model_name="paqueteturistico", name="medidas_seguridad", field=models.TextField(blank=True, verbose_name="Medidas de seguridad y respuesta")),
        migrations.AddField(model_name="paqueteturistico", name="informacion_sostenibilidad", field=models.TextField(blank=True, verbose_name="Información de sostenibilidad")),
        migrations.AddField(model_name="paqueteturistico", name="certificacion_aventura", field=models.JSONField(blank=True, default=dict, verbose_name="Soporte de certificación para turismo de aventura")),
        migrations.RunPython(completar_actividades, migrations.RunPython.noop),
    ]
