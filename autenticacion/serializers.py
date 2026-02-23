from rest_framework import serializers
from .models import Usuario,Agencia,Proveedor
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



        