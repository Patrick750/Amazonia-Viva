from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from .models import Detalles_Venta, ExperienciaEvidencia, ExperienciaCalificacion, PaqueteTuristico, Venta, Usuario
from .serializers import ExperienciaEvidenciaSerializer, ExperienciaCalificacionSerializer
from django.db.models import Count, Q

class ExperienciasDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        mis_paquetes_ids = PaqueteTuristico.objects.filter(agencia_id=user.id).values_list('id', flat=True)
        
        # Automatización: Finalizar tours cuya fecha haya pasado
        from datetime import date
        hoy = date.today()
        from .models import ReservaFecha
        
        pendientes_actualizar = Detalles_Venta.objects.filter(
            paquete__in=mis_paquetes_ids,
            estado='Confirmado'
        )
        for det_up in pendientes_actualizar:
            res_up = ReservaFecha.objects.filter(venta=det_up.venta, paquete_id=det_up.paquete).first()
            if res_up and res_up.fecha < hoy:
                det_up.estado = 'Realizado'
                det_up.save()

        # Obtener todos los detalles de nuevo tras la actualización
        detalles = Detalles_Venta.objects.filter(paquete__in=mis_paquetes_ids).select_related('venta', 'venta__usuario').order_by('-venta__fecha')
        
        # Grupos por (paquete, fecha)
        grupos = {}
        for det in detalles:
            reserva = ReservaFecha.objects.filter(venta=det.venta, paquete_id=det.paquete).first()
            fecha_val = reserva.fecha if reserva else det.venta.fecha.date()
            fecha_key = str(fecha_val)
            
            key = (det.paquete, fecha_key)
            if key not in grupos:
                paquete_obj = PaqueteTuristico.objects.filter(id=det.paquete).first()
                grupos[key] = {
                    'id': f"{det.paquete}-{fecha_key}",
                    'tour_id': det.paquete,
                    'tour': paquete_obj.nombre if paquete_obj else "Desconocido",
                    'fecha': fecha_key,
                    'personas': 0,
                    'estado': 'Realizado', # Default y se degrada si hay pendientes
                    'evidencias_count': 0,
                    'imagenes': [],
                    'leader_id': det.id, # ID para asociar fotos del tour
                    'turistas': []
                }
            
            g = grupos[key]
            g['personas'] += det.cantidad
            
            # Recopilar evidencias
            for ev in det.evidencias.all():
                g['imagenes'].append({
                    'id': ev.id,
                    'url': ev.imagen.url,
                    'fecha': ev.fecha_subida.strftime("%Y-%m-%d %H:%M")
                })
                g['evidencias_count'] += 1
            
            if det.estado == 'Confirmado':
                g['estado'] = 'Confirmado'
                
            # Agregar turista al listado interno
            calif = det.calificacion.first()
            
            # Buscar identificación en novedades_turistas si existe
            identificacion = "N/A"
            if det.venta.novedades_turistas and isinstance(det.venta.novedades_turistas, list):
                # El primer viajero suele ser el que coincide con el usuario si no hay detalle por pasajero
                identificacion = det.venta.novedades_turistas[0].get('num_doc', 'N/A')

            g['turistas'].append({
                'id': det.id,
                'nombre': f"{det.venta.usuario.first_name} {det.venta.usuario.last_name}".strip() or det.venta.usuario.username,
                'identificacion': identificacion,
                'estado': det.estado,
                'rating': calif.puntuacion if calif else None
            })

        lista_registro = list(grupos.values())
        
        # Métricas basadas en grupos
        metrics = {
            'total': len(lista_registro),
            'completadas': sum(1 for g in lista_registro if g['estado'] == 'Realizado'),
            'pendientes': sum(1 for g in lista_registro if g['estado'] == 'Confirmado')
        }
            
        return Response({
            'metrics': metrics,
            'registro': lista_registro
        })

class SubirEvidenciaView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        detalle = get_object_or_404(Detalles_Venta, pk=pk)
        archivos = request.FILES.getlist('imagenes')
        
        if not archivos:
            return Response({'error': 'No se proporcionaron imágenes.'}, status=status.HTTP_400_BAD_REQUEST)
            
        creados = []
        for archivo in archivos:
            evidencia = ExperienciaEvidencia.objects.create(
                detalle_venta=detalle,
                imagen=archivo
            )
            creados.append(evidencia.imagen.url)
        
        return Response({
            'mensaje': f'{len(creados)} evidencias subidas correctamente',
            'urls': creados
        }, status=status.HTTP_201_CREATED)


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


class MisExperienciasTuristaView(APIView):
    """Vista para que el turista vea todos sus tours realizados y pendientes de calificar"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import ReservaFecha
        user = request.user
        
        # Obtenemos detalles de venta que sean paquetes y que pertenezcan a las ventas del usuario
        detalles = Detalles_Venta.objects.filter(
            venta__usuario=user,
            paquete__gt=0
        ).select_related('venta').order_by('-venta__fecha')
        
        resultado = []
        for det in detalles:
            try:
                paquete_obj = PaqueteTuristico.objects.filter(id=det.paquete).first()
                if not paquete_obj:
                    continue
                    
                reserva = ReservaFecha.objects.filter(venta=det.venta, paquete_id=det.paquete).first()
                fecha_val = reserva.fecha if reserva else det.venta.fecha.date()
                
                evidencias = det.evidencias.all()
                calificacion = det.calificacion.first()
                
                # Acceso robusto a la información de la agencia
                agencia_info = {'id': None, 'nombre': "Agencia Local"}
                if paquete_obj.agencia:
                    agencia_info['id'] = paquete_obj.agencia.id
                    agencia_info['nombre'] = paquete_obj.agencia.nombre_agencia or paquete_obj.agencia.username

                resultado.append({
                    'id': det.id,
                    'tour_id': paquete_obj.id,
                    'tour_nombre': paquete_obj.nombre,
                    'agencia': agencia_info,
                    'fecha': fecha_val.strftime("%d de %B de %Y") if hasattr(fecha_val, 'strftime') else str(fecha_val),
                    'fecha_raw': str(fecha_val),
                    'personas': det.cantidad,
                    'estado': det.estado,
                    'evidencias': ExperienciaEvidenciaSerializer(evidencias, many=True).data,
                    'calificacion': ExperienciaCalificacionSerializer(calificacion).data if calificacion else None
                })
            except Exception as e:
                print(f"Error procesando detalle {det.id}: {e}")
                continue
            
        return Response(resultado)
