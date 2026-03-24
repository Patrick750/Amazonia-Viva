from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from cloudinary.models import CloudinaryField

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
    latitud = models.DecimalField(max_digits=10,decimal_places=8, blank=True, null=True)
    logitid = models.DecimalField(max_digits=10,decimal_places=8, blank=True, null=True)
    numero_telefonico = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return f'{self.nombre_empresa}'
    
class Turista(Usuario):
    fecha_nacimiento = models.DateField(blank=False, null=False)
    numero_identidad = models.CharField(max_length=15, blank=False, null=False)

class Categoria(models.Model):
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nombre de la Categoría"
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    nombre = models.CharField(
        max_length=150, 
        verbose_name="Nombre de la Actividad"
    )
    nivel_riesgo = models.PositiveSmallIntegerField(
        verbose_name="Nivel de Riesgo (1-10)",
        help_text="Escala del 1 (Mínimo) al 10 (Extremo)"
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name="actividades", # Esto es clave para la API
        verbose_name="Categoría"
    )

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel_riesgo})"

class PaqueteTuristico(models.Model):
    # --- Datos Básicos ---
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Tour")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (COP)")
    duracion = models.CharField(max_length=100, verbose_name="Duración")
    capacidad = models.PositiveIntegerField(verbose_name="Capacidad Máxima")
    
    # --- Ubicación y Mapas ---
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación (Texto)")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # --- Agencia propietaria ---
    agencia = models.ForeignKey(
        'Agencia',
        on_delete=models.CASCADE,
        related_name='paquetes_agencia',
        verbose_name="Agencia"
    )

    # --- LA RELACIÓN CON TUS CATEGORÍAS/ACTIVIDADES ---
    actividades = models.ManyToManyField(
        Actividad, 
        related_name='paquetes',
        verbose_name="Actividades Incluidas"
    )

    # --- LOS CAMPOS DINÁMICOS DE VUE ---
    # JSONField es perfecto para guardar exactamente los arrays que generamos en el frontend
    itinerario = models.JSONField(
        default=list, 
        verbose_name="Itinerario Detallado",
        help_text="Formato esperado: [{'time': '08:00', 'activity': 'Salida'}]"
    )
    incluido = models.JSONField(
        default=list, 
        verbose_name="Qué incluye",
        help_text="Formato esperado: [{'item': 'Transporte'}]"
    )
    
    rating = models.DecimalField(decimal_places=100, max_digits=100, null=False, default=0)

    class Meta:
        verbose_name = "Paquete Turístico"
        verbose_name_plural = "Paquetes Turísticos"

    def __str__(self):
        return self.nombre
    
class DestinoTuristico(models.Model):
    imagen = CloudinaryField('image', folder='amazonia_viva/destinos')
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE, related_name='imagen_paquete')
    es_portada = models.BooleanField(default=False)


class Categorias(models.Model):
    nombre = models.CharField(max_length=30, null=False, blank=False)
    caracteristicas = models.JSONField(default=dict, null=True)

class Productos(models.Model):
    nombre = models.CharField(max_length=40,null=False,blank=False)
    sku = models.CharField(max_length=150, null=False, blank=False)
    caracterisitcas = models.JSONField(default=dict, blank=True)
    imagenes = models.JSONField(default=dict, null=True)
    stock = models.IntegerField(null=False, blank=False)
    precio = models.DecimalField(decimal_places=1000,max_digits=1000, null=False, blank=False)
    disponible = models.BooleanField(null=False, blank=False)
    categorias = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name='producto_categorias')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='producto_proveedor')
    
class Estados(models.Model):
    estado = models.CharField(max_length=40, null=False, blank=False)

class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrito_usuario')
    status = models.BooleanField(null=False)

class Items(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE,  related_name='item_carrito')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE,  related_name='item_productos')
    paquetes = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE,  related_name='item_paquetes')
    precio = models.DecimalField(decimal_places=1000,max_digits=1000, null=False, blank=False)

class Favoritos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='favorito_usuario')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE,  related_name='favorito_productos')
    paquetes = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE,  related_name='favorito_paquetes')

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(decimal_places=1000, max_digits=1000, null=False, blank=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='venta_usuario')
    fotograficas = models.JSONField(default=dict, null=True)
    estado = models.CharField(max_length=40, null=False, blank=False)

class Detalles_Venta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles_venta')
    producto = models.IntegerField(null=False, blank=False)
    paquete = models.IntegerField(null=False, blank=False)
    cantidad = models.IntegerField(null=False, blank=False)
    precio_unitario = models.DecimalField(decimal_places=1000, max_digits=1000, null=False, blank=False)
    

