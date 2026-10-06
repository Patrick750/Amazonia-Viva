from django.core.management.base import BaseCommand, CommandError
from autenticacion.models import Usuario
from autenticacion.retiros import cambiar_estado


class Command(BaseCommand):
    help = 'Registra una transición auditada de retiro; requiere ID de operador staff.'

    def add_arguments(self, parser):
        parser.add_argument('retiro_id', type=int)
        parser.add_argument('estado', choices=['Procesando', 'Pagado', 'Rechazado', 'Cancelado'])
        parser.add_argument('--actor', type=int, required=True)

    def handle(self, *args, **options):
        try:
            retiro = cambiar_estado(options['retiro_id'], options['estado'], Usuario.objects.get(pk=options['actor']))
        except Exception as exc:
            raise CommandError('No se pudo registrar la transición.') from exc
        self.stdout.write(f'{retiro.referencia}: {retiro.estado}')
