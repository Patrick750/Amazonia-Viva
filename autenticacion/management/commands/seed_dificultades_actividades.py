from django.core.management.base import BaseCommand

from autenticacion.catalogo_dificultades import obtener_dificultad
from autenticacion.models import Actividad


class Command(BaseCommand):
    help = 'Carga o actualiza las opciones seleccionables de dificultad de las actividades'

    def handle(self, *args, **options):
        actualizadas = 0

        for actividad in Actividad.objects.all().iterator():
            dificultad = obtener_dificultad(actividad.nombre)
            cambios = {
                'sistema_dificultad': dificultad['sistema'],
                'opciones_dificultad': dificultad['opciones'],
            }
            if dificultad['norma']:
                cambios.update({
                    'norma_tecnica': dificultad['norma'],
                    'es_turismo_aventura': True,
                })

            columnas = [campo for campo, valor in cambios.items() if getattr(actividad, campo) != valor]
            if not columnas:
                continue

            for campo in columnas:
                setattr(actividad, campo, cambios[campo])
            actividad.save(update_fields=columnas)
            actualizadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Dificultades listas: {actualizadas} actividades actualizadas de {Actividad.objects.count()}.'
        ))
