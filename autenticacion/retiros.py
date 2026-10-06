from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import SolicitudRetiro, Usuario, CambioEstadoRetiro


@transaction.atomic
def cambiar_estado(retiro_id, nuevo, actor):
    if not actor.is_staff:
        raise PermissionDenied('Solo operadores pueden revisar retiros.')
    user_id = SolicitudRetiro.objects.values_list('usuario_id', flat=True).get(pk=retiro_id)
    Usuario.objects.select_for_update().get(pk=user_id)
    retiro = SolicitudRetiro.objects.select_for_update().get(pk=retiro_id)
    transiciones = {'Pendiente': {'Procesando', 'Rechazado', 'Cancelado'}, 'Procesando': {'Pagado', 'Rechazado'}}
    if nuevo == retiro.estado:
        return retiro
    if nuevo not in transiciones.get(retiro.estado, set()):
        raise ValidationError('Transición de retiro inválida.')
    CambioEstadoRetiro.objects.create(solicitud=retiro, anterior=retiro.estado, nuevo=nuevo, actor=actor)
    retiro.estado = nuevo
    retiro.save(update_fields=['estado'])
    return retiro
