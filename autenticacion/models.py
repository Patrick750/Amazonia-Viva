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

@receiver(post_migrate)
def crear_roles_por_defecto(sender, **kwargs):
    # get_or_create busca el grupo; si no existe, lo crea.
    # Así evitas errores de duplicados si corres el migrate varias veces.
    Group.objects.get_or_create(name='Turista')   # ID 1
    Group.objects.get_or_create(name='Agencia')   # ID 2
    Group.objects.get_or_create(name='Proveedor') # ID 3