from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Detalles_Venta, Productos, Usuario
from .compras import entero_positivo


@transaction.atomic
def cambiar_producto(detalle_id, user, nuevo, proveedor=False):
    detalle_id = entero_positivo(detalle_id, 2147483647)
    inicial = get_object_or_404(Detalles_Venta, pk=detalle_id, producto__gt=0)
    prod = get_object_or_404(Productos, pk=inicial.producto)
    if (proveedor and prod.proveedor_id != user.pk) or (not proveedor and inicial.venta.usuario_id != user.pk):
        raise PermissionDenied('Pedido ajeno.')
    # Orden estable de los titulares del saldo.
    for ident in sorted({prod.proveedor_id, inicial.venta.usuario_id}):
        Usuario.objects.select_for_update().get(pk=ident)
    detalle = Detalles_Venta.objects.select_for_update().get(pk=detalle_id)
    prod = Productos.objects.select_for_update().get(pk=detalle.producto)
    if detalle.venta.estado_pago not in ('Pagado', 'Simulado'):
        raise ValidationError('Pedido sin pago confirmado.')
    if nuevo == detalle.estado:
        return detalle
    transiciones = {'Pendiente de Empaque': {'Enviado', 'Cancelado', 'Rechazado'},
                    'Enviado': {'En Tránsito'}, 'En Tránsito': {'Llegó'},
                    'Llegó': {'Entregado'}, 'Entregado': {'Devuelto'}}
    if nuevo not in transiciones.get(detalle.estado, set()):
        raise ValidationError('Transición de pedido inválida.')
    if not proveedor and nuevo not in ('Cancelado', 'Devuelto'):
        raise PermissionDenied('Estado no permitido.')
    if nuevo in ('Cancelado', 'Rechazado'):
        prod.stock += detalle.cantidad
        prod.save(update_fields=['stock'])
    detalle.estado = nuevo
    detalle.save(update_fields=['estado'])
    return detalle


@transaction.atomic
def cancelar_tour(detalle_id, user, agencia=False):
    from django.utils import timezone
    from .models import PaqueteTuristico, ReservaFecha
    detalle_id = entero_positivo(detalle_id, 2147483647)
    inicial = get_object_or_404(Detalles_Venta, pk=detalle_id, paquete__gt=0)
    paquete = get_object_or_404(PaqueteTuristico, pk=inicial.paquete)
    if (agencia and paquete.agencia_id != user.pk) or (not agencia and inicial.venta.usuario_id != user.pk):
        raise PermissionDenied('Reserva ajena.')
    for ident in sorted({paquete.agencia_id, inicial.venta.usuario_id}):
        Usuario.objects.select_for_update().get(pk=ident)
    detalle = Detalles_Venta.objects.select_for_update().get(pk=detalle_id)
    estado = 'Rechazado' if agencia else 'Cancelado'
    if detalle.estado == estado:
        return detalle
    if detalle.venta.estado_pago not in ('Pagado', 'Simulado') or detalle.estado != 'Confirmado':
        raise ValidationError('La reserva no está confirmada o ya finalizó. Cancele el pedido completo si está pendiente de pago.')
    reserva = ReservaFecha.objects.filter(venta=detalle.venta, paquete=paquete).first()
    if not reserva or reserva.fecha < timezone.localdate():
        raise ValidationError('La reserva ya finalizó.')
    PaqueteTuristico.objects.select_for_update().get(pk=paquete.pk)
    detalle.estado = estado
    detalle.save(update_fields=['estado'])
    return detalle
