"""Checkout alojado y confirmaciones verificadas, sin datos de tarjetas."""
import hashlib
import hmac
import re
from urllib.parse import urlencode, urlsplit
import requests
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError, APIException
from .models import Venta, EventoPago, Usuario, Productos, PaqueteTuristico
from .compras import liberar_pedido


class WompiUnavailable(APIException):
    status_code = 503
    default_detail = 'Wompi no está disponible o configurado. Reintente más tarde.'


def verificar_configuracion():
    prefix = settings.WOMPI_ENVIRONMENT
    if settings.PAYMENT_PROVIDER != 'wompi' or not all([
        settings.WOMPI_PUBLIC_KEY.startswith(f'pub_{prefix}_'),
        settings.WOMPI_PRIVATE_KEY.startswith(f'prv_{prefix}_'),
        settings.WOMPI_INTEGRITY_SECRET,
        settings.WOMPI_EVENTS_SECRET,
    ]):
        raise WompiUnavailable()
    redirect = urlsplit(settings.WOMPI_REDIRECT_URL)
    if redirect.scheme != 'https' and not (settings.DEBUG and redirect.hostname in ('localhost', '127.0.0.1') and redirect.scheme == 'http'):
        raise WompiUnavailable()
    if not redirect.hostname or redirect.username or redirect.password:
        raise WompiUnavailable()


def checkout_url(venta):
    verificar_configuracion()
    if venta.estado_pago != 'Pendiente' or venta.ambiente_pago != settings.WOMPI_ENVIRONMENT or not venta.vence_en or venta.vence_en <= timezone.now():
        return None
    importe = int(venta.total * 100)
    vencimiento = venta.vence_en.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    firma = hashlib.sha256(f'{venta.referencia_pago}{importe}{venta.moneda}{vencimiento}{settings.WOMPI_INTEGRITY_SECRET}'.encode()).hexdigest()
    redirect = settings.WOMPI_REDIRECT_URL
    redirect += ('&' if '?' in redirect else '?') + urlencode({'venta_id': venta.pk})
    return 'https://checkout.wompi.co/p/?' + urlencode({
        'public-key': settings.WOMPI_PUBLIC_KEY, 'currency': venta.moneda,
        'amount-in-cents': importe, 'reference': str(venta.referencia_pago),
        'signature:integrity': firma, 'expiration-time': vencimiento, 'redirect-url': redirect,
    })


def validar_evento(evento):
    verificar_configuracion()
    try:
        if evento['event'] != 'transaction.updated' or evento['environment'] != settings.WOMPI_ENVIRONMENT:
            raise ValueError
        timestamp = evento['timestamp']
        if isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp > timezone.now().timestamp() + 300:
            raise ValueError
        firma = evento['signature']
        propiedades = firma['properties']
        if not isinstance(propiedades, list) or not 1 <= len(propiedades) <= 20 or 'transaction.id' not in propiedades:
            raise ValueError
        valores = []
        for propiedad in propiedades:
            if not isinstance(propiedad, str):
                raise ValueError
            valor = evento['data']
            for parte in propiedad.split('.'):
                valor = valor[parte]
            if isinstance(valor, (dict, list, bool)) or valor is None:
                raise ValueError
            valores.append(str(valor))
        calculado = hashlib.sha256((''.join(valores) + str(timestamp) + settings.WOMPI_EVENTS_SECRET).encode()).hexdigest()
        checksum = firma['checksum'].lower()
        if not hmac.compare_digest(calculado, checksum):
            raise ValueError
        transaccion = evento['data']['transaction']['id']
        if not isinstance(transaccion, str) or not re.fullmatch(r'[A-Za-z0-9-]{1,100}', transaccion):
            raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValidationError({'error': 'Notificación Wompi inválida.'})
    return transaccion, checksum


def consultar_transaccion(ident):
    base = 'https://production.wompi.co/v1' if settings.WOMPI_ENVIRONMENT == 'prod' else 'https://sandbox.wompi.co/v1'
    try:
        response = requests.get(f'{base}/transactions/{ident}',
            headers={'Authorization': f'Bearer {settings.WOMPI_PRIVATE_KEY}', 'Accept': 'application/json'},
            timeout=(3, 10), allow_redirects=False)
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError
        data = response.json()['data']
        if not isinstance(data, dict) or data.get('id') != ident:
            raise ValueError
        return data
    except (requests.RequestException, KeyError, ValueError, TypeError):
        raise WompiUnavailable()


