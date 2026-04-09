from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum


def calcular_cupos_disponibles(paquete, fecha=None):
    """Calcula cupos disponibles para un paquete en una fecha dada.
    Si el paquete es fijo, usa su propia fecha. Si es flexible, requiere una fecha."""
    if not fecha and paquete.tipo_paquete == 'fijo':
        fecha = paquete.fecha_realizacion
    if not fecha:
        return paquete.capacidad  # flexible sin fecha consultada = capacidad completa
    reservas = ReservaFecha.objects.filter(paquete=paquete, fecha=fecha).aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    return max(0, paquete.capacidad - reservas)

class CategoriaPaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPaquete
        fields = '__all__'

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
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
            'categoria_paquete', 'fecha_realizacion', 'tipo_paquete'
        ]
        read_only_fields = ['tipo_paquete']

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
    reservas_totales = serializers.SerializerMethodField()
    cupos_disponibles = serializers.SerializerMethodField()

    def get_reservas_totales(self, obj):
        resultado = Detalles_Venta.objects.filter(paquete=obj.id).aggregate(total=Sum('cantidad'))
        return resultado['total'] or 0

    def get_cupos_disponibles(self, obj):
        return calcular_cupos_disponibles(obj)

    class Meta:
        model = PaqueteTuristico
        fields = [
            'id', 'activo', 'nombre', 'descripcion', 'precio', 
            'duracion', 'capacidad', 'ubicacion', 'itinerario', 
            'incluido', 'rating', 'agencia', 'actividades',
            'categoria_paquete', 'imagen_paquete', 'reservas_totales',
            'fecha_realizacion', 'tipo_paquete', 'cupos_disponibles'
        ]


class SerializerCatalogoTour(serializers.ModelSerializer):
    imagen_portada = serializers.SerializerMethodField()
    nombre_agencia = serializers.CharField(source='agencia.nombre_agencia', read_only=True)
    agencia_id = serializers.ReadOnlyField(source='agencia.id')
    ciudad = serializers.CharField(source='ubicacion', read_only=True)
    nivel_riesgo = serializers.SerializerMethodField()
    num_calificaciones = serializers.SerializerMethodField()
    reservas_totales = serializers.SerializerMethodField()

    categoria_paquete_nombre = serializers.CharField(source='categoria_paquete.nombre', read_only=True)

    def get_reservas_totales(self, obj):
        resultado = Detalles_Venta.objects.filter(paquete=obj.id).aggregate(total=Sum('cantidad'))
        return resultado['total'] or 0

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

    proveedor_validado = serializers.SerializerMethodField()
    cupos_disponibles = serializers.SerializerMethodField()

    def get_proveedor_validado(self, obj):
        return bool(obj.agencia.nit or obj.agencia.rut or obj.agencia.rnt)

    def get_cupos_disponibles(self, obj):
        return calcular_cupos_disponibles(obj)

    class Meta:
        model = PaqueteTuristico
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'duracion',
            'ubicacion', 'ciudad', 'rating', 'num_calificaciones',
            'imagen_portada', 'nombre_agencia', 'agencia_id', 'nivel_riesgo', 'activo',
            'categoria_paquete_nombre', 'categoria_paquete', 'proveedor_validado', 'reservas_totales',
            'fecha_realizacion', 'tipo_paquete', 'cupos_disponibles'
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
    proveedor_id = serializers.ReadOnlyField(source='proveedor.id')
    nombre_categoria = serializers.CharField(source='categorias.nombre', read_only=True)
    num_calificaciones = serializers.SerializerMethodField()
    descripcion_corta = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    modelo = serializers.SerializerMethodField()
    ventas_totales = serializers.SerializerMethodField()

    def get_ventas_totales(self, obj):
        resultado = Detalles_Venta.objects.filter(producto=obj.id).aggregate(total=Sum('cantidad'))
        return resultado['total'] or 0

    def get_imagen_portada(self, obj):
        portada = obj.imagen_producto.filter(es_portada=True).first()
        if not portada:
            portada = obj.imagen_producto.first()
        if portada and portada.imagen:
            return portada.imagen.url
        return None

    proveedor_validado = serializers.SerializerMethodField()
    def get_proveedor_validado(self, obj):
        return bool(obj.proveedor.nit or obj.proveedor.rut)

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

    def get_marca(self, obj):
        if isinstance(obj.caracteristicas, list):
            for item in obj.caracteristicas:
                if item.get('clave') == 'Marca':
                    return item.get('valor', '')
        return ''

    def get_modelo(self, obj):
        if isinstance(obj.caracteristicas, list):
            for item in obj.caracteristicas:
                if item.get('clave') == 'Modelo':
                    return item.get('valor', '')
        return ''

    class Meta:
        model = Productos
        fields = [
            'id', 'nombre', 'descripcion_corta', 'precio', 'stock',
            'disponible', 'tipo_catalogo', 'nombre_categoria',
            'imagen_portada', 'nombre_proveedor', 'proveedor_id', 'rating', 'num_calificaciones',
            'marca', 'modelo', 'proveedor_validado', 'ventas_totales'
        ]

