from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .compras import liberar_pedido
from .models import Usuario
from .permissions import IsComprador
from .models import Venta
from .wompi import procesar_evento, checkout_url


class WompiWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(description='Webhook transaction.updated. Verifica checksum y consulta la API privada de Wompi antes de modificar el pedido.', request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        procesar_evento(request.data)
        return Response({'recibido': True})


class EstadoPedidoView(APIView):
    permission_classes = [IsComprador]

    @extend_schema(description='Estado del pedido del comprador autenticado. La redirección del checkout nunca confirma pagos.', responses={200: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk, usuario=request.user)
        return Response({'venta_id': venta.pk, 'total': str(venta.total), 'moneda': venta.moneda,
            'estado': venta.estado, 'estado_pago': venta.estado_pago,
            'checkout_url': checkout_url(venta) if venta.ambiente_pago else None,
            'ambiente_pago': venta.ambiente_pago})


class CancelarPedidoPendienteView(APIView):
    permission_classes = [IsComprador]

    @extend_schema(description='Cancela el pedido completo pendiente y libera sus reservas. Idempotente.', request=None, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, pk):
        with transaction.atomic():
            Usuario.objects.select_for_update().get(pk=request.user.pk)
            venta = get_object_or_404(Venta.objects.select_for_update(), pk=pk, usuario=request.user)
            if venta.estado_pago not in ('Pendiente', 'Fallido'):
                raise ValidationError({'error': 'El pedido ya recibió confirmación de pago.'})
            liberar_pedido(venta.pk)
        return Response({'mensaje': 'Pedido cancelado; inventario y cupos liberados.'})
