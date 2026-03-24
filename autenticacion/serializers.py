from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import Group

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
    url = serializers.ImageField(source='imagen') 
    
    class Meta:
        model = DestinoTuristico # Antes decía models
        fields = ['id', 'url', 'es_portada'] # Antes decía field y faltaba 'url'

class SerializersCreateNewPack(serializers.ModelSerializer):
    imagen_paquete = SerializersImages(many=True, read_only=True)
    archivos_subidos = serializers.ListField(
        child=serializers.ImageField(), 
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
            'id', 'nombre', 'descripcion', 'precio', 'duracion', 
            'ubicacion', 'latitud', 'longitud', 'capacidad', 
            'actividades', 'itinerario', 'incluido', 
            'imagen_paquete', 'archivos_subidos', 'agencia'
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
        actividades_data = validated_data.pop('actividades', None)
        
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
    class Meta:
        model = PaqueteTuristico
        fields = '__all__'