class SerializerDetalleProducto(serializers.ModelSerializer):
    imagen_producto = SerializerCatalogoProductoImagen(many=True, read_only=True)
    nombre_proveedor = serializers.CharField(source='proveedor.nombre_empresa', read_only=True)
    proveedor_id = serializers.ReadOnlyField(source='proveedor.id')
    nombre_categoria = serializers.CharField(source='categorias.nombre', read_only=True)
    num_calificaciones = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    ventas_totales = serializers.SerializerMethodField()

    def get_ventas_totales(self, obj):
        resultado = Detalles_Venta.objects.filter(producto=obj.id).aggregate(total=Sum('cantidad'))
        return resultado['total'] or 0

    def get_num_calificaciones(self, obj):
        return 0

    def get_rating(self, obj):
        return 0

    class Meta:
        model = Productos
        fields = [
            'id', 'nombre', 'sku', 'caracteristicas', 'precio', 'stock',
            'disponible', 'tipo_catalogo', 'nombre_categoria',
            'imagen_producto', 'nombre_proveedor', 'proveedor_id', 'rating', 'num_calificaciones', 'ventas_totales'
        ]

class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favoritos
        fields = ['id', 'usuario', 'producto', 'paquetes']
        extra_kwargs = {
            'usuario': {'read_only': True},
            'producto': {'required': False, 'allow_null': True},
            'paquetes': {'required': False, 'allow_null': True}
        }


class FavoritoDetailSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    item_id = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    descripcion = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    imagen_portada = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    subtitulo = serializers.SerializerMethodField()

    def get_tipo(self, obj):
        return 'producto' if obj.producto_id else 'paquete'

    def get_item_id(self, obj):
        if obj.producto_id:
            return obj.producto_id
        return obj.paquetes_id

    def get_nombre(self, obj):
        try:
            if obj.producto:
                return obj.producto.nombre
            if obj.paquetes:
                return obj.paquetes.nombre
        except Exception:
            pass
        return ''

    def get_descripcion(self, obj):
        try:
            if obj.producto:
                # Productos no tiene campo 'descripcion', usa caracteristicas
                caract = obj.producto.caracteristicas or {}
                if isinstance(caract, dict):
                    return ', '.join(f"{k}: {v}" for k, v in list(caract.items())[:2])
                
                if isinstance(caract, list):
                    # Formato esperado: [{"clave": "Marca", "valor": "Nike"}, ...]
                    partes = []
                    for c in caract[:2]:
                        if isinstance(c, dict) and 'clave' in c and 'valor' in c:
                            partes.append(f"{c['clave']}: {c['valor']}")
                    return ', '.join(partes)

                return str(caract)[:120]
            if obj.paquetes:
                texto = obj.paquetes.descripcion or ''
                # Eliminamos etiquetas HTML si existen para evitar mostrar código en la tarjeta
                import re
                texto_plano = re.sub(r'<[^>]+>', '', texto)
                return texto_plano[:120] + ('...' if len(texto_plano) > 120 else '')
        except Exception:
            pass
        return ''

    def get_precio(self, obj):
        try:
            if obj.producto:
                return str(obj.producto.precio)
            if obj.paquetes:
                return str(obj.paquetes.precio)
        except Exception:
            pass
        return '0'

    def get_imagen_portada(self, obj):
        try:
            if obj.producto:
                img = obj.producto.imagen_producto.filter(es_portada=True).first()
                if not img:
                    img = obj.producto.imagen_producto.first()
                return img.imagen.url if img and img.imagen else None
            if obj.paquetes:
                img = obj.paquetes.imagen_paquete.filter(es_portada=True).first()
                if not img:
                    img = obj.paquetes.imagen_paquete.first()
                return img.imagen.url if img and img.imagen else None
        except Exception:
            pass
        return None

    def get_badge(self, obj):
        try:
            if obj.producto:
                return obj.producto.get_tipo_catalogo_display() or 'Producto'
            if obj.paquetes and obj.paquetes.categoria_paquete:
                return obj.paquetes.categoria_paquete.nombre
        except Exception:
            pass
        return 'Paquete'

    def get_subtitulo(self, obj):
        try:
            if obj.producto and obj.producto.categorias:
                return obj.producto.categorias.nombre
            if obj.paquetes:
                duracion = obj.paquetes.duracion or ''
                ubicacion = obj.paquetes.ubicacion or ''
                return f"{duracion} · {ubicacion}".strip(' ·')
        except Exception:
            pass
        return ''

    class Meta:
        model = Favoritos
        fields = [
            'id', 'tipo', 'item_id', 'nombre', 'descripcion',
            'precio', 'imagen_portada', 'badge', 'subtitulo'
        ]


class CarritoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ['id', 'carrito', 'producto', 'paquetes', 'precio', 'fecha_reserva']
        extra_kwargs = {
            'carrito': {'read_only': True},
            'producto': {'required': False, 'allow_null': True},
            'paquetes': {'required': False, 'allow_null': True},
            'fecha_reserva': {'required': False, 'allow_null': True},
        }

class CarritoItemDetailSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    item_id = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    imagen = serializers.SerializerMethodField()
    subtitulo = serializers.SerializerMethodField()

    def get_tipo(self, obj):
        return 'paquete' if obj.paquetes_id else 'producto'

    def get_item_id(self, obj):
        return obj.paquetes_id if obj.paquetes_id else obj.producto_id

    def get_nombre(self, obj):
        if obj.paquetes: return obj.paquetes.nombre
        if obj.producto: return obj.producto.nombre
        return ''

    def get_precio(self, obj):
        return str(obj.precio)

    def get_imagen(self, obj):
        try:
            if obj.paquetes:
                img = obj.paquetes.imagen_paquete.filter(es_portada=True).first() or obj.paquetes.imagen_paquete.first()
                return img.imagen.url if img and img.imagen else None
            if obj.producto:
                img = obj.producto.imagen_producto.filter(es_portada=True).first() or obj.producto.imagen_producto.first()
                return img.imagen.url if img and img.imagen else None
        except: pass
        return None

    def get_subtitulo(self, obj):
        if obj.paquetes: return obj.paquetes.ubicacion
        if obj.producto: return obj.producto.categorias.nombre if obj.producto.categorias else ''
        return ''

    class Meta:
        model = Items
        fields = ['id', 'tipo', 'item_id', 'nombre', 'precio', 'imagen', 'subtitulo', 'fecha_reserva']


class SerializerDetalleTour(serializers.ModelSerializer):
    imagen_paquete = SerializersImages(many=True, read_only=True)
    nombre_agencia = serializers.CharField(source='agencia.nombre_agencia', read_only=True)
    categoria_paquete_nombre = serializers.CharField(source='categoria_paquete.nombre', read_only=True)
    actividades_detalle = SerializersActividades(source='actividades', many=True, read_only=True)
    reservas_totales = serializers.SerializerMethodField()
    cupos_disponibles = serializers.SerializerMethodField()

    def get_reservas_totales(self, obj):
        resultado = Detalles_Venta.objects.filter(paquete=obj.id).aggregate(total=Sum('cantidad'))
        return resultado['total'] or 0

    def get_cupos_disponibles(self, obj):
        return calcular_cupos_disponibles(obj)

    class Meta:
        model = PaqueteTuristico
        fields = [
            'id', 'activo', 'nombre', 'descripcion', 'precio', 'duracion', 
            'ubicacion', 'latitud', 'longitud', 'capacidad', 
            'itinerario', 'incluido', 'rating',
            'imagen_paquete', 'nombre_agencia', 'categoria_paquete_nombre',
            'actividades_detalle', 'reservas_totales',
            'fecha_realizacion', 'tipo_paquete', 'cupos_disponibles'
        ]


# ─── Serializers de Perfil de Usuario ─────────────────────────────────────────

