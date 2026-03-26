from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import json
from .models import Productos, Proveedor
from .serializers_productos import ProductoSerializer
class ProductosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_catalogo = request.query_params.get('tipo_catalogo', None)
        
        # Si el usuario es proveedor, solo ve sus productos
        if hasattr(request.user, 'proveedor'):
            productos = Productos.objects.filter(proveedor=request.user.proveedor)
        else:
            # Para otros roles (admin/turista/agencia en ciertos contextos) ven todo o segun filtro
            productos = Productos.objects.all()
            
        if tipo_catalogo:
            productos = productos.filter(tipo_catalogo=tipo_catalogo)
            
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            # Asignar proveedor logueado o tomar el primero si es entorno dev local
            proveedor = None
            if hasattr(request.user, 'proveedor'):
                proveedor = request.user.proveedor
            
            if not proveedor:
                return Response({"error": "No tienes una cuenta de proveedor activa."}, status=status.HTTP_403_FORBIDDEN)

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
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        producto = get_object_or_404(Productos, pk=pk)
        
        # Verificar propiedad
        if hasattr(request.user, 'proveedor') and producto.proveedor != request.user.proveedor:
            return Response({"error": "No tienes permiso para modificar este producto."}, status=status.HTTP_403_FORBIDDEN)
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
        
        # Verificar propiedad
        if hasattr(request.user, 'proveedor') and producto.proveedor != request.user.proveedor:
            return Response({"error": "No tienes permiso para eliminar este producto."}, status=status.HTTP_403_FORBIDDEN)
            
        producto.delete()
        return Response({'mensaje': 'Producto eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)
