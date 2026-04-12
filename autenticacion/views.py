from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
import time
import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction
from django.core.mail import send_mail
from datetime import date
from .serializers import calcular_cupos_disponibles

# Create your views here.

#Registro de nueva agencia
class RegistroAgencia(APIView):
    def post(self, request):
        serializers = AgenciaSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()

            return Response(
                {"mensaje":"Agencia registrada existosamente","exito":True},
                status=status.HTTP_201_CREATED
            )
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#registro de nuevo proveedor
class RegistroProveedor(APIView):
    def post(self, request):
        selrializers = ProveedorSerializers(data=request.data)
        if selrializers.is_valid():
            selrializers.save()  
        
            return Response(
                {"mensaje":"Proveedor registrado existosamente","exito":True},
                status=status.HTTP_201_CREATED
            )
        return Response(selrializers.errors, status=status.HTTP_400_BAD_REQUEST)

#registro de nuevo turista
class RegistroTurista(APIView):
    def post(self, request):
        serializers = TuristaSerializers(data=request.data)
        if serializers.is_valid():
            serializers.save()
        
            return Response(
                {"mensaje":"Turista registrada existosamente","exito":True},
                status=status.HTTP_201_CREATED
            )
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#verificacion de correo existente
class VerificarEmail(APIView):
    def post(self, request):
        formEmail = request.data.get('email')
        formUsername = request.data.get('username')
        formIdentidad = request.data.get('identidad')
        
        if formEmail:
            emailExiste = Usuario.objects.filter(email=formEmail).exists()
            return Response({
                'email': emailExiste
            })
        elif formUsername:
            usernameExiste = Usuario.objects.filter(username=formUsername).exists()
            return Response({
                'username': usernameExiste
            })
        elif formIdentidad:
            identidadExiste = Turista.objects.filter(numero_identidad=formIdentidad).exists()
            return Response({
                'identidad': identidadExiste
            })
   
        return Response(
            {'error':'No se validaron los datos'},status=status.HTTP_400_BAD_REQUEST
            )

class Login(TokenObtainPairView):
    serializer_class = SerializersLogin

class Logout(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            print('Logout exitoso')
            return Response ({'mensaje': 'Sesion cerrada exitosamente'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'mensaje': f'Hubo un error{e}'},status=status.HTTP_400_BAD_REQUEST)

class Actividades(APIView):
    def get(self, request):
        try:
            actividades = Actividad.objects.all()
            serializer = SerializersActividades(actividades, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'mensaje':'Hubo un error con la DB'})

