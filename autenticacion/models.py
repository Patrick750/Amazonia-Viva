from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Create your models here.
class Usuario(AbstractUser):
    group = models.ManyToManyField(
        Group, 
        related_name='usuarios',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_query_name="usuario",
    )
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Agencia(Usuario):

    nombre_agencia = models.CharField(max_length=50, null=False, blank=False)
    latitud = models.DecimalField(max_digits=10,decimal_places=10, blank=True,null=True)
    logitud = models.DecimalField(max_digits=10,decimal_places=10, blank=True,null=True)
    numero_telefonico = models.CharField(max_length=20, null=False, blank=False)
    logotipo = models.CharField(max_length=255, blank=True,null=True)
    descripcion = models.CharField(max_length=255, blank=True,null=True)
    red_social = models.URLField(max_length=200, blank=True,null=True)
    nit = models.CharField(max_length=20, blank=True,null=True)
    rnt = models.CharField(max_length=20, blank=True,null=True)
    rut = models.CharField(max_length=20, blank=True,null=True)
    horario_atencion = models.CharField(max_length=100, blank=True,null=True)


    def __str__(self):
        return f'{self.nombre_agencia}'
    
class Proveedor(Usuario):
    nombre_empresa = models.CharField(max_length=50, null=False, blank=False)
    nit = models.CharField(max_length=20, blank=True,null=True)
    rut = models.CharField(max_length=20, blank=True,null=True)
    latitud = models.DecimalField(max_digits=10,decimal_places=10, blank=True, null=True)
    logitid = models.DecimalField(max_digits=10,decimal_places=10, blank=True, null=True)
    numero_telefonico = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return f'{self.nombre_empresa}'
    
class Turista(Usuario):
    fecha_nacimiento = models.DateField(blank=False, null=False)
    numero_identidad = models.CharField(max_length=15, blank=False, null=False)

class Paquetes(models.Model):
    nombre = models.CharField(max_length=40, null=False, blank=False)
    duracion_horas = models.IntegerField(null=False, blank=False)
    precio = models.DecimalField(max_digits=10000000000000,decimal_places=100, null=False, blank=False)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    nivel_riesgo = models.IntegerField(null=False, blank=False)
    caracteristicas = models.JSONField(default=dict, blank=True, null=True)
    imagenes = models.JSONField(default=dict,null=True)
    agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE, related_name='paquetes')

class Categorias(models.Model):
    nombre = models.CharField(max_length=30, null=False, blank=False)
    caracteristicas = models.JSONField(default=dict, null=True)

class Productos(models.Model):
    nombre = models.CharField(max_length=40,null=False,blank=False)
    sku = models.CharField(max_length=150, null=False, blank=False)
    caracterisitcas = models.JSONField(default=dict, blank=True)
    imagenes = models.JSONField(default=dict, null=True)
    stock = models.IntegerField(null=False, blank=False)
    precio = models.DecimalField(decimal_places=1000,max_digits=10000, null=False, blank=False)
    disponible = models.BooleanField(null=False, blank=False)
    categorias = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name='categorias')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='proveedor')
    


