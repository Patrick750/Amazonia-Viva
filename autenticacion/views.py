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
    def get(self, request):
        try:
            paquetes = PaqueteTuristico.objects.all()
            serializers = SerializersPaquetes(paquetes, many=True)
            return Response(serializers.data)
        except Exception as e:
            return Response({'mensaje':'Hubo un error'})


class CatalogoTours(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            tours = PaqueteTuristico.objects.filter(activo=True).prefetch_related(
                'imagen_paquete', 'actividades'
            ).select_related('agencia', 'categoria_paquete')
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
            productos = Productos.objects.filter(disponible=True).prefetch_related(
                'imagen_producto'
            ).select_related('proveedor', 'categorias')
            if tipo:
                productos = productos.filter(tipo_catalogo=tipo)
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
    POST /api/perfil/foto/ → Sube una imagen a Cloudinary y guarda la referencia
    en el campo de foto/logotipo del perfil del usuario autenticado.
    Retorna la URL pública de la imagen subida.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        archivo = request.FILES.get('foto')
        if not archivo:
            return Response(
                {'error': 'No se proporcionó ningún archivo. Usa el campo "foto".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Detectar rol y guardar en el campo correcto
        try:
            instance = Agencia.objects.get(pk=request.user.pk)
            instance.logotipo = archivo
            instance.save(update_fields=['logotipo'])
            return Response({'foto_url': instance.logotipo.url}, status=status.HTTP_200_OK)
        except Agencia.DoesNotExist:
            pass

        try:
            instance = Proveedor.objects.get(pk=request.user.pk)
            instance.foto_perfil = archivo
            instance.save(update_fields=['foto_perfil'])
            return Response({'foto_url': instance.foto_perfil.url}, status=status.HTTP_200_OK)
        except Proveedor.DoesNotExist:
            pass

        try:
            instance = Turista.objects.get(pk=request.user.pk)
            instance.foto_perfil = archivo
            instance.save(update_fields=['foto_perfil'])
            return Response({'foto_url': instance.foto_perfil.url}, status=status.HTTP_200_OK)
        except Turista.DoesNotExist:
            pass

        return Response(
            {'error': 'No se encontró un perfil asociado a este usuario.'},
            status=status.HTTP_404_NOT_FOUND
        )

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
