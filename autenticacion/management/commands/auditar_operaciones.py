"""Revisión de solo lectura. No infiere que una venta histórica esté pagada."""
import json
from decimal import Decimal, ROUND_HALF_UP
from django.core.management.base import BaseCommand
from autenticacion.models import Venta, Detalles_Venta, Productos, SolicitudRetiro


class Command(BaseCommand):
    help = 'Resume anomalías históricas sin exponer datos personales o bancarios.'

    def handle(self, *args, **options):
        discrepancias = []
        for venta in Venta.objects.prefetch_related('detalles_venta').iterator(chunk_size=200):
            detalles = list(venta.detalles_venta.all())
            subtotal = sum((d.precio_unitario * d.cantidad for d in detalles), Decimal('0'))
            tours = sum((d.precio_unitario * d.cantidad for d in detalles if d.paquete), Decimal('0'))
            tarifa = (tours * Decimal('0.01')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            if not detalles or venta.total not in (subtotal, subtotal + tarifa):
                discrepancias.append(venta.pk)
        self.stdout.write(json.dumps({
            'ventas_importe_inconsistente': discrepancias,
            'ventas_historicas_sin_evidencia_pago': Venta.objects.filter(clave_operacion__isnull=True, estado_pago='Pendiente').count(),
            'detalles_cantidad_invalida': Detalles_Venta.objects.filter(cantidad__lte=0).count(),
            'detalles_precio_invalido': Detalles_Venta.objects.filter(precio_unitario__lt=0).count(),
            'productos_stock_negativo': Productos.objects.filter(stock__lt=0).count(),
            'retiros_monto_invalido': SolicitudRetiro.objects.filter(monto__lte=0).count(),
            'retiros_por_reconciliar': SolicitudRetiro.objects.count(),
        }, indent=2))
