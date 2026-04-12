from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from .models import Detalles_Venta, ExperienciaEvidencia, ExperienciaCalificacion, PaqueteTuristico, Venta
from .serializers import ExperienciaEvidenciaSerializer, ExperienciaCalificacionSerializer
from django.db.models import Count, Q

class ExperienciasDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Filtramos por los paquetes que pertenecen a la agencia autenticada
        mis_paquetes_ids = PaqueteTuristico.objects.filter(agencia_id=user.id).values_list('id', flat=True)
        
        detalles = Detalles_Venta.objects.filter(paquete__in=mis_paquetes_ids).select_related('venta', 'venta__usuario').order_by('-venta__fecha')
        
        # Métricas
        total = detalles.count()
        completadas = detalles.filter(estado='Realizado').count()
        pendientes = detalles.filter(estado='Confirmado').count()
        
        lista_clientes = []
        for det in detalles:
            # Buscar el nombre del paquete (el campo es un IntegerField en Detalles_Venta)
            paquete_obj = PaqueteTuristico.objects.filter(id=det.paquete).first()
            p_nombre = paquete_obj.nombre if paquete_obj else "Desconocido"
            
            # Buscar la fecha de reserva
            from .models import ReservaFecha
            reserva = ReservaFecha.objects.filter(venta=det.venta, paquete_id=det.paquete).first()
            fecha_st = reserva.fecha if reserva else det.venta.fecha.date()
            
            # Contar evidencias
            evidencias_count = det.evidencias.count()
            
            lista_clientes.append({
                'id': det.id,
                'cliente': f"{det.venta.usuario.first_name} {det.venta.usuario.last_name}".strip() or det.venta.usuario.username,
                'tour': p_nombre,
                'fecha': str(fecha_st),
                'personas': det.cantidad,
                'estado': det.estado,
                'evidencias': evidencias_count,
            })
            
        return Response({
            'metrics': {
                'total': total,
                'completadas': completadas,
                'pendientes': pendientes
            },
            'registro': lista_clientes
        })

class SubirEvidenciaView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        detalle = get_object_or_404(Detalles_Venta, pk=pk)
        archivo = request.FILES.get('imagen')
        
        if not archivo:
            return Response({'error': 'No se proporcionó ninguna imagen.'}, status=status.HTTP_400_BAD_REQUEST)
            
        evidencia = ExperienciaEvidencia.objects.create(
            detalle_venta=detalle,
            imagen=archivo
        )
        
        return Response({
            'mensaje': 'Evidencia subida correctamente',
            'url': evidencia.imagen.url
        }, status=status.HTTP_201_CREATED)

class MarcarRealizadaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        detalle = get_object_or_404(Detalles_Venta, pk=pk)
        detalle.estado = 'Realizado'
        detalle.save()
        return Response({'mensaje': 'Experiencia marcada como realizada.'})

class DetalleFeedbackView(APIView):
    """Vista para que el turista vea las fotos y califique"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        detalle = get_object_or_404(Detalles_Venta, pk=pk)
        evidencias = detalle.evidencias.all()
        calificacion = detalle.calificacion.first()
        
        paquete_obj = PaqueteTuristico.objects.filter(id=detalle.paquete).first()
        
        return Response({
            'tour_nombre': paquete_obj.nombre if paquete_obj else "Tour",
            'evidencias': ExperienciaEvidenciaSerializer(evidencias, many=True).data,
            'calificacion': ExperienciaCalificacionSerializer(calificacion).data if calificacion else None
        })

    def post(self, request, pk):
        detalle = get_object_or_404(Detalles_Venta, pk=pk)
        puntuacion = request.data.get('puntuacion')
        comentario = request.data.get('comentario', '')
        
        if not puntuacion:
            return Response({'error': 'La puntuación es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)
            
        calificacion, created = ExperienciaCalificacion.objects.update_or_create(
            detalle_venta=detalle,
            defaults={
                'puntuacion': puntuacion,
                'comentario': comentario
            }
        )
        
        # Actualizar el rating promedio del paquete
        self._update_package_rating(detalle.paquete)
        
        return Response({'mensaje': 'Calificación guardada correctamente.'})

    def _update_package_rating(self, paquete_id):
        # El campo paquete en Detalles_Venta es un Integer
        try:
            from django.db.models import Avg
            # Buscamos todas las calificaciones para este paquete_id
            avg_rating = ExperienciaCalificacion.objects.filter(
                detalle_venta__paquete=paquete_id
            ).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
            
            PaqueteTuristico.objects.filter(id=paquete_id).update(rating=avg_rating)
        except Exception as e:
            print(f"Error actualizando rating: {e}")
