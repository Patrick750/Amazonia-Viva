from rest_framework import serializers
from .models import Usuario,Agencia,Proveedor, Turista
from django.contrib.auth.models import Group

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agencia
        fields = ['id','nombre_agencia', 'username','email','numero_telefonico','password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        agencia = Agencia(**validated_data)
        agencia.set_password(password)
        agencia.save()

        try:
            grupo_agencia = Group.objects.get(name='Agencia')   
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
            grupo_proveedor = Group.objects.get(name='Proveedor')   
            proveedor.groups.add(grupo_proveedor)
        except Group.DoesNotExist:
            print("El grupo 'Proveedor' no existe. Por favor, créalo en el admin de Django.")
        return proveedor
    
class TuristaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Turista
        fields = ['id','first_name', 'last_name','fecha_nacimiento','numero_identidad','password']
    def create(self, validated_data):
        password = validated_data.pop('password')
        turista = Turista(**validated_data)
        turista.set_password(password)
        turista.save()

        try:
            group_turista = Group.objects.get(name='Turista')
            turista.groups.add(group_turista)
        except Group.DoesNotExist:
            print("El grupo 'Turista' no existe. Por favor, créalo en el admin de Django.")
        return turista


        