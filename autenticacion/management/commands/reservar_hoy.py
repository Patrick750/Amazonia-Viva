from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from autenticacion.models import (
    Detalles_Venta, PaqueteTuristico, ReservaFecha, Turista, Venta,
)
from autenticacion.serializers import calcular_cupos_disponibles

CORREOS = ['karolquesada76@gmail.com', 'ortizpatrick750@gmail.com']
PAQUETE = 'Caminata Ancestral Tikuna'
AGENCIA = 'amazoniaexpeditions@test.com'


class Command(BaseCommand):
    help = (
        'Registra una reserva para hoy de cada turista indicado en un paquete. '
        'Por defecto: Caminata Ancestral Tikuna de amazoniaexpeditions@test.com. '
        'Es idempotente: no duplica reservas vigentes del mismo turista.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--correos', nargs='+', default=CORREOS,
                            help='Correos de turistas existentes.')
        parser.add_argument('--paquete', default=PAQUETE, help='Nombre exacto del paquete.')
        parser.add_argument('--agencia', default=AGENCIA, help='Correo de la agencia propietaria.')
        parser.add_argument('--cantidad', type=int, default=1,
                            help='Personas por reserva (por defecto 1).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Valida y muestra lo que haría sin escribir.')

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        if cantidad < 1:
            raise CommandError('--cantidad debe ser al menos 1.')

        paquete = PaqueteTuristico.objects.filter(
            nombre=options['paquete'], agencia__email__iexact=options['agencia'],
        ).first()
        if not paquete:
            raise CommandError(f"No existe el paquete '{options['paquete']}' de {options['agencia']}.")

        hoy = timezone.localdate()
        if paquete.tipo_paquete == 'fijo' and paquete.fecha_realizacion != hoy:
            raise CommandError(
                f'El paquete es de fecha fija ({paquete.fecha_realizacion}); no puede reservarse para {hoy}.')

        correos = list(dict.fromkeys(c.strip().lower() for c in options['correos']))
        turistas = {t.email.lower(): t for t in Turista.objects.filter(email__in=correos)}
        faltantes = [c for c in correos if c not in turistas]
        if faltantes:
            raise CommandError(f"No existen turistas con estos correos: {', '.join(faltantes)}")

        with transaction.atomic():
            PaqueteTuristico.objects.select_for_update().get(pk=paquete.pk)
            for correo in correos:
                turista = turistas[correo]
                if self._ya_reservado(turista, paquete, hoy):
                    self.stdout.write(f'{correo}: ya tiene reserva vigente para {hoy}, se omite.')
                    continue
                cupos = calcular_cupos_disponibles(paquete, hoy)
                if cupos < cantidad:
                    raise CommandError(f'Cupos insuficientes para {correo}: quedan {cupos}.')
                if options['dry_run']:
                    self.stdout.write(f'{correo}: se crearía reserva de {cantidad} para {hoy}.')
                    continue
                self._crear_reserva(turista, paquete, hoy, cantidad)
                self.stdout.write(self.style.SUCCESS(f'{correo}: reserva creada para {hoy}.'))

    @staticmethod
    def _ya_reservado(turista, paquete, fecha):
        excluidas = Detalles_Venta.objects.filter(
            paquete=paquete.pk, estado__in=['Cancelado', 'Rechazado', 'Reembolso'],
        ).values_list('venta_id', flat=True)
        return ReservaFecha.objects.filter(
            paquete=paquete, fecha=fecha, venta__usuario=turista,
            venta__estado__in=['Completado', 'Pendiente'],
        ).exclude(venta_id__in=excluidas).exists()

    @staticmethod
    def _crear_reserva(turista, paquete, fecha, cantidad):
        subtotal = paquete.precio * cantidad
        tarifa = (subtotal * Decimal('0.01')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        venta = Venta.objects.create(
            usuario=turista, total=subtotal + tarifa, estado='Completado',
            estado_pago='Simulado', novedades_turistas=[],
        )
        Detalles_Venta.objects.create(
            venta=venta, producto=0, paquete=paquete.pk, cantidad=cantidad,
            precio_unitario=paquete.precio, estado='Confirmado',
        )
        ReservaFecha.objects.create(venta=venta, paquete=paquete, fecha=fecha, cantidad=cantidad)
