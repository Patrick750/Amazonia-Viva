from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.utils import timezone
import uuid

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
    es_turismo_aventura = models.BooleanField(
        default=False,
        verbose_name="Actividad de turismo de aventura"
    )
    norma_tecnica = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Norma técnica aplicable"
    )
    sistema_dificultad = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Sistema de clasificación técnica"
    )
    opciones_dificultad = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Opciones de dificultad",
        help_text="Opciones propias de la actividad; no se comparan entre normas distintas."
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


class EstandarPaquete(models.Model):
    clave = models.SlugField(max_length=40, unique=True)
    version = models.CharField(max_length=20)
    nombre = models.CharField(max_length=180)
    proposito = models.TextField()
    activo = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estándar de paquetes"
        verbose_name_plural = "Estándares de paquetes"
        ordering = ['clave']

    def __str__(self):
        return f"{self.nombre} ({self.version})"


class ModalidadTurismo(models.Model):
    estandar = models.ForeignKey(
        EstandarPaquete,
        on_delete=models.CASCADE,
        related_name='modalidades',
    )
    codigo = models.SlugField(max_length=40)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Modalidad de turismo"
        verbose_name_plural = "Modalidades de turismo"
        ordering = ['orden', 'nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['estandar', 'codigo'],
                name='modalidad_codigo_unico_por_estandar',
            ),
        ]

    def __str__(self):
        return self.nombre


class PrincipioEstandarPaquete(models.Model):
    estandar = models.ForeignKey(
        EstandarPaquete,
        on_delete=models.CASCADE,
        related_name='principios',
    )
    codigo = models.SlugField(max_length=50)
    descripcion = models.TextField()
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Principio del estándar"
        verbose_name_plural = "Principios del estándar"
        ordering = ['orden', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['estandar', 'codigo'],
                name='principio_codigo_unico_por_estandar',
            ),
        ]

    def __str__(self):
        return self.descripcion


class FuenteEstandarPaquete(models.Model):
    estandar = models.ForeignKey(
        EstandarPaquete,
        on_delete=models.CASCADE,
        related_name='fuentes',
    )
    codigo = models.SlugField(max_length=60)
    titulo = models.CharField(max_length=180)
    entidad = models.CharField(max_length=180)
    alcance = models.TextField()
    url = models.URLField(blank=True, max_length=500)
    verificada = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fuente del estándar"
        verbose_name_plural = "Fuentes del estándar"
        ordering = ['orden', 'titulo']
        constraints = [
            models.UniqueConstraint(
                fields=['estandar', 'codigo'],
                name='fuente_codigo_unico_por_estandar',
            ),
        ]

    def __str__(self):
        return self.titulo


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

    # --- Ficha técnica y de seguridad MEJ-003 ---
    modalidades_turismo = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Modalidades de turismo"
    )
    clasificacion_actividades = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Clasificación técnica por actividad",
        help_text="Cada elemento identifica la actividad, su sistema y el nivel o descripción aplicable."
    )
    requisitos_participantes = models.TextField(
        blank=True,
        verbose_name="Requisitos y restricciones para participantes"
    )
    condiciones_operacion = models.TextField(
        blank=True,
        verbose_name="Condiciones de operación"
    )
    medidas_seguridad = models.TextField(
        blank=True,
        verbose_name="Medidas de seguridad y respuesta"
    )
    informacion_sostenibilidad = models.TextField(
        blank=True,
        verbose_name="Información de sostenibilidad"
    )
    certificacion_aventura = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Soporte de certificación para turismo de aventura"
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
    referencia_pago = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    ambiente_pago = models.CharField(max_length=4, blank=True)
    clave_operacion = models.UUIDField(null=True, blank=True)
    huella_operacion = models.CharField(max_length=64, blank=True)
    estado_pago = models.CharField(max_length=20, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Pagado', 'Pagado'), ('Simulado', 'Simulado'), ('Fallido', 'Fallido'), ('Reembolsado', 'Reembolsado'), ('Revision', 'Revision')])
    moneda = models.CharField(max_length=3, default='COP')
    vence_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['usuario', 'clave_operacion'], name='venta_operacion_unica')]

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

class SolicitudRetiro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='retiros')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(max_length=50)
    banco = models.CharField(max_length=100, blank=True, null=True)
    cuenta = models.CharField(max_length=100, blank=True, null=True)
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    titular = models.CharField(max_length=150, blank=True, null=True)
    numero_documento = models.CharField(max_length=50, blank=True, null=True)
    referencia = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=50, default='Pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Retiro"
        verbose_name_plural = "Solicitudes de Retiro"


class IntentosCredenciales(models.Model):
    clave = models.CharField(max_length=64, unique=True)
    inicio = models.DateTimeField(default=timezone.now)
    intentos = models.PositiveIntegerField(default=0)


class CambioEstadoRetiro(models.Model):
    solicitud = models.ForeignKey(SolicitudRetiro, on_delete=models.PROTECT, related_name='cambios')
    anterior = models.CharField(max_length=50)
    nuevo = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True)


class EventoPago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name='eventos_pago')
    checksum = models.CharField(max_length=64, unique=True)
    transaccion = models.CharField(max_length=100)
    ambiente = models.CharField(max_length=4)
    estado = models.CharField(max_length=20)
    importe_centavos = models.BigIntegerField()
    moneda = models.CharField(max_length=3)
    resultado = models.CharField(max_length=30)
    recibido_en = models.DateTimeField(auto_now_add=True)


class Recorrido(models.Model):
    """Trazado GPS grabado por una agencia y asociado a un paquete turístico.

    ``id_cliente`` lo genera el dispositivo para que un recorrido registrado sin conexión
    pueda reenviarse sin duplicarse. Solo un recorrido por paquete puede estar publicado.
    """
    id_cliente = models.UUIDField(unique=True, editable=False)
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE, related_name='recorridos')
    nombre = models.CharField(max_length=120, blank=True)
    iniciado_en = models.DateTimeField()
    finalizado_en = models.DateTimeField(null=True, blank=True)
    publicado = models.BooleanField(default=False)
    publicado_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-iniciado_en']
        constraints = [
            models.UniqueConstraint(
                fields=['paquete'],
                condition=models.Q(publicado=True),
                name='recorrido_publicado_unico_por_paquete',
            ),
        ]

    def __str__(self):
        return f"Recorrido {self.id_cliente} de {self.paquete_id}"


class PuntoRecorrido(models.Model):
    """Punto GPS de un recorrido. ``secuencia`` la asigna el dispositivo y evita duplicados al reintentar."""
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, related_name='puntos')
    secuencia = models.PositiveIntegerField()
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    precision_m = models.FloatField(null=True, blank=True)
    capturado_en = models.DateTimeField()

    class Meta:
        ordering = ['secuencia']
        constraints = [
            models.UniqueConstraint(fields=['recorrido', 'secuencia'], name='punto_recorrido_secuencia_unica'),
        ]
