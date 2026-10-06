"""Pedidos atómicos. Ninguna entrada del cliente confirma un pago real."""
import hashlib
import json
from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Usuario, Venta, Detalles_Venta, Productos, PaqueteTuristico, ReservaFecha, Items
from .serializers import calcular_cupos_disponibles


def entero_positivo(value, maximum=1000):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValidationError({'error': f'La cantidad o identificador debe ser un entero entre 1 y {maximum}.'})
    return value


def fecha_item(paquete, raw):
    try:
        fecha = date.fromisoformat(raw) if raw else paquete.fecha_realizacion
    except (ValueError, TypeError):
        raise ValidationError({'error': 'Fecha de reserva inválida.'})
    if not fecha or fecha < timezone.localdate():
        raise ValidationError({'error': 'Se requiere una fecha futura válida.'})
    if paquete.tipo_paquete == 'fijo' and fecha != paquete.fecha_realizacion:
        raise ValidationError({'error': 'La fecha debe corresponder a la salida del paquete.'})
    if paquete.tipo_paquete == 'flexible' and fecha < timezone.localdate() + timedelta(days=7):
        raise ValidationError({'error': 'Reserve con al menos siete días de antelación.'})
    return fecha


@transaction.atomic
def procesar_compra(user, data):
    try:
        clave = UUID(str(data.get('clave_operacion')))
    except (ValueError, TypeError):
        raise ValidationError({'error': 'Se requiere clave_operacion UUID.'})
    raw_items = data.get('items')
    if not isinstance(raw_items, list) or not 1 <= len(raw_items) <= 100:
        raise ValidationError({'error': 'Seleccione entre 1 y 100 artículos.'})
    normalizados, vistos = [], set()
    for raw in raw_items:
        if not isinstance(raw, dict) or raw.get('tipo') not in ('producto', 'tour', 'paquete'):
            raise ValidationError({'error': 'Tipo de artículo desconocido.'})
        tipo = 'paquete' if raw['tipo'] == 'tour' else raw['tipo']
        ident = entero_positivo(raw.get('id'), 2147483647)
        cantidad = entero_positivo(raw.get('cantidad', 1))
        if (tipo, ident) in vistos:
            raise ValidationError({'error': 'No se admiten artículos duplicados en una operación.'})
        vistos.add((tipo, ident))
        normalizados.append({'tipo': tipo, 'id': ident, 'cantidad': cantidad, 'fecha_reserva': raw.get('fecha_reserva')})
    normalizados.sort(key=lambda it: (it['tipo'], it['id']))
    novedades = data.get('novedades_turistas', [])
    if not isinstance(novedades, list) or len(json.dumps(novedades)) > 50000:
        raise ValidationError({'error': 'Datos de viajeros inválidos.'})
    huella = hashlib.sha256(json.dumps([normalizados, novedades], sort_keys=True).encode()).hexdigest()
    # Serializa reintentos del mismo comprador antes de consultar/crear la venta.
    Usuario.objects.select_for_update().get(pk=user.pk)
    existente = Venta.objects.filter(usuario=user, clave_operacion=clave).first()
    if existente:
        if existente.huella_operacion != huella:
            raise ValidationError({'error': 'Esta clave ya se usó con otra compra.'})
        return existente, False
    total_productos, total_tours = Decimal('0'), Decimal('0')
    preparados = []
    for it in normalizados:
        cantidad = it['cantidad']
        fecha = None
        if it['tipo'] == 'producto':
            obj = Productos.objects.select_for_update().filter(pk=it['id'], disponible=True).first()
            catalogo = 'agencias' if hasattr(user, 'agencia') else 'turistas'
            if not obj or obj.tipo_catalogo != catalogo or obj.stock < cantidad:
                raise ValidationError({'error': 'Producto no disponible o stock insuficiente.'})
            total_productos += obj.precio * cantidad
        else:
            if not hasattr(user, 'turista'):
                raise ValidationError({'error': 'Solo turistas pueden reservar paquetes.'})
            obj = PaqueteTuristico.objects.select_for_update().filter(pk=it['id'], activo=True).first()
            if not obj:
                raise ValidationError({'error': 'Paquete no disponible.'})
            fecha = fecha_item(obj, it['fecha_reserva'])
            if calcular_cupos_disponibles(obj, fecha) < cantidad:
                raise ValidationError({'error': 'Cupos insuficientes.'})
            total_tours += obj.precio * cantidad
        if obj.precio <= 0:
            raise ValidationError({'error': 'Artículo sin precio válido.'})
        preparados.append((it, obj, fecha))
    tarifa = (total_tours * Decimal('0.01')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    total = total_productos + total_tours + tarifa
    if total > Decimal('9999999999.99'):
        raise ValidationError({'error': 'El total excede el límite de la operación.'})
    demo = settings.CHECKOUT_MODE == 'demo'
    venta = Venta.objects.create(usuario=user, clave_operacion=clave, huella_operacion=huella,
        total=total, novedades_turistas=novedades, estado='Completado' if demo else 'Pendiente',
        estado_pago='Simulado' if demo else 'Pendiente', ambiente_pago=settings.WOMPI_ENVIRONMENT if settings.PAYMENT_PROVIDER == 'wompi' and not demo else '', vence_en=None if demo else timezone.now() + timedelta(minutes=30))
    for it, obj, fecha in preparados:
        producto = it['tipo'] == 'producto'
        Detalles_Venta.objects.create(venta=venta, producto=obj.pk if producto else 0,
            paquete=0 if producto else obj.pk, cantidad=it['cantidad'], precio_unitario=obj.precio,
            estado=('Pendiente de Empaque' if producto else 'Confirmado') if demo else 'Pendiente de Pago')
        if producto:
            obj.stock -= it['cantidad']
            obj.save(update_fields=['stock'])
        else:
            ReservaFecha.objects.create(venta=venta, paquete=obj, fecha=fecha, cantidad=it['cantidad'])
        # Compras parciales: elimina únicamente los artículos adquiridos.
        Items.objects.filter(carrito__usuario=user, carrito__status=True,
            **({'producto_id': obj.pk} if producto else {'paquetes_id': obj.pk})).delete()
    return venta, True


@transaction.atomic
def liberar_pedido(venta_id):
    venta = Venta.objects.select_for_update().get(pk=venta_id)
    if venta.estado_pago != 'Pendiente':
        return False
    for det in venta.detalles_venta.order_by('producto', 'paquete'):
        if det.producto:
            producto = Productos.objects.select_for_update().get(pk=det.producto)
            producto.stock += det.cantidad
            producto.save(update_fields=['stock'])
        elif det.paquete:
            PaqueteTuristico.objects.select_for_update().get(pk=det.paquete)
        det.estado = 'Cancelado'
        det.save(update_fields=['estado'])
    venta.reservas_fecha_venta.all().delete()
    venta.estado, venta.estado_pago = 'Cancelado', 'Fallido'
    venta.save(update_fields=['estado', 'estado_pago'])
    return True
