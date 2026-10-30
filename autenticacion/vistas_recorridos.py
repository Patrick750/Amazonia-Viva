"""Recorridos GPS vinculados a paquetes turísticos (MEJ-001).

La agencia graba el trazado en el dispositivo, incluso sin conexión, y lo sincroniza
después. Cada recorrido y cada punto llevan un identificador generado por el cliente,
de modo que reintentar un envío no duplica datos. El público solo ve un trazado
simplificado y publicado por la agencia; los puntos originales (con hora y precisión)
no se exponen.
"""
import math
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Detalles_Venta, PaqueteTuristico, PuntoRecorrido, Recorrido, ReservaFecha
from .permissions import IsAgencia, IsTurista

MAX_PUNTOS_POR_LOTE = 500
MIN_PUNTOS_PARA_PUBLICAR = 2
DISTANCIA_MINIMA_PUBLICA_M = 5
MAX_PUNTOS_PUBLICOS = 1000


def fecha_de_hoy():
    """Día actual en la zona horaria de los paquetes, no en la del servidor."""
    return timezone.now().astimezone(ZoneInfo(settings.RECORRIDOS_ZONA_HORARIA)).date()


def distancia_m(a, b):
    """Distancia aproximada en metros entre dos puntos (lat, lng)."""
    radio = 6371000
    f1, f2 = math.radians(a[0]), math.radians(b[0])
    df, dl = f2 - f1, math.radians(b[1] - a[1])
    h = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * radio * math.asin(math.sqrt(h))


def simplificar(puntos):
    """Descarta puntos casi idénticos y limita el total que se envía al público."""
    if not puntos:
        return []
    conservados = [puntos[0]]
    for punto in puntos[1:-1]:
        if distancia_m(conservados[-1], punto) >= DISTANCIA_MINIMA_PUBLICA_M:
            conservados.append(punto)
    if len(puntos) > 1:
        conservados.append(puntos[-1])
    if len(conservados) > MAX_PUNTOS_PUBLICOS:
        paso = len(conservados) / MAX_PUNTOS_PUBLICOS
        conservados = [conservados[int(i * paso)] for i in range(MAX_PUNTOS_PUBLICOS - 1)] + [conservados[-1]]
    return conservados


def trazado_publico(recorrido):
    pares = [(float(lat), float(lng)) for lat, lng in recorrido.puntos.values_list('latitud', 'longitud')]
    puntos = simplificar(pares)
    kilometros = sum(distancia_m(puntos[i], puntos[i + 1]) for i in range(len(puntos) - 1)) / 1000
    return {
        'disponible': True,
        'nombre': recorrido.nombre,
        'publicado_en': recorrido.publicado_en,
        'distancia_km': round(kilometros, 2),
        'puntos': [[lat, lng] for lat, lng in puntos],
    }


def distancias_al_paquete_m(recorridos):
    """Menor distancia (m) entre cada recorrido y la ubicación de su paquete.

    Devuelve {id_del_recorrido: metros}; falta la clave si el paquete no tiene ubicación o el
    recorrido no tiene puntos. Se resuelve con una sola consulta de puntos.
    """
    destinos = {
        r.pk: (float(r.paquete.latitud), float(r.paquete.longitud))
        for r in recorridos if r.paquete.latitud is not None and r.paquete.longitud is not None
    }
    minimas = {}
    filas = PuntoRecorrido.objects.filter(recorrido_id__in=list(destinos)).values_list('recorrido_id', 'latitud', 'longitud')
    for recorrido_id, lat, lng in filas:
        metros = distancia_m((float(lat), float(lng)), destinos[recorrido_id])
        if recorrido_id not in minimas or metros < minimas[recorrido_id]:
            minimas[recorrido_id] = metros
    return minimas


def reserva_habilitada(usuario_id, paquete_id):
    """Reserva del turista que habilita el recorrido hoy, o None.

    Exige una compra pagada (venta Completado), el paquete Confirmado y que la fecha
    elegida para realizarlo sea el día de hoy.
    """
    hoy = fecha_de_hoy()
    confirmados = Detalles_Venta.objects.filter(
        venta__usuario_id=usuario_id, venta__estado='Completado',
        paquete=paquete_id, estado='Confirmado',
    ).values_list('venta_id', flat=True)
    return ReservaFecha.objects.filter(
        venta_id__in=list(confirmados), paquete_id=paquete_id, fecha=hoy,
    ).select_related('paquete').first()


