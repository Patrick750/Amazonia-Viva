from django.core.management.base import BaseCommand
from django.utils import timezone
from autenticacion.models import Venta
from autenticacion.compras import liberar_pedido


class Command(BaseCommand):
    help = 'Libera inventario y cupos de pedidos pendientes vencidos; ejecutar cada minuto.'

    def handle(self, *args, **options):
        ids = Venta.objects.filter(estado_pago='Pendiente', vence_en__lte=timezone.now()).values_list('pk', flat=True)
        count = sum(liberar_pedido(pk) for pk in list(ids))
        self.stdout.write(f'Pedidos liberados: {count}')
