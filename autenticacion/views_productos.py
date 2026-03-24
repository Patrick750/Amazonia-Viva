from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import json
from .models import Productos, Proveedor
from .serializers_productos import ProductoSerializer

class ProductosAPIView(APIView):
    def get(self, request):
        tipo_catalogo = request.query_params.get('tipo_catalogo', None)
        if tipo_catalogo:
            productos = Productos.objects.filter(tipo_catalogo=tipo_catalogo)
        else:
            productos = Productos.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            # Asignar proveedor logueado o tomar el primero si es entorno dev local
            proveedor = None
            if hasattr(request.user, 'proveedor'):
                proveedor = request.user.proveedor
            elif Proveedor.objects.exists():
                proveedor = Proveedor.objects.first()

            data = {}
            for key in request.data.keys():
                if key in ['archivos_subidos', 'imagenes_eliminar']:
                    data[key] = request.data.getlist(key)
                elif key == 'caracteristicas':
                    try:
                        data[key] = json.loads(request.data.get(key))
                    except:
                        data[key] = request.data.get(key)
                elif key == 'disponible':
                    data[key] = str(request.data.get(key)).lower() == 'true'
                else:
                    data[key] = request.data.get(key)
                    
            if proveedor:
                data['proveedor'] = proveedor.id

            serializer = ProductoSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'mensaje': 'Producto guardado exitosamente.', 'producto': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'errores': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductoDetalleAPIView(APIView):
    def put(self, request, pk):
        producto = get_object_or_404(Productos, pk=pk)
        data = {}
        for key in request.data.keys():
            if key in ['archivos_subidos', 'imagenes_eliminar']:
                data[key] = request.data.getlist(key)
            elif key == 'caracteristicas':
                try:
                    data[key] = json.loads(request.data.get(key))
                except:
                    data[key] = request.data.get(key)
            elif key == 'disponible':
                data[key] = str(request.data.get(key)).lower() == 'true'
            else:
                data[key] = request.data.get(key)
        
        serializer = ProductoSerializer(producto, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Producto actualizado con éxito.', 'producto': serializer.data}, status=status.HTTP_200_OK)
        return Response({'errores': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        producto = get_object_or_404(Productos, pk=pk)
        producto.delete()
        return Response({'mensaje': 'Producto eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)