class PuntoEntradaSerializer(serializers.Serializer):
    secuencia = serializers.IntegerField(min_value=0)
    latitud = serializers.FloatField(min_value=-90, max_value=90)
    longitud = serializers.FloatField(min_value=-180, max_value=180)
    precision_m = serializers.FloatField(required=False, allow_null=True, min_value=0)
    capturado_en = serializers.DateTimeField()


class LotePuntosSerializer(serializers.Serializer):
    puntos = serializers.ListField(child=PuntoEntradaSerializer(), min_length=1, max_length=MAX_PUNTOS_POR_LOTE)


class CrearRecorridoSerializer(serializers.Serializer):
    id_cliente = serializers.UUIDField()
    paquete = serializers.IntegerField(min_value=1)
    nombre = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    iniciado_en = serializers.DateTimeField()


class FinalizarRecorridoSerializer(serializers.Serializer):
    finalizado_en = serializers.DateTimeField()


def resumen(recorrido, distancia_paquete_m=None):
    limite = settings.RECORRIDOS_DISTANCIA_MAXIMA_M
    return {
        'id_cliente': recorrido.id_cliente,
        'paquete': recorrido.paquete_id,
        'nombre': recorrido.nombre,
        'iniciado_en': recorrido.iniciado_en,
        'finalizado_en': recorrido.finalizado_en,
        'publicado': recorrido.publicado,
        'total_puntos': getattr(recorrido, 'total_puntos', None),
        'distancia_paquete_m': None if distancia_paquete_m is None else round(distancia_paquete_m),
        'coincide_con_paquete': None if distancia_paquete_m is None else distancia_paquete_m <= limite,
        'limite_m': limite,
    }


def recorrido_de_la_agencia(request, id_cliente):
    return get_object_or_404(Recorrido, id_cliente=id_cliente, paquete__agencia_id=request.user.pk)


class RecorridosAgenciaView(APIView):
    permission_classes = [IsAgencia]

    def get(self, request):
        recorridos = Recorrido.objects.filter(paquete__agencia_id=request.user.pk).select_related('paquete').annotate(total_puntos=Count('puntos'))
        paquete = request.query_params.get('paquete')
        if paquete and paquete.isdigit():
            recorridos = recorridos.filter(paquete_id=int(paquete))
        lista = list(recorridos[:100])
        distancias = distancias_al_paquete_m(lista)
        return Response([resumen(r, distancias.get(r.pk)) for r in lista])

    def post(self, request):
        datos = CrearRecorridoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        valores = datos.validated_data
        paquete = get_object_or_404(PaqueteTuristico, pk=valores['paquete'], agencia_id=request.user.pk)
        recorrido, creado = Recorrido.objects.get_or_create(
            id_cliente=valores['id_cliente'],
            defaults={'paquete': paquete, 'nombre': valores['nombre'], 'iniciado_en': valores['iniciado_en']},
        )
        if recorrido.paquete.agencia_id != request.user.pk:
            return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if recorrido.paquete_id != paquete.pk:
            return Response({'detail': 'Este recorrido ya está asociado a otro paquete.'}, status=status.HTTP_409_CONFLICT)
        return Response(resumen(recorrido), status=status.HTTP_201_CREATED if creado else status.HTTP_200_OK)


class PuntosRecorridoView(APIView):
    permission_classes = [IsAgencia]

    def post(self, request, id_cliente):
        recorrido = recorrido_de_la_agencia(request, id_cliente)
        if recorrido.publicado:
            return Response({'detail': 'Un recorrido publicado no admite más puntos. Despublícalo primero.'}, status=status.HTTP_409_CONFLICT)
        lote = LotePuntosSerializer(data=request.data)
        lote.is_valid(raise_exception=True)
        puntos = [
            PuntoRecorrido(
                recorrido=recorrido, secuencia=p['secuencia'],
                latitud=round(p['latitud'], 6), longitud=round(p['longitud'], 6),
                precision_m=p.get('precision_m'), capturado_en=p['capturado_en'],
            )
            for p in lote.validated_data['puntos']
        ]
        # ignore_conflicts: un reintento con la misma secuencia no duplica el punto.
        PuntoRecorrido.objects.bulk_create(puntos, ignore_conflicts=True)
        return Response({'recibidos': len(puntos), 'total': recorrido.puntos.count()})


class FinalizarRecorridoView(APIView):
    permission_classes = [IsAgencia]

    def post(self, request, id_cliente):
        recorrido = recorrido_de_la_agencia(request, id_cliente)
        datos = FinalizarRecorridoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        if recorrido.finalizado_en is None:
            recorrido.finalizado_en = datos.validated_data['finalizado_en']
            recorrido.save(update_fields=['finalizado_en'])
        recorrido.total_puntos = recorrido.puntos.count()
        return Response(resumen(recorrido))