class AgenciaPerfilSerializer(serializers.ModelSerializer):
    """
    Lectura y actualización parcial del perfil de una Agencia.
    - nit, rnt, rut → read_only (bloqueados).
    - foto_url      → URL pública del logotipo en Cloudinary.
    - logotipo      → excluido de edición directa (se actualiza vía /perfil/foto/).
    """
    foto_url = serializers.SerializerMethodField()

    def get_foto_url(self, obj):
        if obj.logotipo:
            return obj.logotipo.url
        return None

    foto_portada_url = serializers.SerializerMethodField()

    def get_foto_portada_url(self, obj):
        if obj.foto_portada:
            return obj.foto_portada.url
        return None

    def validate(self, attrs):
        instance = self.instance
        if instance:
            # --- Regla: NIT y RUT son inmutables después de ser registrados ---
            for field in ['nit', 'rut']:
                if field in attrs:
                    current_val = getattr(instance, field)
                    if current_val and current_val != attrs[field]:
                        raise serializers.ValidationError({
                            field: f"El {field.upper()} ya está registrado y no puede modificarse."
                        })
            
            # --- Regla para RNT: Inmutable durante 300 segundos (5 min) ---
            if 'rnt' in attrs:
                current_rnt = getattr(instance, 'rnt')
                nueva_rnt = attrs['rnt']
                
                if current_rnt and current_rnt != nueva_rnt:
                    # Si ya tiene RNT y está intentando cambiarlo
                    ahora = timezone.now()
                    referencia = instance.rnt_registrado_at or instance.date_joined
                    limite_edicion = referencia + timedelta(days=30)
                    
                    if ahora <= limite_edicion:
                        delta = limite_edicion - ahora
                        dias = delta.days
                        horas = delta.seconds // 3600
                        raise serializers.ValidationError({
                            "rnt": f"El RNT ya está verificado. Faltan {dias} días y {horas} horas para la próxima renovación obligatoria."
                        })
                    else:
                        # Si ya pasó el tiempo, permitimos el cambio y actualizamos la fecha de registro
                        attrs['rnt_registrado_at'] = ahora
                elif not current_rnt and nueva_rnt:
                    # Es la primera vez que registra el RNT
                    attrs['rnt_registrado_at'] = timezone.now()
        return attrs

    class Meta:
        model = Agencia
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_agencia', 'numero_telefonico', 'descripcion',
            'informacion_contacto', 'horario_atencion',
            'nit', 'rnt', 'rut', 'rnt_registrado_at',
            'foto_url', 'foto_portada_url', 'date_joined',
        ]
        read_only_fields = ['id', 'email', 'username', 'foto_url', 'foto_portada_url']


class ProveedorPerfilSerializer(serializers.ModelSerializer):
    """
    Lectura y actualización parcial del perfil de un Proveedor.
    - nit, rut  → read_only (bloqueados).
    - foto_url  → URL pública de la foto de perfil en Cloudinary.
    """
    foto_url = serializers.SerializerMethodField()

    def get_foto_url(self, obj):
        if obj.foto_perfil:
            return obj.foto_perfil.url
        return None

    foto_portada_url = serializers.SerializerMethodField()

    def get_foto_portada_url(self, obj):
        if obj.foto_portada:
            return obj.foto_portada.url
        return None

    def validate(self, attrs):
        instance = self.instance
        if instance:
            # NIT y RUT inmutables después de ser registrados
            for field in ['nit', 'rut']:
                if field in attrs:
                    current_val = getattr(instance, field)
                    if current_val and current_val != attrs[field]:
                        raise serializers.ValidationError({
                            field: f"El {field.upper()} ya está registrado y es inmutable para este perfil."
                        })
        return attrs

    class Meta:
        model = Proveedor
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_empresa', 'numero_telefonico', 'descripcion',
            'informacion_contacto', 'horario_atencion',
            'nit', 'rut',
            'foto_url', 'foto_portada_url'
        ]
        read_only_fields = ['id', 'email', 'username', 'foto_url', 'foto_portada_url']


class TuristaPerfilSerializer(serializers.ModelSerializer):
    """
    Lectura y actualización parcial del perfil de un Turista.
    - numero_identidad → read_only (dato legal inmutable).
    - foto_url         → URL pública de la foto de perfil en Cloudinary.
    """
    foto_url = serializers.SerializerMethodField()

    def get_foto_url(self, obj):
        if obj.foto_perfil:
            return obj.foto_perfil.url
        return None

    def validate(self, attrs):
        instance = self.instance
        if instance:
            field = 'numero_identidad'
            if field in attrs:
                current_val = getattr(instance, field)
                if current_val and current_val != attrs[field]:
                    raise serializers.ValidationError({
                        field: "El número de identidad ya está registrado y no puede modificarse."
                    })
        return attrs

    class Meta:
        model = Turista
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'fecha_nacimiento', 'numero_identidad',
            'foto_url',
        ]
        read_only_fields = ['id', 'email', 'username', 'foto_url']
