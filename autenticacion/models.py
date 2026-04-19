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
    latitud = models.DecimalField(max_digits=10,decimal_places=8, blank=True,null=True)
    logitud = models.DecimalField(max_digits=10,decimal_places=8, blank=True,null=True)
    numero_telefonico = models.CharField(max_length=20, null=True, blank=True)
    logotipo = CloudinaryField('image', folder='amazonia_viva/perfiles', blank=True, null=True)
    foto_portada = CloudinaryField('image', folder='amazonia_viva/portadas', blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True,null=True)
    informacion_contacto = models.JSONField(default=dict, blank=True, null=True, help_text="Diccionario de redes sociales: {'instagram': 'url', 'facebook': 'url', 'whatsapp': 'numero'}")
    nit = models.CharField(max_length=20, blank=True,null=True)
    rnt = models.CharField(max_length=20, blank=True,null=True)
    rut = models.CharField(max_length=20, blank=True,null=True)
    rnt_registrado_at = models.DateTimeField(null=True, blank=True)
    horario_atencion = models.CharField(max_length=100, blank=True,null=True)


    def __str__(self):
        return f'{self.nombre_agencia}'
    
class Proveedor(Usuario):
    nombre_empresa = models.CharField(max_length=50, null=False, blank=False)
    nit = models.CharField(max_length=20, blank=True,null=True)
    rut = models.CharField(max_length=20, blank=True,null=True)
    latitud = models.DecimalField(max_digits=10,decimal_places=8, blank=True, null=True)
    logitid = models.DecimalField(max_digits=10,decimal_places=8, blank=True, null=True)
    numero_telefonico = models.CharField(max_length=20, null=True, blank=True)
    foto_perfil = CloudinaryField('image', folder='amazonia_viva/perfiles', blank=True, null=True)
    foto_portada = CloudinaryField('image', folder='amazonia_viva/portadas', blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True,null=True)
    informacion_contacto = models.JSONField(default=dict, blank=True, null=True, help_text="Diccionario de redes sociales: {'instagram': 'url', 'facebook': 'url', 'whatsapp': 'numero'}")
    horario_atencion = models.CharField(max_length=100, blank=True,null=True)

    def __str__(self):
        return f'{self.nombre_empresa}'
    
class Turista(Usuario):
    fecha_nacimiento = models.DateField(blank=False, null=False)
    numero_identidad = models.CharField(max_length=15, blank=False, null=False)
    foto_perfil = CloudinaryField('image', folder='amazonia_viva/perfiles', blank=True, null=True)
    foto_portada = CloudinaryField('image', folder='amazonia_viva/portadas', blank=True, null=True)
    numero_telefonico = models.CharField(max_length=20, null=True, blank=True)

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

class CategoriaPaquete(models.Model):
    grupo = models.CharField(max_length=100, verbose_name="Grupo de Categoría")
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Subcategoría")

    class Meta:
        verbose_name = "Categoría de Paquete"
        verbose_name_plural = "Categorías de Paquetes"
        ordering = ['grupo', 'nombre']

    def __str__(self):
        return f"{self.grupo} — {self.nombre}"


class PaqueteTuristico(models.Model):
    TIPO_PAQUETE_CHOICES = [
        ('fijo', 'Fijo'),
        ('flexible', 'Flexible'),
    ]

    # --- Datos Básicos ---
    activo = models.BooleanField(default=True, verbose_name="Activo")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Tour")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (COP)")
    duracion = models.CharField(max_length=100, verbose_name="Duración")
    capacidad = models.PositiveIntegerField(verbose_name="Capacidad Máxima")

    # --- Fecha y Tipo ---
    fecha_realizacion = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha de Realización",
        help_text="Si se establece, el paquete es Fijo. Si está vacío, es Flexible."
    )
    tipo_paquete = models.CharField(
        max_length=10,
        choices=TIPO_PAQUETE_CHOICES,
        default='flexible',
        verbose_name="Tipo de Paquete"
    )
    
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

    # --- Categoría del paquete ---
    categoria_paquete = models.ForeignKey(
        'CategoriaPaquete',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paquetes',
        verbose_name="Categoría del Tour"
    )

    # --- LOS CAMPOS DINÁMICOS DE VUE ---
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
    
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Paquete Turístico"
        verbose_name_plural = "Paquetes Turísticos"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        # Auto-calcular tipo según si hay fecha
        if self.fecha_realizacion:
            self.tipo_paquete = 'fijo'
            # Si la fecha ya pasó, marcar como inactivo
            if self.fecha_realizacion < timezone.now().date():
                self.activo = False
        else:
            self.tipo_paquete = 'flexible'
        super().save(*args, **kwargs)

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
    TIPO_CATALOGO_CHOICES = [
        ('turistas', 'Turistas'),
        ('agencias', 'Agencias'),
    ]
    nombre = models.CharField(max_length=40,null=False,blank=False)
    sku = models.CharField(max_length=150, null=False, blank=False)
    caracteristicas = models.JSONField(default=dict, blank=True)
    stock = models.IntegerField(null=False, blank=False)
    precio = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    disponible = models.BooleanField(null=False, blank=False)
    categorias = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name='producto_categorias')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='producto_proveedor')
    tipo_catalogo = models.CharField(max_length=20, choices=TIPO_CATALOGO_CHOICES, default='turistas')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

