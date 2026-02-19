from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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

class Agencia(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, null=True, blank=False)
    nombre_agencia = models.CharField(max_length=50, null=False, blank=False)
    latitud = models.DecimalField(max_digits=10,decimal_places=10, null=False, blank=False)
    logitud = models.DecimalField(max_digits=10,decimal_places=10, null=False, blank=False)
    numero_telefonico = models.CharField(max_length=20, null=False, blank=False)
    logotipo = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    red_social = models.URLField(max_length=200, null=False, blank=False)
    nit = models.CharField(max_length=20, null=False, blank=False)
    rnt = models.CharField(max_length=20, null=False, blank=False)
    rut = models.CharField(max_length=20, null=False, blank=False)
    horario_atencion = models.CharField(max_length=100, null=False, blank=False)


    def __str__(self):
        return f'{self.nombre_agencia}'
    
class Proveedor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, null=True, blank=False)
    nombre_empresa = models.CharField(max_length=50, null=False, blank=False)
    nit = models.CharField(max_length=20, null=False, blank=False)
    rut = models.CharField(max_length=20, null=False, blank=False)
    latitud = models.DecimalField(max_digits=10,decimal_places=10, null=False, blank=False)
    logitid = models.DecimalField(max_digits=10,decimal_places=10, null=False, blank=False)
    numero_telefonico = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return f'{self.nombre_empresa}'
