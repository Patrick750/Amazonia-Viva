from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import Group

class CategoriaPaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPaquete
        fields = '__all__'

class AgenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agencia
        fields = ['id','nombre_agencia', 'username','email','numero_telefonico','password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        agencia = Agencia(**validated_data)
        agencia.set_password(password)
        agencia.save()

        try:
            grupo_agencia = Group.objects.get(name='agencia')   
            agencia.groups.add(grupo_agencia)
        except Group.DoesNotExist:
            print("El grupo 'Agencia' no existe. Por favor, créalo en el admin de Django.")
        return agencia
    

class ProveedorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id','nombre_empresa','username','email','numero_telefonico','password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        proveedor = Proveedor(**validated_data)
        proveedor.set_password(password)
        proveedor.save()

        try:
            grupo_proveedor = Group.objects.get(name='proveedor')   
            proveedor.groups.add(grupo_proveedor)
        except Group.DoesNotExist:
            print("El grupo 'Proveedor' no existe. Por favor, créalo en el admin de Django.")
        return proveedor
    
class TuristaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Turista
        fields = ['id','first_name', 'last_name','username','fecha_nacimiento','numero_identidad','email','password']
    def create(self, validated_data):
        password = validated_data.pop('password')
        turista = Turista(**validated_data)
        turista.set_password(password)
        turista.save()

        try:
            group_turista = Group.objects.get(name='turista')
            turista.groups.add(group_turista)
        except Group.DoesNotExist:
            print("El grupo 'Turista' no existe. Por favor, créalo en el admin de Django.")
        return turista
    
#Serializador del login
class SerializersLogin(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        nombre_agencia = None
        nombre_proveedor = None
        if hasattr(self.user, 'agencia'):
            nombre_agencia = self.user.agencia.nombre_agencia
        if hasattr(self.user, 'proveedor'):
            nombre_proveedor = self.user.proveedor.nombre_empresa

        data['usuario'] = {
            'nombre_empresa': nombre_proveedor,
            'nombre_agencia': nombre_agencia,
            'username': self.user.username,
            'nombre':self.user.first_name,
            'apellido': self.user.last_name,
            'email': self.user.email,
            'group': self.user.groups.first().name if self.user.groups.exists() else None
        }
        return data

class SerializersActividades(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'

class SerializersImages(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    def get_url(self, obj):
        # CloudinaryField tiene una propiedad .url que retorna la URL completa del CDN
        if obj.imagen:
            return obj.imagen.url
        return None

    class Meta:
        model = DestinoTuristico
        fields = ['id', 'url', 'es_portada']

class SerializersCreateNewPack(serializers.ModelSerializer):
    imagen_paquete = SerializersImages(many=True, read_only=True)
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
    agencia = serializers.PrimaryKeyRelatedField(
        queryset=Agencia.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = PaqueteTuristico
        fields = [
            'id', 'activo', 'nombre', 'descripcion', 'precio', 'duracion', 
            'ubicacion', 'latitud', 'longitud', 'capacidad', 
            'actividades', 'itinerario', 'incluido', 
            'imagen_paquete', 'archivos_subidos', 'imagenes_eliminar', 'agencia',
            'categoria_paquete'
        ]

    def create(self, validated_data):
        archivos = validated_data.pop('archivos_subidos', [])
        
        actividades_data = validated_data.pop('actividades', [])
        
        paquete = PaqueteTuristico.objects.create(**validated_data)

        if actividades_data:
            paquete.actividades.set(actividades_data)

        # 2. Guardamos las imágenes
        if archivos:
            for archivo in archivos:
                DestinoTuristico.objects.create(paquete=paquete, imagen=archivo)

        return paquete

    def update(self, instance, validated_data):
        archivos = validated_data.pop('archivos_subidos', [])
        imagenes_eliminar_list = validated_data.pop('imagenes_eliminar', [])
        actividades_data = validated_data.pop('actividades', None)
        
        if imagenes_eliminar_list:
            import cloudinary.uploader
            for img_id in imagenes_eliminar_list:
                try:
                    img = DestinoTuristico.objects.get(id=img_id, paquete=instance)
                    if img.imagen:
                        cloudinary.uploader.destroy(img.imagen.public_id)
                    img.delete()
                except DestinoTuristico.DoesNotExist:
                    pass

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if actividades_data is not None:
            instance.actividades.set(actividades_data)
            
        if archivos:
            for archivo in archivos:
                DestinoTuristico.objects.create(paquete=instance, imagen=archivo)
                
        return instance

class SerializersImagenes(serializers.ModelSerializer):
    class Meta:
        model = DestinoTuristico
        fields = '__all__'

class SerializersPaquetes(serializers.ModelSerializer):
    imagen_paquete = SerializersImages(many=True, read_only=True)

    class Meta:
        model = PaqueteTuristico
        fields = '__all__'


class SerializerCatalogoTour(serializers.ModelSerializer):
    imagen_portada = serializers.SerializerMethodField()
    nombre_agencia = serializers.CharField(source='agencia.nombre_agencia', read_only=True)
    ciudad = serializers.CharField(source='ubicacion', read_only=True)
    nivel_riesgo = serializers.SerializerMethodField()
    num_calificaciones = serializers.SerializerMethodField()

    categoria_paquete_nombre = serializers.CharField(source='categoria_paquete.nombre', read_only=True)

    def get_imagen_portada(self, obj):
        portada = obj.imagen_paquete.filter(es_portada=True).first()
        if not portada:
            portada = obj.imagen_paquete.first()
        if portada and portada.imagen:
            return portada.imagen.url
        return None

    def get_nivel_riesgo(self, obj):
        niveles = obj.actividades.values_list('nivel_riesgo', flat=True)
        return max(niveles) if niveles else 0

    def get_num_calificaciones(self, obj):
        return 0  # Placeholder until rating system is implemented

    class Meta:
        model = PaqueteTuristico
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'duracion',
            'ubicacion', 'ciudad', 'rating', 'num_calificaciones',
            'imagen_portada', 'nombre_agencia', 'nivel_riesgo', 'activo',
            'categoria_paquete_nombre', 'categoria_paquete'
        ]


class SerializerCatalogoProductoImagen(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return None

    class Meta:
        model = ProductoImagen
        fields = ['id', 'url', 'es_portada']


class SerializerCatalogoProducto(serializers.ModelSerializer):
    imagen_portada = serializers.SerializerMethodField()
    nombre_proveedor = serializers.CharField(source='proveedor.nombre_empresa', read_only=True)
    nombre_categoria = serializers.CharField(source='categorias.nombre', read_only=True)
    num_calificaciones = serializers.SerializerMethodField()
    descripcion_corta = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_imagen_portada(self, obj):
        portada = obj.imagen_producto.filter(es_portada=True).first()
        if not portada:
            portada = obj.imagen_producto.first()
        if portada and portada.imagen:
            return portada.imagen.url
        return None

    def get_num_calificaciones(self, obj):
        return 0

    def get_descripcion_corta(self, obj):
        # Build a short description from caracteristicas JSON
        caract = obj.caracteristicas
        if isinstance(caract, dict):
            items = [f"{k}: {v}" for k, v in list(caract.items())[:3]]
            return ' · '.join(items) if items else 'Sin descripción'
        return 'Sin descripción'

    def get_rating(self, obj):
        return 0

    class Meta:
        model = Productos
        fields = [
            'id', 'nombre', 'descripcion_corta', 'precio', 'stock',
            'disponible', 'tipo_catalogo', 'nombre_categoria',
            'imagen_portada', 'nombre_proveedor', 'rating', 'num_calificaciones'
        ]