class NewPack(APIView):
    def post(self, request):
        serializer = SerializersCreateNewPack(data=request.data)
        if serializer.is_valid():
            try:
                # Obtener el objeto Agencia del usuario autenticado
                agencia = Agencia.objects.get(pk=request.user.pk)
                serializer.save(agencia=agencia)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Agencia.DoesNotExist:
                return Response(
                    {"error": "Solo las agencias pueden crear paquetes turísticos."},
                    status=status.HTTP_403_FORBIDDEN
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:   
            print('Error en los serializers: ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdatePack(APIView):
    def put(self, request, pk):
        try:
            paquete = PaqueteTuristico.objects.get(pk=pk)
        except PaqueteTuristico.DoesNotExist:
            return Response({"error": "Paquete no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SerializersCreateNewPack(paquete, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:   
            print('Error en update serializers: ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePack(APIView):
    def delete(self, request, pk):
        try:
            paquete = PaqueteTuristico.objects.get(pk=pk)
            paquete.delete()
            return Response({"mensaje": "Paquete eliminado exitosamente"}, status=status.HTTP_200_OK)
        except PaqueteTuristico.DoesNotExist:
            return Response({"error": "Paquete no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaquetesTuristicos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            agencia_id = request.query_params.get('agencia_id', None)
            
            # Si se solicita una agencia específica (uso público/previsualización)
            if agencia_id:
                paquetes = PaqueteTuristico.objects.filter(agencia_id=agencia_id)
            # Si no hay ID, pero el usuario es una agencia, mostrar solo SUS paquetes
            elif hasattr(request.user, 'agencia'):
                paquetes = PaqueteTuristico.objects.filter(agencia=request.user.agencia)
            else:
                # Para otros roles sin ID específico, no mostramos nada por seguridad
                # O podríamos mostrar todos si es admin, pero por ahora aislamos.
                paquetes = PaqueteTuristico.objects.none()
                
            serializers = SerializersPaquetes(paquetes, many=True)
            return Response(serializers.data)
        except Exception as e:
            return Response({'mensaje': 'Hubo un error al obtener los paquetes', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CatalogoTours(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            from django.utils import timezone as tz
            agencia_id = request.query_params.get('agencia_id', None)
            tipo = request.query_params.get('tipo', None)  # 'fijo' | 'flexible'

            tours = PaqueteTuristico.objects.filter(activo=True).prefetch_related(
                'imagen_paquete', 'actividades'
            ).select_related('agencia', 'categoria_paquete')

            if agencia_id:
                tours = tours.filter(agencia_id=agencia_id)
            if tipo in ('fijo', 'flexible'):
                tours = tours.filter(tipo_paquete=tipo)

            # Auto-expirar paquetes fijos con fecha pasada
            vencidos = PaqueteTuristico.objects.filter(
                activo=True,
                tipo_paquete='fijo',
                fecha_realizacion__lt=tz.now().date()
            )
            if vencidos.exists():
                vencidos.update(activo=False)
                # Excluir los recién vencidos del resultado actual
                tours = tours.exclude(fecha_realizacion__lt=tz.now().date())

            serializer = SerializerCatalogoTour(tours, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CuposDisponiblesView(APIView):
    """GET /api/cupos/<pk>/?fecha=YYYY-MM-DD
    Devuelve cupos disponibles para un paquete en una fecha específica."""
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        try:
            from django.utils import timezone as tz
            from datetime import date as date_type
            from .serializers import calcular_cupos_disponibles
            paquete = get_object_or_404(PaqueteTuristico, pk=pk)
            fecha_str = request.query_params.get('fecha', None)

            fecha = None
            if fecha_str:
                try:
                    from datetime import date
                    fecha = date.fromisoformat(fecha_str)
                except ValueError:
                    return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            
            cupos = calcular_cupos_disponibles(paquete, fecha)
            return Response({
                'paquete_id': pk,
                'capacidad': paquete.capacidad,
                'cupos_disponibles': cupos,
                'fecha': fecha_str or (str(paquete.fecha_realizacion) if paquete.fecha_realizacion else None),
                'tipo_paquete': paquete.tipo_paquete,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoriaPaqueteListView(APIView):
    def get(self, request):
        try:
            categorias = CategoriaPaquete.objects.all()
            serializer = CategoriaPaqueteSerializer(categorias, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoriaProductoListView(APIView):
    def get(self, request):
        try:
            categorias = Categorias.objects.all()
            serializer = CategoriaProductoSerializer(categorias, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CatalogoProductos(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            tipo = request.query_params.get('tipo', None)
            proveedor_id = request.query_params.get('proveedor_id', None)
            productos = Productos.objects.filter(disponible=True).prefetch_related(
                'imagen_producto'
            ).select_related('proveedor', 'categorias')
            if tipo:
                productos = productos.filter(tipo_catalogo=tipo)
            if proveedor_id:
                productos = productos.filter(proveedor_id=proveedor_id)
            serializer = SerializerCatalogoProducto(productos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FavoritoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            favoritos = Favoritos.objects.filter(usuario=request.user).select_related(
                'producto', 'producto__categorias',
                'paquetes', 'paquetes__categoria_paquete'
            ).prefetch_related('producto__imagen_producto', 'paquetes__imagen_paquete')
            serializer = FavoritoDetailSerializer(favoritos, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"ERROR EN GET FAVORITOS: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            producto_id = request.data.get('producto')
            paquetes_id = request.data.get('paquetes')
            
            if not producto_id and not paquetes_id:
                return Response({'error': 'Debe proporcionar un producto o un paquete.'}, status=status.HTTP_400_BAD_REQUEST)

            # Evitar duplicados de forma segura
            favorito = Favoritos.objects.filter(
                usuario=request.user,
                producto_id=producto_id if producto_id else None,
                paquetes_id=paquetes_id if paquetes_id else None
            ).first()
            
            created = False
            if not favorito:
                favorito = Favoritos.objects.create(
                    usuario=request.user,
                    producto_id=producto_id if producto_id else None,
                    paquetes_id=paquetes_id if paquetes_id else None
                )
                created = True
                
            serializer = FavoritoSerializer(favorito)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR EN FAVORITOS: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        favorito = get_object_or_404(Favoritos, pk=pk, usuario=request.user)
        favorito.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user, status=True)
            items = Items.objects.filter(carrito=carrito).select_related(
                'producto', 'producto__categorias',
                'paquetes'
            ).prefetch_related('producto__imagen_producto', 'paquetes__imagen_paquete')
            
            serializer = CarritoItemDetailSerializer(items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user, status=True)
            producto_id = request.data.get('producto')
            paquetes_id = request.data.get('paquetes')
            precio = request.data.get('precio')
            fecha_reserva = request.data.get('fecha_reserva')  # fecha elegida por el turista

            if not producto_id and not paquetes_id:
                return Response({'error': 'Debe proporcionar un producto o un paquete.'}, status=status.HTTP_400_BAD_REQUEST)

            # Evitar duplicados del mismo paquete en el mismo carrito activo de forma segura
            item = Items.objects.filter(
                carrito=carrito,
                producto=producto_id if producto_id else None,
                paquetes=paquetes_id if paquetes_id else None
            ).first()
            
            cantidad = request.data.get('cantidad', 1)
            
            created = False
            if not item:
                item = Items.objects.create(
                    carrito=carrito,
                    producto_id=producto_id if producto_id else None,
                    paquetes_id=paquetes_id if paquetes_id else None,
                    precio=precio,
                    fecha_reserva=fecha_reserva if fecha_reserva else None,
                    cantidad=cantidad
                )
                created = True
            else:
                # Actualizar campos si ya existía el item
                if fecha_reserva:
                    item.fecha_reserva = fecha_reserva
                if cantidad:
                    item.cantidad = cantidad
                item.save()

            serializer = CarritoItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR EN CARRITO: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk=None):
        try:
            if not pk:
                return Response({'error': 'ID de ítem requerido.'}, status=status.HTTP_400_BAD_REQUEST)
            
            item = get_object_or_404(Items, pk=pk, carrito__usuario=request.user)
            
            if 'cantidad' in request.data:
                item.cantidad = request.data['cantidad']
            if 'fecha_reserva' in request.data:
                item.fecha_reserva = request.data['fecha_reserva']
            
            item.save()
            serializer = CarritoItemSerializer(item)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        try:
            if pk:
                # Eliminar un item específico
                item = get_object_or_404(Items, pk=pk, carrito__usuario=request.user)
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                # Vaciar el carrito completo (opcional, pero útil)
                carrito = Carrito.objects.filter(usuario=request.user, status=True).first()
                if carrito:
                    Items.objects.filter(carrito=carrito).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetalleTourPublico(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        tour = get_object_or_404(PaqueteTuristico, pk=pk, activo=True)
        serializer = SerializerDetalleTour(tour)
        return Response(serializer.data)

class DetalleProductoPublico(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        producto = get_object_or_404(Productos, pk=pk, disponible=True)
        serializer = SerializerDetalleProducto(producto)
        return Response(serializer.data)

class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fav_count = Favoritos.objects.filter(usuario=request.user).count()
        
        # Obtener el carrito activo
        carrito = Carrito.objects.filter(usuario=request.user, status=True).first()
        if not carrito:
            return Response({'favorites_count': fav_count, 'cart_count': 0})

        # Contar paquetes únicos y productos únicos
        paquetes_unicos = Items.objects.filter(carrito=carrito, paquetes__isnull=False).values('paquetes').distinct().count()
        productos_unicos = Items.objects.filter(carrito=carrito, producto__isnull=False).values('producto').distinct().count()
        
        return Response({
            'favorites_count': fav_count,
            'cart_count': paquetes_unicos + productos_unicos
        })


class PerfilPublicoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, id):
        tipo = request.query_params.get('tipo')
        
        if tipo == 'agencia' or not tipo:
            try:
                agencia = Agencia.objects.get(pk=id)
                serializer = AgenciaPerfilSerializer(agencia)
                data = serializer.data
                data['es_agencia'] = True
                return Response(data)
            except Agencia.DoesNotExist:
                if tipo == 'agencia':
                    return Response({'error': 'Agencia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if tipo == 'proveedor' or not tipo:
            try:
                proveedor = Proveedor.objects.get(pk=id)
                serializer = ProveedorPerfilSerializer(proveedor)
                data = serializer.data
                data['es_proveedor'] = True
                return Response(data)
            except Proveedor.DoesNotExist:
                pass
                
        return Response({'error': 'Perfil público no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class PerfilView(APIView):
    """
    GET  /api/perfil/  → Devuelve el perfil del usuario autenticado según su rol.
    PATCH /api/perfil/ → Actualiza parcialmente el perfil. Ignora campos bloqueados.
    """
    permission_classes = [IsAuthenticated]

    def _get_instance_and_serializer(self, user):
        """
        Detecta el rol del usuario y retorna (instancia, clase_serializer).
        SEGURIDAD: Se utiliza 'user.pk' para garantizar que un usuario solo acceda a su propio perfil.
        """
        try:
            agencia = Agencia.objects.get(pk=user.pk)
            return agencia, AgenciaPerfilSerializer
        except Agencia.DoesNotExist:
            pass

        try:
            proveedor = Proveedor.objects.get(pk=user.pk)
            return proveedor, ProveedorPerfilSerializer
        except Proveedor.DoesNotExist:
            pass

        try:
            turista = Turista.objects.get(pk=user.pk)
            return turista, TuristaPerfilSerializer
        except Turista.DoesNotExist:
            pass

        return None, None

    def get(self, request):
        instance, SerializerClass = self._get_instance_and_serializer(request.user)
        if instance is None:
            return Response(
                {'error': 'No se encontró un perfil asociado a este usuario.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SerializerClass(instance)
        return Response(serializer.data)

    def patch(self, request):
        instance, SerializerClass = self._get_instance_and_serializer(request.user)
        if instance is None:
            return Response(
                {'error': 'No se encontró un perfil asociado a este usuario.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SerializerClass(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerfilFotoView(APIView):
    """
    POST /api/perfil/foto/ → Sube una imagen a Cloudinary.
    - query param ?tipo=portada  → Sube a foto_portada
    - default o ?tipo=perfil     → Sube a logotipo / foto_perfil
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            tipo = request.query_params.get('tipo', 'perfil')
            archivo = request.FILES.get('foto') or request.FILES.get('portada')
            
            print(f"DEBUG: Intento de carga de imagen - Tipo: {tipo}, Usuario: {request.user.email}")
            
            if not archivo:
                return Response(
                    {'error': 'No se proporcionó ningún archivo. Usa el campo "foto" o "portada".'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Identificar la instancia del perfil
            instance = None
            if hasattr(request.user, 'agencia'):
                instance = request.user.agencia
            elif hasattr(request.user, 'proveedor'):
                instance = request.user.proveedor
            elif hasattr(request.user, 'turista'):
                instance = request.user.turista

            if not instance:
                print(f"ERROR: Perfil no encontrado para el usuario {request.user.id}")
                return Response({'error': 'Perfil no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            # Decidir qué campo actualizar
            if tipo == 'portada':
                if hasattr(instance, 'foto_portada'):
                    instance.foto_portada = archivo
                    instance.save(update_fields=['foto_portada'])
                    # Refetch to ensure we have the processed Cloudinary URL
                    instance.refresh_from_db()
                    return Response({'foto_url': instance.foto_portada.url}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Este tipo de perfil no admite fotos de portada.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Perfil / Logotipo
                if hasattr(instance, 'logotipo'): # Agencia
                    instance.logotipo = archivo
                    instance.save(update_fields=['logotipo'])
                    instance.refresh_from_db()
                    return Response({'foto_url': instance.logotipo.url}, status=status.HTTP_200_OK)
                elif hasattr(instance, 'foto_perfil'): # Proveedor / Turista
                    instance.foto_perfil = archivo
                    instance.save(update_fields=['foto_perfil'])
                    instance.refresh_from_db()
                    return Response({'foto_url': instance.foto_perfil.url}, status=status.HTTP_200_OK)
                
            return Response({'error': 'No se pudo determinar el campo de imagen para este perfil.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            msg_error = str(e)
            print(f"CRITICAL ERROR EN CARGA DE IMAGEN: {msg_error}")
            return Response({
                'error': 'Error interno al procesar la imagen.',
                'detalle': msg_error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- VISTA MOCK PARA VALIDACIÓN DE CREDENCIALES LEGALES ---
class VerificarCredenciales(APIView):
    """
    Simula la validación de un NIT o RNT contra una base de datos estatal.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tipo = request.data.get('tipo', '').upper() # 'NIT' o 'RNT'
        numero = request.data.get('numero', '')

        if not tipo or not numero:
            return Response(
                {"error": "Debe proporcionar el tipo de documento y el número."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Simular latencia de red (2 segundos asíncronos en el cliente)
        time.sleep(2)

        # 2. Leer base de datos mock
        fixture_path = os.path.join(settings.BASE_DIR, 'autenticacion', 'fixtures', 'datos_gobierno.json')
        
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                db_gobierno = json.load(f)
            
            # 3. Validar existencia
            lista_blanca = db_gobierno.get(tipo, [])
            
            if str(numero) in [str(x) for x in lista_blanca]:
                return Response({
                    "valido": True,
                    "mensaje": f"El {tipo} {numero} ha sido verificado exitosamente en la base de datos del Estado."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "valido": False,
                    "mensaje": f"No se encontró registro para el {tipo} proporcionado."
                }, status=status.HTTP_404_NOT_FOUND)

        except FileNotFoundError:
            return Response(
                {"error": "Base de datos de gobierno no disponible (Mock file not found)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": f"Error interno al validar: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConfirmarPasswordView(APIView):
    """
    Verifica la contraseña del usuario antes de desbloquear secciones sensibles.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        
        if not password:
            return Response(
                {"error": "La contraseña es obligatoria."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar contra el usuario actual
        if request.user.check_password(password):
            return Response({"success": True, "mensaje": "Acceso concedido."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Contraseña incorrecta."}, status=status.HTTP_401_UNAUTHORIZED)

class ProcesarPagoView(APIView):
    """
    Endpoint para procesar la transacción final, guardar en DB, reducir stock y vaciar el carrito.
    Garantiza atomicidad total: o se procesa todo el carrito o no se guarda nada.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        items = data.get('items', [])
        novedades = data.get('novedades_turistas', [])

        if not items:
            return Response({'error': 'No hay items seleccionados para procesar.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Asegurar que el total sea un número decimal válido
                try:
                    total = round(float(data.get('total', 0)), 2)
                except (ValueError, TypeError):
                    total = 0

                # 2. Crear la Venta principal
                venta = Venta.objects.create(
                    usuario=request.user,
                    total=total,
                    novedades_turistas=novedades,
                    estado='Completado'
                )

                # 3. Procesar cada ítem del carrito
                for it in items:
                    tipo = it.get('tipo')
                    item_id = it.get('id')
                    cantidad = int(it.get('cantidad', 1))
                    
                    try:
                        precio_unitario = round(float(it.get('precio', 0)), 2)
                    except (ValueError, TypeError):
                        precio_unitario = 0

                    if not item_id or item_id == 0:
                        continue

                    if tipo == 'producto':
                        producto = Productos.objects.select_for_update().filter(pk=item_id).first()
                        if not producto:
                            raise ValueError(f"El producto con ID {item_id} no existe.")

                        if producto.stock < cantidad:
                             raise ValueError(f"Stock insuficiente para '{producto.nombre}'. Disponibles: {producto.stock}")

                        producto.stock -= cantidad
                        producto.save()
                        
                        Detalles_Venta.objects.create(
                            venta=venta,
                            producto=int(item_id),
                            paquete=0,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            estado='Pendiente de Empaque'
                        )

                    elif tipo == 'paquete' or tipo == 'tour':
                        paquete = PaqueteTuristico.objects.select_for_update().get(pk=item_id)
                        
                        # Determinar y validar la fecha de reserva
                        from datetime import date, timedelta
                        fecha_reserva_str = it.get('fecha_reserva')
                        fecha_reserva = None

                        if fecha_reserva_str:
                            try:
                                fecha_reserva = date.fromisoformat(fecha_reserva_str)
                            except (ValueError, TypeError):
                                pass

                        if not fecha_reserva and paquete.tipo_paquete == 'fijo':
                            fecha_reserva = paquete.fecha_realizacion

                        if not fecha_reserva:
                            raise ValueError(f"Debes seleccionar una fecha para el tour '{paquete.nombre}'.")

                        # Validar antelación (7 días mínimo)
                        fecha_minima = date.today() + timedelta(days=7)
                        if fecha_reserva < fecha_minima and paquete.tipo_paquete == 'flexible':
                            raise ValueError(f"La fecha de '{paquete.nombre}' debe ser al menos 7 días a futuro.")

                        # Validar cupos disponibles
                        from .serializers import calcular_cupos_disponibles
                        cupos = calcular_cupos_disponibles(paquete, fecha_reserva)
                        if cupos < cantidad:
                            raise ValueError(f"No hay cupos suficientes para '{paquete.nombre}' en la fecha {fecha_reserva}. Disponibles: {cupos}.")

                        Detalles_Venta.objects.create(
                            venta=venta,
                            producto=0,
                            paquete=int(item_id),
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            estado='Confirmado'
                        )

                        ReservaFecha.objects.create(
                            paquete=paquete,
                            venta=venta,
                            fecha=fecha_reserva,
                            cantidad=cantidad
                        )

                # 4. Vaciar el Carrito SOLO si todo lo anterior fue exitoso
                carrito = Carrito.objects.filter(usuario=request.user, status=True).first()
                if carrito:
                    Items.objects.filter(carrito=carrito).delete()

            # Fuera del bloque atomic, si llegamos aquí es que todo se guardó correctamente
            return Response({
                'exito': True, 
                'mensaje': 'Pago procesado exitosamente.',
                'venta_id': venta.id
            }, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"CRITICAL ERROR EN PAGO: {str(e)}")
            return Response({
                'error': 'Error interno al procesar el pago.',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MisReservasView(APIView):
    """
    GET /api/mis-reservas/
    Devuelve todas las reservas de paquetes turísticos del turista autenticado.
    Cada ítem incluye estado semántico: 'Confirmado', 'Cancelado' o 'Realizado'.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date as date_type
        try:
            if not Turista.objects.filter(pk=request.user.pk).exists():
                return Response({'error': 'Acceso restringido a turistas.'}, status=status.HTTP_403_FORBIDDEN)

            detalles = Detalles_Venta.objects.filter(
                venta__usuario=request.user,
                paquete__gt=0,
            ).select_related('venta').order_by('-venta__fecha')

            resultado = []
            hoy = date_type.today()

            for detalle in detalles:
                paquete = PaqueteTuristico.objects.filter(pk=detalle.paquete).select_related('agencia').prefetch_related('imagen_paquete').first()
                if not paquete:
                    continue

                reserva_fecha = ReservaFecha.objects.filter(
                    paquete=paquete,
                    venta=detalle.venta
                ).first()

                fecha_actividad = None
                if reserva_fecha:
                    fecha_actividad = str(reserva_fecha.fecha)
                elif paquete.fecha_realizacion:
                    fecha_actividad = str(paquete.fecha_realizacion)

                estado_raw = detalle.estado
                if estado_raw == 'Confirmado':
                    if fecha_actividad:
                        try:
                            from datetime import date as dt
                            fa = dt.fromisoformat(fecha_actividad)
                            if fa < hoy:
                                estado_semantico = 'Realizado'
                                # Persistencia: Actualizamos el estado en la base de datos
                                detalle.estado = 'Realizado'
                                detalle.save()
                            else:
                                estado_semantico = 'Confirmado'
                        except Exception:
                            estado_semantico = 'Confirmado'
                    else:
                        estado_semantico = 'Confirmado'
                elif estado_raw == 'Cancelado':
                    estado_semantico = 'Cancelado'
                elif estado_raw == 'Rechazado':
                    estado_semantico = 'Rechazado'
                else:
                    estado_semantico = estado_raw

                imagen_portada = None
                portada = paquete.imagen_paquete.filter(es_portada=True).first()
                if portada:
                    imagen_portada = portada.imagen.url
                else:
                    primera = paquete.imagen_paquete.first()
                    if primera:
                        imagen_portada = primera.imagen.url

                requerimientos = ''
                viajeros_lista = []
                novedades = detalle.venta.novedades_turistas or []
                if novedades and isinstance(novedades, list):
                    for v in novedades:
                        if isinstance(v, dict):
                            viajeros_lista.append({
                                'nombres':   v.get('nombres', ''),
                                'apellidos': v.get('apellidos', ''),
                                'tipo_doc':  v.get('tipo_doc', ''),
                                'num_doc':   v.get('num_doc', ''),
                                'edad':      v.get('edad', ''),
                                'novedades': v.get('novedades', '') or v.get('novedad', ''),
                            })
                    # Compatibilidad: requerimientos sigue siendo el del primer viajero
                    if viajeros_lista:
                        requerimientos = viajeros_lista[0].get('novedades', '')

                # Calificación si existe
                calificacion = ExperienciaCalificacion.objects.filter(detalle_venta=detalle).first()
                calif_data = ExperienciaCalificacionSerializer(calificacion).data if calificacion else None

                resultado.append({
                    'id': detalle.id,
                    'venta_id': detalle.venta.id,
                    'paquete_id': paquete.id,
                    'nombre': paquete.nombre,
                    'imagen': imagen_portada,
                    'agencia': paquete.agencia.nombre_agencia if paquete.agencia else '',
                    'ubicacion': paquete.ubicacion,
                    'fecha_actividad': fecha_actividad,
                    'cantidad': detalle.cantidad,
                    'precio_unitario': str(detalle.precio_unitario),
                    'precio_total': str(round(float(detalle.precio_unitario) * detalle.cantidad, 2)),
                    'estado': estado_semantico,
                    'calificacion': calif_data,
                    'requerimientos': requerimientos,
                    'viajeros': viajeros_lista,
                    'fecha_compra': str(detalle.venta.fecha.date()),
                })

            return Response(resultado, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR EN MisReservasView: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelarReservaView(APIView):
    """
    PATCH /api/mis-reservas/<pk>/cancelar/
    Cancela una reserva de paquete turístico del turista autenticado.
    Si la fecha de actividad es 8 o más días a futuro, restaura los cupos
    eliminando el registro ReservaFecha correspondiente.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        from datetime import date as date_type, timedelta
        try:
            if not Turista.objects.filter(pk=request.user.pk).exists():
                return Response({'error': 'Acceso restringido a turistas.'}, status=status.HTTP_403_FORBIDDEN)

            detalle = get_object_or_404(Detalles_Venta, pk=pk, venta__usuario=request.user)

            if detalle.paquete == 0:
                return Response({'error': 'Este ítem no es una reserva de paquete.'}, status=status.HTTP_400_BAD_REQUEST)

            if detalle.estado == 'Cancelado':
                return Response({'error': 'Esta reserva ya fue cancelada anteriormente.'}, status=status.HTTP_400_BAD_REQUEST)

            paquete = PaqueteTuristico.objects.filter(pk=detalle.paquete).first()
            if not paquete:
                return Response({'error': 'No se encontró el paquete turístico asociado.'}, status=status.HTTP_404_NOT_FOUND)

            hoy = date_type.today()
            cupos_restaurados = False

            reserva_fecha = ReservaFecha.objects.filter(
                paquete=paquete,
                venta=detalle.venta
            ).first()

            if reserva_fecha:
                dias_diferencia = (reserva_fecha.fecha - hoy).days
                if dias_diferencia >= 8:
                    # No eliminamos ReservaFecha para mantener visibilidad en la logística de la agencia
                    cupos_restaurados = True

            detalle.estado = 'Cancelado'
            detalle.save()

            venta = detalle.venta
            todos_cancelados = not Detalles_Venta.objects.filter(
                venta=venta,
                paquete__gt=0
            ).exclude(estado='Cancelado').exists()
            if todos_cancelados:
                venta.estado = 'Cancelado'
                venta.save()

            mensaje = 'Reserva cancelada exitosamente.'
            if cupos_restaurados:
                mensaje += ' Los cupos han sido restaurados para la fecha de la actividad.'

            return Response({
                'exito': True,
                'cupos_restaurados': cupos_restaurados,
                'mensaje': mensaje,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR EN CancelarReservaView: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GestionLogisticaAPIView(APIView):
    """
    GET /api/gestion-logistica/
    Retorna toda la data necesaria para el Gestor de Reservas (Agencias y Proveedores).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            # Detectar rol
            es_agencia = Agencia.objects.filter(pk=user.pk).exists()
            es_proveedor = Proveedor.objects.filter(pk=user.pk).exists()

            if not es_agencia and not es_proveedor:
                return Response({'error': 'Perfil de empresa no encontrado.'}, status=status.HTTP_403_FORBIDDEN)

            paquetes_list = []
            reservas_agrupadas = []
            rechazados_agrupados = []
            cancelaciones_list = []

            if es_agencia:
                # 1. Listado de paquetes de la agencia
                paquetes_obj = PaqueteTuristico.objects.filter(agencia_id=user.pk)
                hoy = date.today()
                for p in paquetes_obj:
                    cupos = calcular_cupos_disponibles(p, hoy)
                    paquetes_list.append({
                        'id': p.id,
                        'nombre': p.nombre,
                        'activo': p.activo,
                        'cupos_disponibles': cupos
                    })

                # 2. Reservas Agrupadas
                # Optimizamos trayendo todos los detalles de venta de los paquetes de la agencia de una vez
                detalles_dict = {}
                detalles_qs = Detalles_Venta.objects.filter(paquete__in=paquetes_obj.values_list('id', flat=True))
                for det in detalles_qs:
                    detalles_dict[(det.venta_id, det.paquete)] = det

                reservas_query = ReservaFecha.objects.filter(paquete__agencia_id=user.pk).select_related('paquete', 'venta', 'venta__usuario').order_by('fecha')
                
                agrupado_por_pk = {}
                agrupado_por_pk_rechazados = {}

                # 2. Agrupamiento por paquete con rastro de estados
                procesados = set() # (venta_id, pk_id)

                for res in reservas_query:
                    pk_id = res.paquete.id
                    
                    # Obtener detalle pre-cargado
                    detalle = detalles_dict.get((res.venta.id, pk_id))
                    
                    # Determinar estado (por defecto Confirmado si no se encuentra el detalle por alguna discrepancia)
                    estado_item = detalle.estado if detalle else 'Confirmado'
                    precio_item = float(detalle.precio_unitario) if detalle else float(res.paquete.precio)
                    detalle_id = detalle.id if detalle else None

                    # Determinar en qué grupo cae (Activo o Rechazado)
                    is_rejected = (estado_item in ['Cancelado', 'Rechazado'])
                    current_agrupado = agrupado_por_pk_rechazados if is_rejected else agrupado_por_pk

                    if pk_id not in current_agrupado:
                        # Buscar la imagen de portada
                        portada_obj = DestinoTuristico.objects.filter(paquete_id=pk_id, es_portada=True).first()
                        if not portada_obj:
                            portada_obj = DestinoTuristico.objects.filter(paquete_id=pk_id).first()
                        
                        current_agrupado[pk_id] = {
                            'paquete': {
                                'id': pk_id,
                                'nombre': res.paquete.nombre,
                                'portada': portada_obj.imagen.url if portada_obj and hasattr(portada_obj.imagen, 'url') else None,
                                'capacidad': res.paquete.capacidad,
                            },
                            'totalReservas': 0,
                            'reservasPorFecha': {}
                        }
                    
                    fecha_str = str(res.fecha)
                    if fecha_str not in current_agrupado[pk_id]['reservasPorFecha']:
                        current_agrupado[pk_id]['reservasPorFecha'][fecha_str] = {
                            'fecha': fecha_str,
                            'totalTuristas': 0,
                            'turistas': []
                        }
                    
                    novedades = res.venta.novedades_turistas
                    if isinstance(novedades, str):
                        try:
                            novedades = json.loads(novedades)
                        except:
                            novedades = []
                    
                    if not isinstance(novedades, list):
                        novedades = []

                    # Si no hay novedades, al menos mostrar al usuario de la venta como comprador
                    if not novedades:
                        novedades = [{
                            'nombres': res.venta.usuario.first_name,
                            'apellidos': res.venta.usuario.last_name,
                            'num_doc': 'N/A'
                        }]

                    for i, nov in enumerate(novedades):
                        comprador_nombre = f"{nov.get('nombres', '')} {nov.get('apellidos', '')}".strip() or res.venta.usuario.username
                        
                        # Obtener foto si es el comprador
                        comprador_foto = None
                        if i == 0:
                            v_u = res.venta.usuario
                            if hasattr(v_u, 'turista') and v_u.turista.foto_perfil:
                                comprador_foto = v_u.turista.foto_perfil.url
                            elif hasattr(v_u, 'proveedor') and v_u.proveedor.foto_perfil:
                                comprador_foto = v_u.proveedor.foto_perfil.url
                            elif hasattr(v_u, 'agencia') and v_u.agencia.logotipo:
                                comprador_foto = v_u.agencia.logotipo.url

                        viajero_data = {
                            'id_transaccion': f"{res.venta.id}",
                            'nombre': comprador_nombre,
                            'identificacion': nov.get('num_doc', 'N/A'),
                            'contacto': res.venta.usuario.email if i == 0 else 'N/A',
                            'es_comprador': (i == 0),
                            'rol': 'Comprador' if i == 0 else 'Pasajero',
                            'foto': comprador_foto,
                            'cupos': 1, # Cada fila es 1 persona
                            'monto_total': float(precio_item * detalle.cantidad) if (i == 0 and detalle) else 0,
                            'id_detalle': detalle_id,
                            'estado': estado_item
                        }
                        current_agrupado[pk_id]['reservasPorFecha'][fecha_str]['turistas'].append(viajero_data)

                    # Incremento de totales (UNA VEZ por reserva_fecha, no por cada pasajero)
                    current_agrupado[pk_id]['reservasPorFecha'][fecha_str]['totalTuristas'] += res.cantidad
                    current_agrupado[pk_id]['totalReservas'] += res.cantidad
                    procesados.add((res.venta.id, pk_id))

                # BARRIDO DE SEGURIDAD: Capturar rechazos que no tienen registro en ReservaFecha
                for (v_id, p_id), det in detalles_dict.items():
                    estado_det = str(det.estado).strip().title()
                    if estado_det in ['Cancelado', 'Rechazado'] and (v_id, p_id) not in procesados:
                        if p_id not in agrupado_por_pk_rechazados:
                            pk_obj = next((p for p in paquetes_obj if p.id == p_id), None)
                            if not pk_obj: continue
                            
                            portada_obj = DestinoTuristico.objects.filter(paquete_id=p_id, es_portada=True).first()
                            if not portada_obj:
                                portada_obj = DestinoTuristico.objects.filter(paquete_id=p_id).first()

                            agrupado_por_pk_rechazados[p_id] = {
                                'paquete': {
                                    'id': p_id,
                                    'nombre': pk_obj.nombre,
                                    'portada': portada_obj.imagen.url if portada_obj and hasattr(portada_obj.imagen, 'url') else None,
                                    'capacidad': pk_obj.capacidad,
                                },
                                'totalReservas': 0,
                                'reservasPorFecha': {}
                            }
                        
                        # Fallback a fecha de venta si no hay rastro de la fecha de reserva
                        f_res = str(det.fecha_reserva if hasattr(det, 'fecha_reserva') and det.fecha_reserva else det.venta.fecha.date())
                        if f_res not in agrupado_por_pk_rechazados[p_id]['reservasPorFecha']:
                            agrupado_por_pk_rechazados[p_id]['reservasPorFecha'][f_res] = {
                                'fecha': f_res,
                                'totalTuristas': 0,
                                'turistas': []
                            }
                        
                        v_u = det.venta.usuario
                        comprador_foto = None
                        if hasattr(v_u, 'turista') and v_u.turista.foto_perfil:
                            comprador_foto = v_u.turista.foto_perfil.url

                        viajero_data = {
                            'id_transaccion': f"{det.venta.id}",
                            'nombre': f"{v_u.first_name} {v_u.last_name}".strip() or v_u.username,
                            'identificacion': 'N/A',
                            'contacto': v_u.email,
                            'es_comprador': True,
                            'rol': 'Comprador',
                            'foto': comprador_foto,
                            'cupos': det.cantidad,
                            'monto_total': float(det.precio_unitario * det.cantidad),
                            'id_detalle': det.id,
                            'estado': estado_det
                        }
                        agrupado_por_pk_rechazados[p_id]['reservasPorFecha'][f_res]['turistas'].append(viajero_data)
                        agrupado_por_pk_rechazados[p_id]['reservasPorFecha'][f_res]['totalTuristas'] += det.cantidad
                        agrupado_por_pk_rechazados[p_id]['totalReservas'] += det.cantidad

                # Finalizar agrupamientos
                for pk_data in agrupado_por_pk.values():
                    pk_data['reservasPorFecha'] = sorted(pk_data['reservasPorFecha'].values(), key=lambda x: x['fecha'])
                    if pk_data['totalReservas'] > 0:
                        reservas_agrupadas.append(pk_data)

                for pk_data in agrupado_por_pk_rechazados.values():
                    pk_data['reservasPorFecha'] = sorted(pk_data['reservasPorFecha'].values(), key=lambda x: x['fecha'])
                    if pk_data['totalReservas'] > 0:
                        rechazados_agrupados.append(pk_data)

                # 3. Bitácora de Cancelaciones (Solo las que hace el turista)
                detalles_cancelados = Detalles_Venta.objects.filter(
                    paquete__in=paquetes_obj.values_list('id', flat=True),
                    estado='Cancelado'
                ).select_related('venta')
                
                for dc in detalles_cancelados:
                    p_info = next((p for p in paquetes_list if p['id'] == dc.paquete), None)
                    paquete_nombre = p_info['nombre'] if p_info else "Paquete"
                    
                    # Intentar obtener la fecha de salida desde ReservaFecha
                    reserva_fecha = ReservaFecha.objects.filter(venta=dc.venta, paquete__id=dc.paquete).first()
                    fecha_salida = str(reserva_fecha.fecha) if reserva_fecha else "N/A"
                        
                    cancelaciones_list.append({
                        'id_reserva': f"{dc.venta.id}",
                        'paquete_nombre': paquete_nombre,
                        'fecha_salida': fecha_salida,
                        'fecha_cancelacion': str(dc.venta.fecha),
                        'monto_reembolso': float(dc.precio_unitario * dc.cantidad)
                    })
                
                # Ordenar la bitácora por fecha de salida (más recientes primero)
                cancelaciones_list = sorted(cancelaciones_list, key=lambda x: x['fecha_salida'], reverse=True)

            elif es_proveedor:
                productos_obj = Productos.objects.filter(proveedor_id=user.pk)
                for prod in productos_obj:
                    paquetes_list.append({
                        'id': prod.id,
                        'nombre': prod.nombre,
                        'activo': prod.disponible,
                        'cupos_disponibles': prod.stock
                    })
                
                # Para proveedores, también incluimos rastro de rechazos y cancelaciones
                ventas_prod = Detalles_Venta.objects.filter(
                    producto__in=productos_obj.values_list('id', flat=True)
                ).select_related('venta', 'venta__usuario')

                agrupado_por_prod = {}
                agrupado_por_prod_rechazados = {}

                for vp in ventas_prod:
                    prod_id = vp.producto
                    prod_obj = next((p for p in productos_obj if p.id == prod_id), None)
                    if not prod_obj: continue

                    is_rejected_p = (vp.estado in ['Cancelado', 'Rechazado'])
                    current_ag_p = agrupado_por_prod_rechazados if is_rejected_p else agrupado_por_prod

                    if prod_id not in current_ag_p:
                        current_ag_p[prod_id] = {
                            'paquete': {'id': prod_id, 'nombre': prod_obj.nombre},
                            'totalReservas': 0,
                            'reservasPorFecha': {}
                        }
                    
                    fecha_str = str(vp.venta.fecha.date())
                    if fecha_str not in current_ag_p[prod_id]['reservasPorFecha']:
                         current_ag_p[prod_id]['reservasPorFecha'][fecha_str] = {
                            'fecha': fecha_str,
                            'totalTuristas': 0,
                            'turistas': []
                        }
                    
                    turista_data = {
                        'id_transaccion': f"{vp.venta.id}",
                        'comprador_principal': f"{vp.venta.usuario.first_name} {vp.venta.usuario.last_name}".strip() or vp.venta.usuario.username,
                        'identificacion': 'N/A',
                        'contacto': vp.venta.usuario.email,
                        'cupos': vp.cantidad,
                        'monto_total': float(vp.precio_unitario * vp.cantidad),
                        'acompanantes': [],
                        'id_detalle': vp.id,
                        'estado': vp.estado
                    }
                    current_ag_p[prod_id]['reservasPorFecha'][fecha_str]['turistas'].append(turista_data)
                    current_ag_p[prod_id]['reservasPorFecha'][fecha_str]['totalTuristas'] += vp.cantidad
                    current_ag_p[prod_id]['totalReservas'] += vp.cantidad

                for pr_data in agrupado_por_prod.values():
                    pr_data['reservasPorFecha'] = sorted(pr_data['reservasPorFecha'].values(), key=lambda x: x['fecha'], reverse=True)
                    reservas_agrupadas.append(pr_data)

                for pr_data in agrupado_por_prod_rechazados.values():
                    pr_data['reservasPorFecha'] = sorted(pr_data['reservasPorFecha'].values(), key=lambda x: x['fecha'], reverse=True)
                    rechazados_agrupados.append(pr_data)

            return Response({
                'paquetes': paquetes_list,
                'reservasAgrupadas': reservas_agrupadas,
                'rechazadosAgrupados': rechazados_agrupados,
                'cancelaciones': cancelaciones_list
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error en GestionLogisticaAPIView: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GestionAnularReservaAPIView(APIView):
    """
    POST /api/gestion-logistica/anular/
    Un proveedor o agencia anula una reserva/venta.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        detalle_id = request.data.get('id_detalle')
        if not detalle_id:
            return Response({'error': 'ID de detalle no proporcionado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            detalle = get_object_or_404(Detalles_Venta, pk=detalle_id)
            
            es_dueno = False
            if detalle.paquete > 0:
                es_dueno = PaqueteTuristico.objects.filter(pk=detalle.paquete, agencia_id=request.user.pk).exists()
            elif detalle.producto > 0:
                es_dueno = Productos.objects.filter(pk=detalle.producto, proveedor_id=request.user.pk).exists()
            
            if not es_dueno:
                return Response({'error': 'No tienes permiso para anular esta venta.'}, status=status.HTTP_403_FORBIDDEN)

            if detalle.estado == 'Cancelado':
                return Response({'error': 'Esta venta ya ha sido anulada.'}, status=status.HTTP_400_BAD_REQUEST)

            if detalle.paquete > 0:
                # No eliminamos ReservaFecha para que quede rastro en el dashboard de logística
                pass
            elif detalle.producto > 0:
                prod = Productos.objects.filter(pk=detalle.producto).first()
                if prod:
                    prod.stock += detalle.cantidad
                    prod.save()

            detalle.estado = 'Rechazado'
            detalle.save()

            return Response({'mensaje': 'Reserva rechazada correctamente.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GestionAnularSalidaAPIView(APIView):
    """
    POST /api/gestion-logistica/anular-salida/
    Anula todas las reservas de un paquete en una fecha específica.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        paquete_id = request.data.get('paquete_id')
        fecha = request.data.get('fecha')

        if not paquete_id or not fecha:
            return Response({'error': 'Paquete y fecha son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar que la agencia sea dueña del paquete
            paquete = get_object_or_404(PaqueteTuristico, pk=paquete_id, agencia_id=request.user.pk)
            
            # 1. Buscar todas las reservas vinculadas a esta fecha
            reservas_fecha = ReservaFecha.objects.filter(paquete=paquete, fecha=fecha)
            
            if not reservas_fecha.exists():
                return Response({'error': 'No hay reservas para esta fecha.'}, status=status.HTTP_404_NOT_FOUND)

            # 2. Obtener IDs de ventas involucradas
            ventas_ids = reservas_fecha.values_list('venta_id', flat=True)

            # 3. Anular detalles de venta correspondientes
            detalles = Detalles_Venta.objects.filter(venta_id__in=ventas_ids, paquete=paquete_id).exclude(estado='Rechazado').exclude(estado='Cancelado')
            
            count = detalles.count()
            detalles.update(estado='Rechazado')

            # 4. No eliminamos registros de ReservaFecha para rastro en Dashboard
            # reservas_fecha.delete()

            return Response({
                'message': f'Salida rechazada correctamente. {count} reservas marcadas como Rechazadas.',
                'count': count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
