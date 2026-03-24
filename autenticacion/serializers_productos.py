from rest_framework import serializers
from .models import Productos, ProductoImagen, Proveedor

class ProductoImagenSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    def get_url(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return None

    class Meta:
        model = ProductoImagen
        fields = ['id', 'url', 'es_portada']

class ProductoSerializer(serializers.ModelSerializer):
    imagen_producto = ProductoImagenSerializer(many=True, read_only=True)
    archivos_subidos = serializers.ListField(
        child=serializers.ImageField(), 
        write_only=True, 
        required=False
    )
    imagenes_eliminar = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    proveedor = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Productos
        fields = [
            'id', 'nombre', 'sku', 'caracteristicas', 'stock', 'precio', 
            'disponible', 'categorias', 'proveedor', 'tipo_catalogo',
            'imagen_producto', 'archivos_subidos', 'imagenes_eliminar'
        ]

    def create(self, validated_data):
        archivos = validated_data.pop('archivos_subidos', [])
        producto = Productos.objects.create(**validated_data)

        if archivos:
            for archivo in archivos:
                ProductoImagen.objects.create(producto=producto, imagen=archivo)

        return producto

    def update(self, instance, validated_data):
        archivos = validated_data.pop('archivos_subidos', [])
        imagenes_eliminar_list = validated_data.pop('imagenes_eliminar', [])
        
        if imagenes_eliminar_list:
            import cloudinary.uploader
            for img_id in imagenes_eliminar_list:
                try:
                    img = ProductoImagen.objects.get(id=img_id, producto=instance)
                    if img.imagen:
                        cloudinary.uploader.destroy(img.imagen.public_id)
                    img.delete()
                except ProductoImagen.DoesNotExist:
                    pass

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if archivos:
            for archivo in archivos:
                ProductoImagen.objects.create(producto=instance, imagen=archivo)
                
        return instance