def procesar_evento(evento):
    ident, checksum = validar_evento(evento)
    if EventoPago.objects.filter(checksum=checksum).exists():
        return
    datos = consultar_transaccion(ident)
    # Usar siempre la referencia/estado/moneda/importe de la API autenticada.
    try:
        original = Venta.objects.get(referencia_pago=datos.get('reference'), ambiente_pago=settings.WOMPI_ENVIRONMENT)
    except (Venta.DoesNotExist, ValueError, DjangoValidationError):
        raise ValidationError({'error': 'Referencia Wompi desconocida.'})
    importe = datos.get('amount_in_cents')
    estado = datos.get('status')
    if isinstance(importe, bool) or not isinstance(importe, int) or importe != int(original.total * 100) or datos.get('currency') != original.moneda:
        raise ValidationError({'error': 'El importe o moneda no corresponde al pedido.'})
    if estado not in {'APPROVED', 'DECLINED', 'VOIDED', 'ERROR', 'PENDING'}:
        raise ValidationError({'error': 'Estado Wompi desconocido.'})
    # Saldo y devoluciones se serializan con retiros del titular.
    detalles = list(original.detalles_venta.all())
    owners = {original.usuario_id}
    owners.update(Productos.objects.filter(pk__in=[d.producto for d in detalles]).values_list('proveedor_id', flat=True))
    owners.update(PaqueteTuristico.objects.filter(pk__in=[d.paquete for d in detalles]).values_list('agencia_id', flat=True))
    with transaction.atomic():
        for user_id in sorted(owners):
            Usuario.objects.select_for_update().get(pk=user_id)
        venta = Venta.objects.select_for_update().get(pk=original.pk)
        if EventoPago.objects.filter(checksum=checksum).exists():
            return
        if EventoPago.objects.filter(transaccion=ident, ambiente=settings.WOMPI_ENVIRONMENT).exclude(venta=venta).exists():
            raise ValidationError({'error': 'Transacción ya asociada a otro pedido.'})
        resultado = 'Sin cambios'
        if estado == 'APPROVED' and venta.estado_pago == 'Pendiente':
            try:
                finalized = parse_datetime(datos.get('finalized_at') or '')
            except (ValueError, TypeError):
                raise ValidationError({'error': 'Fecha de confirmación inválida.'})
            if not finalized or timezone.is_naive(finalized):
                raise ValidationError({'error': 'Falta fecha verificable del pago.'})
            if venta.vence_en and finalized > venta.vence_en:
                liberar_pedido(venta.pk)
                venta.refresh_from_db()
                venta.estado_pago = 'Revision'
                resultado = 'Aprobación tardía'
            else:
                venta.estado = 'Completado'
                venta.estado_pago = 'Pagado' if settings.WOMPI_ENVIRONMENT == 'prod' else 'Simulado'
                for detalle in venta.detalles_venta.select_for_update():
                    if detalle.estado != 'Pendiente de Pago':
                        raise ValidationError({'error': 'Pedido requiere conciliación de sus reservas.'})
                    detalle.estado = 'Pendiente de Empaque' if detalle.producto else 'Confirmado'
                    detalle.save(update_fields=['estado'])
                resultado = 'Confirmado'
        elif estado == 'APPROVED' and venta.estado_pago == 'Fallido':
            # El inventario ya fue liberado; no volver a confirmar ni reponer reservas.
            venta.estado_pago = 'Revision'
            resultado = 'Aprobación tardía'
        elif estado in {'DECLINED', 'ERROR', 'VOIDED'} and venta.estado_pago == 'Pendiente':
            liberar_pedido(venta.pk)
            venta.refresh_from_db()
            resultado = 'Liberado'
        elif estado == 'VOIDED' and venta.estado_pago in {'Pagado', 'Simulado'}:
            venta.estado_pago = 'Reembolsado'
            venta.estado = 'Cancelado'
            venta.detalles_venta.update(estado='Reembolsado')
            venta.reservas_fecha_venta.all().delete()
            resultado = 'Anulado'
        venta.save(update_fields=['estado', 'estado_pago'])
        EventoPago.objects.create(venta=venta, checksum=checksum, transaccion=ident,
            ambiente=settings.WOMPI_ENVIRONMENT, estado=estado, importe_centavos=importe,
            moneda=datos['currency'], resultado=resultado)
