import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from autenticacion.models import (
    Agencia, Productos, Venta, Detalles_Venta
)

class Command(BaseCommand):
    help = 'Seeds historical purchases made by Agencies to Providers.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando sembrado de compras de agencias..."))

        agencias = list(Agencia.objects.all())
        # Productos del catálogo para agencias
        productos_agencia = list(Productos.objects.filter(tipo_catalogo='agencias'))

        if not agencias:
            self.stdout.write(self.style.ERROR("No hay agencias en la base de datos."))
            return

        if not productos_agencia:
            self.stdout.write(self.style.ERROR("No hay productos en el catálogo de agencias."))
            return

        # Generar unas 40 compras históricas
        creadas = 0
        for i in range(40):
            agencia = random.choice(agencias)
            
            # Fecha aleatoria entre hace 180 días y hace 2 días (todo en pasado)
            dias_atras = random.randint(2, 180)
            fecha_pasada = timezone.now() - timedelta(days=dias_atras)
            
            # Crear la Venta
            venta = Venta.objects.create(
                usuario=agencia,
                total=Decimal('0.00'),
                estado='Completado',
                fotograficas={},
                novedades_turistas=[]
            )
            
            # Forzar la fecha en el pasado (bypass auto_now_add)
            Venta.objects.filter(pk=venta.pk).update(fecha=fecha_pasada)
            venta.refresh_from_db()

            total_venta = Decimal('0.00')
            num_items = random.randint(1, 4)
            used_prods = set()

            for _ in range(num_items):
                producto = random.choice(productos_agencia)
                if producto.id in used_prods: continue
                
                cantidad = random.randint(1, 3)
                precio_u = producto.precio
                subtotal = precio_u * cantidad
                
                Detalles_Venta.objects.create(
                    venta=venta,
                    paquete=0,
                    producto=producto.id,
                    cantidad=cantidad,
                    precio_unitario=precio_u,
                    estado='Entregado'
                )
                
                total_venta += subtotal
                used_prods.add(producto.id)

            # Actualizar total
            venta.total = total_venta
            venta.save()
            creadas += 1

        self.stdout.write(self.style.SUCCESS(f"Se han creado {creadas} compras históricas para agencias correctamente."))
