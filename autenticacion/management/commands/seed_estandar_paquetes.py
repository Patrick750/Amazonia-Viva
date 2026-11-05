from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from autenticacion.estandar_turistico import (
    ESTANDAR_PAQUETES,
    FUENTES_ESTANDAR,
    MODALIDADES_TURISMO,
    PRINCIPIOS_ESTANDAR,
)
from autenticacion.models import (
    EstandarPaquete,
    FuenteEstandarPaquete,
    ModalidadTurismo,
    PrincipioEstandarPaquete,
)


class Command(BaseCommand):
    help = 'Carga o actualiza el catálogo completo del estándar de paquetes MEJ-003'

    @transaction.atomic
    def handle(self, *args, **options):
        estandar, creado = EstandarPaquete.objects.update_or_create(
            clave=ESTANDAR_PAQUETES['clave'],
            defaults={
                'version': ESTANDAR_PAQUETES['version'],
                'nombre': ESTANDAR_PAQUETES['nombre'],
                'proposito': ESTANDAR_PAQUETES['proposito'],
                'activo': True,
            },
        )

        codigos_modalidades = set()
        for orden, datos in enumerate(MODALIDADES_TURISMO, start=1):
            codigos_modalidades.add(datos['value'])
            ModalidadTurismo.objects.update_or_create(
                estandar=estandar,
                codigo=datos['value'],
                defaults={
                    'nombre': datos['label'],
                    'descripcion': datos['description'],
                    'orden': orden,
                    'activa': True,
                },
            )
        estandar.modalidades.exclude(codigo__in=codigos_modalidades).update(activa=False)

        codigos_principios = set()
        for orden, datos in enumerate(PRINCIPIOS_ESTANDAR, start=1):
            codigos_principios.add(datos['codigo'])
            PrincipioEstandarPaquete.objects.update_or_create(
                estandar=estandar,
                codigo=datos['codigo'],
                defaults={
                    'descripcion': datos['descripcion'],
                    'orden': orden,
                    'activo': True,
                },
            )
        estandar.principios.exclude(codigo__in=codigos_principios).update(activo=False)

        codigos_fuentes = set()
        for orden, datos in enumerate(FUENTES_ESTANDAR, start=1):
            codigos_fuentes.add(datos['codigo'])
            FuenteEstandarPaquete.objects.update_or_create(
                estandar=estandar,
                codigo=datos['codigo'],
                defaults={
                    'titulo': datos['titulo'],
                    'entidad': datos['entidad'],
                    'alcance': datos['alcance'],
                    'url': datos['url'],
                    'verificada': datos['verificada'],
                    'orden': orden,
                    'activa': True,
                },
            )
        estandar.fuentes.exclude(codigo__in=codigos_fuentes).update(activa=False)

        call_command('seed_dificultades_actividades', verbosity=options['verbosity'])

        accion = 'creado' if creado else 'actualizado'
        self.stdout.write(self.style.SUCCESS(
            'Estándar de paquetes '
            f'{accion}: {len(codigos_modalidades)} modalidades, '
            f'{len(codigos_principios)} principios y {len(codigos_fuentes)} fuentes.'
        ))
