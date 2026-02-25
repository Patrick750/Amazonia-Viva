from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from .serializers import UsuarioSerializer, ProveedorSerializers, TuristaSerializers
from .models import *

# Create your views here.

#Registro de nueva agencia
class RegistroAgencia(APIView):
    def post(self, request):
        serializers = UsuarioSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()  
        
            return Response(
                {"mensaje":"Agencia registrada existosamente"},
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
                {"mensaje":"Proveedor registrado existosamente"},
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
                {"mensaje":"Turista registrada existosamente"},
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


def login(request):
    return render(request, 'core/login.html')
