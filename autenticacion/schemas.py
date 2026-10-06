"""Contratos públicos de los endpoints monetarios."""
from rest_framework import serializers


class ArticuloCompraSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=['producto', 'paquete', 'tour'])
    id = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1, max_value=1000)
    fecha_reserva = serializers.DateField(required=False, allow_null=True)


class CompraSerializer(serializers.Serializer):
    clave_operacion = serializers.UUIDField()
    items = ArticuloCompraSerializer(many=True)
    novedades_turistas = serializers.ListField(required=False)


class CompraRespuestaSerializer(serializers.Serializer):
    checkout_url = serializers.URLField(allow_null=True)
    exito = serializers.BooleanField()
    venta_id = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    moneda = serializers.CharField()
    estado_pago = serializers.ChoiceField(choices=['Pendiente', 'Simulado'])
    mensaje = serializers.CharField()


class RetiroRespuestaSerializer(serializers.Serializer):
    mensaje = serializers.CharField()
    referencia = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo = serializers.CharField()
    estado = serializers.CharField()
    fecha_solicitud = serializers.DateTimeField()
