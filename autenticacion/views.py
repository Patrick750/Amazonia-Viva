from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

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