class EliminarRecorridoView(APIView):
    """Elimina un recorrido de la agencia con todos sus puntos. Si estaba publicado, deja de verse en el paquete."""
    permission_classes = [IsAgencia]

    def delete(self, request, id_cliente):
        recorrido_de_la_agencia(request, id_cliente).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicarRecorridoView(APIView):
    """POST publica el recorrido (reemplaza al publicado); DELETE lo retira."""
    permission_classes = [IsAgencia]

    def post(self, request, id_cliente):
        recorrido = recorrido_de_la_agencia(request, id_cliente)
        if recorrido.finalizado_en is None:
            return Response({'detail': 'Finaliza el recorrido antes de publicarlo.'}, status=status.HTTP_400_BAD_REQUEST)
        if recorrido.puntos.count() < MIN_PUNTOS_PARA_PUBLICAR:
            return Response({'detail': 'El recorrido necesita al menos dos puntos sincronizados.'}, status=status.HTTP_400_BAD_REQUEST)
        distancia = distancias_al_paquete_m([recorrido]).get(recorrido.pk)
        maximo = settings.RECORRIDOS_DISTANCIA_MAXIMA_M
        if distancia is not None and distancia > maximo:
            return Response({
                'detail': (
                    f'El recorrido queda a {distancia / 1000:.1f} km de la ubicación del paquete '
                    f'(máximo {maximo / 1000:.1f} km). Revisa que grabaste el paquete correcto o actualiza la ubicación del paquete.'
                ),
                'codigo': 'lejos_del_paquete',
                'distancia_m': round(distancia),
            }, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            Recorrido.objects.filter(paquete_id=recorrido.paquete_id, publicado=True).exclude(pk=recorrido.pk).update(publicado=False, publicado_en=None)
            if not recorrido.publicado:
                recorrido.publicado = True
                recorrido.publicado_en = timezone.now()
                recorrido.save(update_fields=['publicado', 'publicado_en'])
        recorrido.total_puntos = recorrido.puntos.count()
        return Response(resumen(recorrido))

    def delete(self, request, id_cliente):
        recorrido = recorrido_de_la_agencia(request, id_cliente)
        recorrido.publicado = False
        recorrido.publicado_en = None
        recorrido.save(update_fields=['publicado', 'publicado_en'])
        recorrido.total_puntos = recorrido.puntos.count()
        return Response(resumen(recorrido))


class RecorridoPublicoView(APIView):
    """Trazado publicado de un paquete, visible para quien consulta el paquete."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        recorrido = Recorrido.objects.filter(paquete_id=pk, publicado=True).first()
        if recorrido is None:
            return Response({'disponible': False})
        return Response(trazado_publico(recorrido))


class RecorridosHabilitadosTuristaView(APIView):
    """Paquetes comprados por el turista cuyo recorrido está habilitado hoy."""
    permission_classes = [IsTurista]

    def get(self, request):
        hoy = fecha_de_hoy()
        confirmados = Detalles_Venta.objects.filter(
            venta__usuario_id=request.user.pk, venta__estado='Completado', estado='Confirmado',
        ).values_list('venta_id', 'paquete')
        pares = set(confirmados)
        reservas = ReservaFecha.objects.filter(
            fecha=hoy, venta__usuario_id=request.user.pk,
        ).select_related('paquete')
        habilitados = {}
        for reserva in reservas:
            if (reserva.venta_id, reserva.paquete_id) in pares:
                habilitados[reserva.paquete_id] = {
                    'paquete': reserva.paquete_id, 'nombre': reserva.paquete.nombre,
                    'ubicacion': reserva.paquete.ubicacion, 'fecha': reserva.fecha,
                    'tiene_recorrido': Recorrido.objects.filter(paquete_id=reserva.paquete_id, publicado=True).exists(),
                }
        return Response(list(habilitados.values()))


class RecorridoTuristaView(APIView):
    """Trazado del paquete, solo si el turista tiene la reserva habilitada hoy."""
    permission_classes = [IsTurista]

    def get(self, request, pk):
        reserva = reserva_habilitada(request.user.pk, pk)
        if reserva is None:
            return Response(
                {'detail': 'El recorrido se habilita el día de realización de un paquete que hayas comprado y confirmado.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        recorrido = Recorrido.objects.filter(paquete_id=pk, publicado=True).first()
        datos = trazado_publico(recorrido) if recorrido else {'disponible': False}
        datos.update({'paquete': pk, 'nombre_paquete': reserva.paquete.nombre, 'fecha': reserva.fecha})
        return Response(datos)