class ProductoImagen(models.Model):
    imagen = CloudinaryField('image', folder='amazonia_viva/productos')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='imagen_producto')
    es_portada = models.BooleanField(default=False)
    
class Estados(models.Model):
    estado = models.CharField(max_length=40, null=False, blank=False)

class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrito_usuario')
    status = models.BooleanField(null=False)

class Items(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE,  related_name='item_carrito')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE,  related_name='item_productos', null=True, blank=True)
    paquetes = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE,  related_name='item_paquetes', null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    fecha_reserva = models.DateField(null=True, blank=True, verbose_name="Fecha de Reserva", help_text="Fecha elegida por el turista para realizar el paquete (solo aplica a paquetes).")

class Favoritos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='favorito_usuario')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE,  related_name='favorito_productos', null=True, blank=True)
    paquetes = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE,  related_name='favorito_paquetes', null=True, blank=True)

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='venta_usuario')
    fotograficas = models.JSONField(default=dict, null=True)
    novedades_turistas = models.JSONField(default=list, blank=True, null=True, help_text="Almacena el listado de viajeros y sus novedades registradas en el checkout en formato JSON.")
    estado = models.CharField(max_length=40, null=False, blank=False)

class Detalles_Venta(models.Model):
    ESTADO_PRODUCTO_CHOICES = [
        ('Pendiente de Empaque', 'Pendiente de Empaque'),
        ('Enviado', 'Enviado'),
        ('Cancelado', 'Cancelado'),
        ('Reembolsado', 'Reembolsado'),
        ('En Tránsito', 'En Tránsito'),
        ('Llegó', 'Llegó'),
        ('Entregado', 'Entregado'),
        ('Devuelto', 'Devuelto'),
    ]
    ESTADO_PAQUETE_CHOICES = [
        ('Confirmado', 'Confirmado'),
        ('Cancelado', 'Cancelado'),
        ('Rechazado', 'Rechazado'),
        ('Reembolso', 'Reembolso'),
    ]

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles_venta')
    producto = models.IntegerField(null=False, blank=False)
    paquete = models.IntegerField(null=False, blank=False)
    cantidad = models.IntegerField(null=False, blank=False)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    estado = models.CharField(max_length=40, default='Pendiente de Empaque', verbose_name="Estado del Item")


class ReservaFecha(models.Model):
    """Registra la fecha elegida por cada turista al reservar un paquete.
    Permite calcular cupos disponibles por fecha para paquetes flexibles y fijos."""
    paquete = models.ForeignKey(
        PaqueteTuristico,
        on_delete=models.CASCADE,
        related_name='reservas_fecha',
        verbose_name="Paquete Turístico"
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='reservas_fecha_venta',
        verbose_name="Venta"
    )
    fecha = models.DateField(verbose_name="Fecha de Realización")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad de Personas")

    class Meta:
        verbose_name = "Reserva por Fecha"
        verbose_name_plural = "Reservas por Fecha"

    def __str__(self):
        return f"{self.paquete.nombre} - {self.fecha} ({self.cantidad} personas)"

class ExperienciaEvidencia(models.Model):
    detalle_venta = models.ForeignKey(Detalles_Venta, on_delete=models.CASCADE, related_name='evidencias')
    imagen = CloudinaryField('image', folder='amazonia_viva/evidencias')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidencia de Experiencia"
        verbose_name_plural = "Evidencias de Experiencias"

class ExperienciaCalificacion(models.Model):
    detalle_venta = models.ForeignKey(Detalles_Venta, on_delete=models.CASCADE, related_name='calificacion')
    puntuacion = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Calificación de Experiencia"
        verbose_name_plural = "Calificaciones de Experiencias"
