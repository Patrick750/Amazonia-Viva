from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from .serializers import UsuarioSerializer, ProveedorSerializers
from .models import *

# Create your views here.
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

class VerificarEmail(APIView):
    def verificar(self, request):
        formEmail = request.data.get('email')

        existe = Usuario.objects.filter(email=formEmail).exists()

        return Response({
            'existe':existe
        })

def login(request):
    return render(request, 'core/login.html')
