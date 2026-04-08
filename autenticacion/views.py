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
            agencia_id = request.query_params.get('agencia_id', None)
            tours = PaqueteTuristico.objects.filter(activo=True).prefetch_related(
                'imagen_paquete', 'actividades'
            ).select_related('agencia', 'categoria_paquete')
            if agencia_id:
                tours = tours.filter(agencia_id=agencia_id)
            serializer = SerializerCatalogoTour(tours, many=True)
            return Response(serializer.data)
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

            if not producto_id and not paquetes_id:
                return Response({'error': 'Debe proporcionar un producto o un paquete.'}, status=status.HTTP_400_BAD_REQUEST)

            # Evitar duplicados del mismo paquete en el mismo carrito activo de forma segura
            item = Items.objects.filter(
                carrito=carrito,
                producto=producto_id if producto_id else None,
                paquetes=paquetes_id if paquetes_id else None
            ).first()
            
            created = False
            if not item:
                item = Items.objects.create(
                    carrito=carrito,
                    producto_id=producto_id if producto_id else None,
                    paquetes_id=paquetes_id if paquetes_id else None,
                    precio=precio
                )
                created = True

            serializer = CarritoItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR EN CARRITO: {str(e)}")
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
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
            print(f"DEBUG: Procesando pago para usuario {request.user.email}")
            print(f"DEBUG: Payload recibido: {data}")
            
            # Asegurar que el total sea un número decimal válido
            try:
                total = round(float(data.get('total', 0)), 2)
            except (ValueError, TypeError):
                total = 0

            novedades = data.get('novedades_turistas', [])
            items = data.get('items', [])

            if not items:
                return Response({'error': 'No hay items seleccionados para procesar.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la Venta
            venta = Venta.objects.create(
                usuario=request.user,
                total=total,
                novedades_turistas=novedades,
                estado='Completado'
            )
            
            # Procesar items y generar Detalles_Venta
            for it in items:
                tipo = it.get('tipo')
                item_id = it.get('id')
                cantidad = int(it.get('cantidad', 1))
                
                # Asegurar que el precio sea un número
                try:
                    precio = round(float(it.get('precio', 0)), 2)
                except (ValueError, TypeError):
                    precio = 0
                
                if not item_id or item_id == 0:
                    print(f"WARNING: Item saltado por ID inválido: {it}")
                    continue

                if tipo == 'producto':
                    producto = Productos.objects.filter(pk=item_id).first()
                    if not producto:
                         raise ValueError(f"El producto con ID {item_id} no existe en la base de datos.")

                    # Reducir stock
                    if producto.stock >= cantidad:
                        producto.stock -= cantidad
                    else:
                        producto.stock = 0
                    producto.save()
                    
                    Detalles_Venta.objects.create(
                        venta=venta,
                        producto=int(item_id),
                        paquete=0,
                        cantidad=cantidad,
                        precio_unitario=precio
                    )
                elif tipo == 'paquete' or tipo == 'tour':
                    paquete = PaqueteTuristico.objects.filter(pk=item_id).first()
                    if not paquete:
                         raise ValueError(f"El paquete/tour con ID {item_id} no existe en la base de datos.")

                    Detalles_Venta.objects.create(
                        venta=venta,
                        producto=0,
                        paquete=int(item_id),
                        cantidad=cantidad,
                        precio_unitario=precio
                    )

            # Vaciar el Carrito en base de datos
            carrito = Carrito.objects.filter(usuario=request.user, status=True).first()
            if carrito:
                Items.objects.filter(carrito=carrito).delete()
                
            # Enviar correo de confirmación
            msg_body = (
                f"¡Hola {request.user.username}!\n\n"
                f"Gracias por confiar en Amazonia Viva.\n"
                f"Te confirmamos que hemos recibido exitosamente el pago por tu compra.\n\n"
                f"💳 Total de la compra: ${total}\n"
                f"✅ Estado de transacción: Pagado\n\n"
                f"¡Prepárate para la aventura de tu vida!\n"
                f"Atentamente, el equipo de Amazonia Viva."
            )
            
            send_mail(
                subject="Confirmación de tu reserva - Amazonia Viva",
                message=msg_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,  # Cambiado a False para depuración
            )
                
            return Response({
                'exito': True, 
                'mensaje': 'Pago procesado y compra guardada exitosamente.',
                'venta_id': venta.id
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as ve:
            print(f"ERROR DE VALIDACIÓN EN VENTA: {str(ve)}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg_error = str(e)
            print(f"CRITICAL ERROR EN VENTA: {msg_error}")
            return Response({
                'error': 'Error interno del servidor al procesar el pago.',
                'detalle': msg_error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

