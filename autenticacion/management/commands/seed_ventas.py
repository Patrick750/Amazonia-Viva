import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from autenticacion.models import (
    Usuario, Turista, PaqueteTuristico, Productos, Venta, Detalles_Venta, 
    ReservaFecha, ExperienciaCalificacion
)

class Command(BaseCommand):
    help = 'Seeds the Venta and Detalles_Venta tables with realistic data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando sembrado de ventas y detalles..."))

        turistas = list(Turista.objects.all())
        paquetes = list(PaqueteTuristico.objects.all())
        productos = list(Productos.objects.all())

        if not turistas:
            self.stdout.write(self.style.ERROR("No hay turistas en la base de datos."))
            return

        if not paquetes and not productos:
            self.stdout.write(self.style.ERROR("No hay paquetes ni productos para vender."))
            return

        # Generar unas 50 ventas aleatorias
        for i in range(50):
            turista_user = random.choice(turistas)
            
            # Crear una Venta
            venta = Venta.objects.create(
                usuario=turista_user,
                total=Decimal('0.00'), # Se actualizará luego
                estado='Completado',
                fotograficas={},
                novedades_turistas=[]
            )

            total_venta = Decimal('0.00')
            
            # Agregar entre 1 y 3 items a la venta
            num_items = random.randint(1, 3)
            used_items = set()

            for _ in range(num_items):
                item_type = random.choice(['paquete', 'producto'])
                
                if item_type == 'paquete' and paquetes:
                    paquete = random.choice(paquetes)
                    if f"paq_{paquete.id}" in used_items: continue
                    
                    cantidad = random.randint(1, 4)
                    precio_u = paquete.precio
                    subtotal = precio_u * cantidad
                    
                    detalle = Detalles_Venta.objects.create(
                        venta=venta,
                        paquete=paquete.id,
                        producto=0,
                        cantidad=cantidad,
                        precio_unitario=precio_u,
                        estado=random.choice(['Confirmado', 'Confirmado', 'Confirmado', 'Cancelado']) # Mayoría confirmados
                    )
                    
                    # Si está confirmado, crear ReservaFecha
                    if detalle.estado == 'Confirmado':
                        ReservaFecha.objects.create(
                            paquete=paquete,
                            venta=venta,
                            fecha=paquete.fecha_realizacion or (timezone.now().date() + timedelta(days=random.randint(5, 30))),
                            cantidad=cantidad
                        )
                    
                    total_venta += subtotal
                    used_items.add(f"paq_{paquete.id}")

                    # Agregar una calificación aleatoria (80% de probabilidad)
                    if random.random() > 0.2 and detalle.estado == 'Confirmado':
                        ExperienciaCalificacion.objects.create(
                            detalle_venta=detalle,
                            puntuacion=random.randint(4, 5),
                            comentario=random.choice(["¡Increíble experiencia!", "Muy buena atención", "Recomendado", "Paisajes hermosos"])
                        )

                elif item_type == 'producto' and productos:
                    producto = random.choice(productos)
                    if f"prod_{producto.id}" in used_items: continue
                    
                    cantidad = random.randint(1, 5)
                    precio_u = producto.precio
                    subtotal = precio_u * cantidad
                    
                    Detalles_Venta.objects.create(
                        venta=venta,
                        paquete=0,
                        producto=producto.id,
                        cantidad=cantidad,
                        precio_unitario=precio_u,
                        estado=random.choice(['Entregado', 'Enviado', 'Pendiente de Empaque'])
                    )
                    
                    total_venta += subtotal
                    used_items.add(f"prod_{producto.id}")

            # Actualizar total de la venta
            venta.total = total_venta
            venta.save()

        self.stdout.write(self.style.SUCCESS(f"Sembrado de 50 ventas completado con éxito."))
