from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase, override_settings, skipUnlessDBFeature
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (Agencia, Proveedor, Turista, Usuario, Categorias, PaqueteTuristico,
                     Productos, Venta, Detalles_Venta, ReservaFecha, Carrito, Items, SolicitudRetiro,
                     IntentosCredenciales, CambioEstadoRetiro)
from .compras import procesar_compra, liberar_pedido
from .retiros import cambiar_estado
from .vistas_liquidacion import _calcular_saldos


def fixtures():
    agencia = Agencia.objects.create_user(username='agencia', email='agencia@example.test', password='A-safe-pass-938!', nombre_agencia='Agencia')
    proveedor = Proveedor.objects.create_user(username='proveedor', email='proveedor@example.test', password='A-safe-pass-938!', nombre_empresa='Proveedor')
    turista = Turista.objects.create_user(username='turista', email='turista@example.test', password='A-safe-pass-938!', fecha_nacimiento='1990-01-01', numero_identidad='123456')
    otro = Turista.objects.create_user(username='otro', email='otro@example.test', password='A-safe-pass-938!', fecha_nacimiento='1990-01-01', numero_identidad='654321')
    categoria = Categorias.objects.create(nombre='Accesorios')
    producto = Productos.objects.create(nombre='Botas', sku='BO-1', precio='100.25', stock=3, disponible=True, categorias=categoria, proveedor=proveedor)
    paquete = PaqueteTuristico.objects.create(nombre='Selva', descripcion='Tour', precio='200.50', duracion='2 días', capacidad=3, ubicacion='Leticia', agencia=agencia, tipo_paquete='flexible')
    return agencia, proveedor, turista, otro, producto, paquete


def payload(producto, **kwargs):
    data = {'clave_operacion': str(uuid4()), 'total': 1, 'items': [{'tipo': 'producto', 'id': producto.pk, 'cantidad': 1, 'precio': 1}]}
    data.update(kwargs)
    return data


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False, CHECKOUT_MODE='pending', ALLOW_WITHDRAWALS=True,
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SecurityTests(TestCase):
    def setUp(self):
        self.agencia, self.proveedor, self.turista, self.otro, self.producto, self.paquete = fixtures()
        self.client = APIClient()
        self.client.force_authenticate(self.turista)

    def post_compra(self, data=None):
        return self.client.post('/api/venta/procesar/', data or payload(self.producto), format='json')

    def paid_detail(self):
        venta = Venta.objects.create(usuario=self.turista, total='100.25', estado='Completado', estado_pago='Pagado')
        return Detalles_Venta.objects.create(venta=venta, producto=self.producto.pk, paquete=0, cantidad=1, precio_unitario='100.25', estado='Entregado')

    def retiro_payload(self, monto='50.00'):
        return {'monto': monto, 'metodo': 'nequi', 'datos_bancarios': {'cuenta': '3001234567', 'titular': 'Persona', 'numero': '123'}}

    def test_anonymous_cannot_mutate_or_access_private_api(self):
        self.client.force_authenticate(None)
        for method, path in [('put', f'/api/updatepack/{self.paquete.pk}/'), ('delete', f'/api/deletepack/{self.paquete.pk}/'), ('get', '/api/carrito/')]:
            with self.subTest(path=path):
                self.assertEqual(getattr(self.client, method)(path, {}, format='json').status_code, 401)

    def test_wrong_role_forbidden(self):
        for path, method in [(f'/api/updatepack/{self.paquete.pk}/', 'put'), (f'/api/productos/{self.producto.pk}/', 'delete'), ('/api/liquidacion/saldos/', 'get'), ('/api/experiencias/dashboard/', 'get'), ('/api/proveedor/gestion-logistica/exportar/', 'get')]:
            with self.subTest(path=path):
                self.assertEqual(getattr(self.client, method)(path, {}, format='json').status_code, 403)

    def test_other_agency_cannot_manage_package(self):
        agencia = Agencia.objects.create_user(username='otra-agencia', email='otra-agencia@example.test', nombre_agencia='Otra')
        self.client.force_authenticate(agencia)
        self.assertEqual(self.client.put(f'/api/updatepack/{self.paquete.pk}/', {'nombre': 'Robado'}, format='json').status_code, 404)
        self.assertEqual(self.client.delete(f'/api/deletepack/{self.paquete.pk}/').status_code, 404)
        self.paquete.refresh_from_db()
        self.assertEqual(self.paquete.nombre, 'Selva')

    def test_owner_cannot_transfer_package(self):
        self.client.force_authenticate(self.agencia)
        response = self.client.put(f'/api/updatepack/{self.paquete.pk}/', {'agencia': self.otro.pk, 'nombre': 'Propio'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.paquete.refresh_from_db()
        self.assertEqual(self.paquete.agencia_id, self.agencia.pk)

    def test_provider_creates_product_and_cannot_transfer_it(self):
        self.client.force_authenticate(self.proveedor)
        data = {'nombre': 'Sombrero', 'sku': 'SO-1', 'stock': 5, 'precio': '20.10', 'disponible': True,
                'categorias': self.producto.categorias_id, 'proveedor': self.otro.pk}
        response = self.client.post('/api/productos/', data, format='json')
        self.assertEqual(response.status_code, 201)
        creado = Productos.objects.get(nombre='Sombrero')
        self.assertEqual(creado.proveedor_id, self.proveedor.pk)
        response = self.client.put(f'/api/productos/{creado.pk}/', {'proveedor': self.otro.pk, 'precio': '30.10'}, format='json')
        self.assertEqual(response.status_code, 200)
        creado.refresh_from_db()
        self.assertEqual(creado.proveedor_id, self.proveedor.pk)

    def test_other_provider_cannot_mutate_product(self):
        otro = Proveedor.objects.create_user(username='otro-proveedor', email='otro-proveedor@example.test', nombre_empresa='Otro')
        self.client.force_authenticate(otro)
        self.assertEqual(self.client.delete(f'/api/productos/{self.producto.pk}/').status_code, 404)
        self.assertEqual(self.client.put(f'/api/productos/{self.producto.pk}/', {'stock': 99}, format='json').status_code, 404)

    def test_soft_delete_preserves_history(self):
        self.paid_detail()
        self.client.force_authenticate(self.proveedor)
        self.assertEqual(self.client.delete(f'/api/productos/{self.producto.pk}/').status_code, 204)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.disponible)
        self.assertEqual(Detalles_Venta.objects.count(), 1)

    def test_public_catalogs_available(self):
        self.client.force_authenticate(None)
        for path in ['/api/catalogo/tours/', '/api/catalogo/productos/', '/api/categorias-paquetes/', '/api/categorias-productos/', '/api/actividades/', f'/api/catalogo/tours/{self.paquete.pk}/', f'/api/catalogo/productos/{self.producto.pk}/']:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_password_validation_and_hidden_password(self):
        self.client.force_authenticate(None)
        data = {'username': 'newperson', 'email': 'newperson@example.test', 'password': '123', 'fecha_nacimiento': '1991-01-01', 'numero_identidad': '777'}
        response = self.client.post('/api/signup/turista/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        data['password'] = 'A-new-strong-pass-968!'
        self.assertEqual(self.client.post('/api/signup/turista/', data, format='json').status_code, 201)
        from .serializers import TuristaSerializers
        self.assertNotIn('password', TuristaSerializers(Turista.objects.get(email=data['email'])).data)

    def test_credentials_throttled(self):
        for _ in range(5):
            self.assertEqual(self.client.post('/api/confirmar-password/', {'password': 'wrong'}, format='json').status_code, 401)
        self.assertEqual(self.client.post('/api/confirmar-password/', {'password': 'wrong'}, format='json').status_code, 429)

    def test_login_throttled(self):
        self.client.force_authenticate(None)
        for _ in range(5):
            self.assertEqual(self.client.post('/api/login/', {'email': self.turista.email, 'password': 'wrong'}, format='json').status_code, 401)
        self.assertEqual(self.client.post('/api/login/', {'email': self.turista.email, 'password': 'wrong'}, format='json').status_code, 429)

    def test_logout_rejects_foreign_refresh(self):
        token = RefreshToken.for_user(self.otro)
        self.assertEqual(self.client.post('/api/logout/', {'refresh_token': str(token)}, format='json').status_code, 403)

    def test_refresh_rotation_and_logout(self):
        token = RefreshToken.for_user(self.turista)
        self.client.force_authenticate(None)
        response = self.client.post('/api/token/refresh/', {'refresh': str(token)}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh', response.data)
        self.assertEqual(self.client.post('/api/token/refresh/', {'refresh': str(token)}, format='json').status_code, 401)
        self.client.force_authenticate(self.turista)
        self.assertEqual(self.client.post('/api/logout/', {'refresh_token': response.data['refresh']}, format='json').status_code, 205)

    def test_server_price_and_pending_payment(self):
        response = self.post_compra()
        self.assertEqual(response.status_code, 201)
        venta = Venta.objects.get()
        self.assertEqual(venta.total, Decimal('100.25'))
        self.assertEqual(venta.estado_pago, 'Pendiente')
        self.assertEqual(venta.estado, 'Pendiente')
        self.assertEqual(venta.detalles_venta.get().precio_unitario, Decimal('100.25'))
        self.assertEqual(venta.detalles_venta.get().estado, 'Pendiente de Pago')
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], 0)

    def test_invalid_quantities_and_identifiers_do_not_change_stock(self):
        for field, values in [('cantidad', [-1, 0, 1.5, '2', True, 1001, None]), ('id', [0, -1, '1', True, 999999])]:
            for value in values:
                with self.subTest(field=field, value=value):
                    data = payload(self.producto)
                    data['items'][0][field] = value
                    self.assertEqual(self.post_compra(data).status_code, 400)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertFalse(Venta.objects.exists())

    def test_unknown_type_and_duplicates_rejected(self):
        for tipo in ['desconocido', None]:
            data = payload(self.producto)
            data['items'][0]['tipo'] = tipo
            self.assertEqual(self.post_compra(data).status_code, 400)
        data = payload(self.producto)
        data['items'] *= 2
        self.assertEqual(self.post_compra(data).status_code, 400)

    def test_inactive_product_rejected(self):
        self.producto.disponible = False
        self.producto.save()
        self.assertEqual(self.post_compra().status_code, 400)

    def test_rollback_entire_purchase(self):
        data = payload(self.producto)
        data['items'].append({'tipo': 'producto', 'id': 999999, 'cantidad': 1})
        self.assertEqual(self.post_compra(data).status_code, 400)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertFalse(Venta.objects.exists())

    def test_unexpected_failure_rolls_back_and_hides_details(self):
        with patch('autenticacion.compras.Items.objects.filter', side_effect=RuntimeError('private database password')):
            response = self.post_compra()
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('private', str(response.data))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertFalse(Venta.objects.exists())

    def test_idempotent_retry_and_conflicting_payload(self):
        data = payload(self.producto)
        self.assertEqual(self.post_compra(data).status_code, 201)
        data['total'], data['items'][0]['precio'] = -1000, -1
        self.assertEqual(self.post_compra(data).status_code, 200)
        self.assertEqual(Venta.objects.count(), 1)
        data['items'][0]['cantidad'] = 2
        self.assertEqual(self.post_compra(data).status_code, 400)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)

    def test_partial_cart_preserved(self):
        carrito = Carrito.objects.create(usuario=self.turista, status=True)
        selected = Items.objects.create(carrito=carrito, producto=self.producto, precio=1)
        remaining = Items.objects.create(carrito=carrito, paquetes=self.paquete, precio=1)
        self.assertEqual(self.post_compra().status_code, 201)
        self.assertFalse(Items.objects.filter(pk=selected.pk).exists())
        self.assertTrue(Items.objects.filter(pk=remaining.pk).exists())

    def test_cart_validates_quantity_and_uses_server_price(self):
        response = self.client.post('/api/carrito/', {'producto': self.producto.pk, 'precio': -1, 'cantidad': 1}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Items.objects.get().precio, Decimal(str(self.producto.precio)))
        self.assertEqual(self.client.patch(f'/api/carrito/{Items.objects.get().pk}/', {'cantidad': -1}, format='json').status_code, 400)
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.client.patch(f'/api/carrito/{Items.objects.get().pk}/', {'cantidad': 2}, format='json').status_code, 404)

    def tour_payload(self, fecha=None, cantidad=1):
        return payload(self.producto, items=[{'tipo': 'tour', 'id': self.paquete.pk, 'cantidad': cantidad, 'fecha_reserva': fecha or str(timezone.localdate() + timedelta(days=10))}])

    def test_tour_fee_and_pending_capacity(self):
        response = self.post_compra(self.tour_payload(cantidad=2))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Venta.objects.get().total, Decimal('405.00'))
        self.assertEqual(self.post_compra(self.tour_payload(cantidad=2)).status_code, 400)
        self.assertEqual(ReservaFecha.objects.count(), 1)

    def test_invalid_tour_date_or_inactive(self):
        for fecha in ['bad-date', str(timezone.localdate()), str(timezone.localdate() - timedelta(days=1))]:
            self.assertEqual(self.post_compra(self.tour_payload(fecha)).status_code, 400)
        self.paquete.activo = False
        self.paquete.save()
        self.assertEqual(self.post_compra(self.tour_payload()).status_code, 400)

    def test_fixed_tour_date_cannot_be_changed(self):
        self.paquete.tipo_paquete = 'fijo'
        self.paquete.fecha_realizacion = timezone.localdate() + timedelta(days=10)
        self.paquete.save()
        self.assertEqual(self.post_compra(self.tour_payload(str(timezone.localdate() + timedelta(days=20)))).status_code, 400)

    def test_expiry_releases_stock_once(self):
        self.post_compra()
        venta = Venta.objects.get()
        self.assertTrue(liberar_pedido(venta.pk))
        self.assertFalse(liberar_pedido(venta.pk))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        venta.refresh_from_db()
        self.assertEqual(venta.estado_pago, 'Fallido')

    def test_expiry_releases_tour_capacity(self):
        self.post_compra(self.tour_payload(cantidad=3))
        liberar_pedido(Venta.objects.get().pk)
        self.assertFalse(ReservaFecha.objects.exists())
        self.assertEqual(self.post_compra(self.tour_payload(cantidad=3)).status_code, 201)

    @override_settings(CHECKOUT_MODE='demo')
    def test_demo_is_identified_and_not_liquidable(self):
        self.post_compra()
        detalle = Detalles_Venta.objects.get()
        detalle.estado = 'Entregado'
        detalle.save()
        self.assertEqual(Venta.objects.get().estado_pago, 'Simulado')
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], 0)

    @override_settings(CHECKOUT_MODE='disabled')
    def test_checkout_suspended(self):
        self.assertEqual(self.post_compra().status_code, 503)
        self.assertFalse(Venta.objects.exists())

    def test_feedback_and_evidence_ownership(self):
        detalle = self.paid_detail()
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.client.get(f'/api/experiencias/{detalle.pk}/feedback/').status_code, 404)
        self.assertEqual(self.client.post(f'/api/experiencias/{detalle.pk}/feedback/', {'puntuacion': 5}, format='json').status_code, 404)
        self.assertEqual(self.client.get(f'/api/experiencias/{detalle.pk}/zip/').status_code, 403)
        self.client.force_authenticate(self.agencia)
        self.assertEqual(self.client.post(f'/api/experiencias/{detalle.pk}/evidencia/', {}, format='multipart').status_code, 403)

    def test_invalid_feedback_rating(self):
        detalle = self.paid_detail()
        for rating in [0, 6, '5', True]:
            self.assertEqual(self.client.post(f'/api/experiencias/{detalle.pk}/feedback/', {'puntuacion': rating}, format='json').status_code, 400)

    def test_withdrawal_pending_and_paid_remain_deducted(self):
        self.paid_detail()
        self.client.force_authenticate(self.proveedor)
        self.assertEqual(self.client.post('/api/liquidacion/solicitar-retiro/', self.retiro_payload(), format='json').status_code, 201)
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], Decimal('42.23'))
        self.assertEqual(self.client.post('/api/liquidacion/solicitar-retiro/', self.retiro_payload(), format='json').status_code, 400)
        operator = Usuario.objects.create_user(username='staff', email='staff@example.test', is_staff=True)
        retiro = SolicitudRetiro.objects.get()
        cambiar_estado(retiro.pk, 'Procesando', operator)
        cambiar_estado(retiro.pk, 'Pagado', operator)
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], Decimal('42.23'))
        self.assertEqual(CambioEstadoRetiro.objects.count(), 3)
        with self.assertRaises(ValidationError):
            cambiar_estado(retiro.pk, 'Cancelado', operator)

    def test_rejected_withdrawal_releases_funds(self):
        self.paid_detail()
        self.client.force_authenticate(self.proveedor)
        self.client.post('/api/liquidacion/solicitar-retiro/', self.retiro_payload(), format='json')
        operator = Usuario.objects.create_user(username='staff', email='staff@example.test', is_staff=True)
        cambiar_estado(SolicitudRetiro.objects.get().pk, 'Rechazado', operator)
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], Decimal('92.23'))

    def test_invalid_withdrawals(self):
        self.paid_detail()
        self.client.force_authenticate(self.proveedor)
        for monto in ['-1', '0', 'NaN', 'Infinity', '1.001', '9999999999999999999']:
            with self.subTest(monto=monto):
                self.assertEqual(self.client.post('/api/liquidacion/solicitar-retiro/', self.retiro_payload(monto), format='json').status_code, 400)
        data = self.retiro_payload()
        data['metodo'] = 'unknown'
        self.assertEqual(self.client.post('/api/liquidacion/solicitar-retiro/', data, format='json').status_code, 400)
        data = self.retiro_payload()
        data['datos_bancarios'] = {}
        self.assertEqual(self.client.post('/api/liquidacion/solicitar-retiro/', data, format='json').status_code, 400)
        self.assertFalse(SolicitudRetiro.objects.exists())

    @override_settings(ALLOW_WITHDRAWALS=False)
    def test_withdrawals_suspended(self):
        self.client.force_authenticate(self.proveedor)
        self.assertEqual(self.client.post('/api/liquidacion/solicitar-retiro/', self.retiro_payload(), format='json').status_code, 503)

    def test_refund_not_liquidable(self):
        detalle = self.paid_detail()
        detalle.estado = 'Reembolsado'
        detalle.save()
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], 0)

    def test_provider_cannot_reject_pending_payment(self):
        self.post_compra()
        self.client.force_authenticate(self.proveedor)
        response = self.client.post('/api/proveedor/gestion-logistica/anular/', {'id_detalle': Detalles_Venta.objects.get().pk}, format='json')
        self.assertEqual(response.status_code, 400)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)

    def test_product_rejection_restores_stock_only_once(self):
        detalle = self.paid_detail()
        detalle.estado = 'Pendiente de Empaque'
        detalle.save()
        self.client.force_authenticate(self.proveedor)
        data = {'id_detalle': detalle.pk}
        for _ in range(2):
            self.assertEqual(self.client.post('/api/proveedor/gestion-logistica/anular/', data, format='json').status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 4)

    def test_unverified_notification_route_absent(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/pagos/webhook/', {'estado': 'Pagado'}, format='json').status_code, 404)
        self.assertFalse(Venta.objects.exists())


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False, CHECKOUT_MODE='pending', ALLOW_WITHDRAWALS=True,
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.agencia, self.proveedor, self.turista, self.otro, self.producto, self.paquete = fixtures()

    def concurrent(self, operation):
        barrier = Barrier(2)
        def worker(index):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return operation(index)
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker, [0, 1]))

    def purchase(self, user, data):
        try:
            procesar_compra(user, data)
            return True
        except ValidationError:
            return False

    @skipUnlessDBFeature('has_select_for_update')
    def test_two_purchases_cannot_oversell_stock(self):
        self.producto.stock = 1
        self.producto.save()
        data = [payload(self.producto), payload(self.producto)]
        result = self.concurrent(lambda i: self.purchase([self.turista, self.otro][i], data[i]))
        self.assertEqual(sorted(result), [False, True])
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
        self.assertEqual(Venta.objects.count(), 1)

    @skipUnlessDBFeature('has_select_for_update')
    def test_concurrent_retries_only_one_sale(self):
        data = payload(self.producto)
        result = self.concurrent(lambda i: self.purchase(self.turista, data))
        self.assertEqual(result, [True, True])
        self.assertEqual(Venta.objects.count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)

    @skipUnlessDBFeature('has_select_for_update')
    def test_two_reservations_cannot_exceed_capacity(self):
        self.paquete.capacidad = 1
        self.paquete.save()
        data = [payload(self.producto, items=[{'tipo': 'paquete', 'id': self.paquete.pk, 'cantidad': 1, 'fecha_reserva': str(timezone.localdate() + timedelta(days=10))}]) for _ in range(2)]
        result = self.concurrent(lambda i: self.purchase([self.turista, self.otro][i], data[i]))
        self.assertEqual(sorted(result), [False, True])
        self.assertEqual(ReservaFecha.objects.count(), 1)

    @skipUnlessDBFeature('has_select_for_update')
    def test_two_withdrawals_cannot_overcommit_balance(self):
        venta = Venta.objects.create(usuario=self.turista, total='100.25', estado='Completado', estado_pago='Pagado')
        Detalles_Venta.objects.create(venta=venta, producto=self.producto.pk, paquete=0, cantidad=1, precio_unitario='100.25', estado='Entregado')
        def operation(index):
            client = APIClient()
            client.force_authenticate(self.proveedor)
            return client.post('/api/liquidacion/solicitar-retiro/', {'monto': '60.00', 'metodo': 'nequi', 'datos_bancarios': {'cuenta': '3001234567', 'titular': 'Persona', 'numero': '123'}}, format='json').status_code
        self.assertEqual(sorted(self.concurrent(operation)), [201, 400])
        self.assertEqual(SolicitudRetiro.objects.count(), 1)


    @skipUnlessDBFeature('has_select_for_update')
    @override_settings(PAYMENT_PROVIDER='wompi', WOMPI_ENVIRONMENT='prod', WOMPI_PUBLIC_KEY='pub_prod_fixture',
                       WOMPI_PRIVATE_KEY='prv_prod_fixture', WOMPI_INTEGRITY_SECRET='fixture-integrity-secret',
                       WOMPI_EVENTS_SECRET='fixture-events-secret', WOMPI_REDIRECT_URL='https://store.example.test/pago')
    def test_concurrent_webhooks_confirm_once(self):
        from .wompi import procesar_evento
        from .models import EventoPago
        import hashlib
        venta, _ = procesar_compra(self.turista, payload(self.producto))
        data = {'id': 'concurrent-fixture-001', 'status': 'APPROVED', 'reference': str(venta.referencia_pago),
                'currency': 'COP', 'amount_in_cents': 10025, 'finalized_at': timezone.now().isoformat()}
        timestamp = int(timezone.now().timestamp())
        checksum = hashlib.sha256(f"{data['id']}APPROVED10025{timestamp}fixture-events-secret".encode()).hexdigest()
        event = {'event': 'transaction.updated', 'environment': 'prod', 'timestamp': timestamp,
                 'data': {'transaction': data}, 'signature': {'properties': ['transaction.id', 'transaction.status', 'transaction.amount_in_cents'], 'checksum': checksum}}
        with patch('autenticacion.wompi.consultar_transaccion', return_value=data):
            self.concurrent(lambda i: procesar_evento(event))
        venta.refresh_from_db()
        self.assertEqual(venta.estado_pago, 'Pagado')
        self.assertEqual(EventoPago.objects.count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False, CHECKOUT_MODE='pending', PAYMENT_PROVIDER='wompi',
                   WOMPI_ENVIRONMENT='prod', WOMPI_PUBLIC_KEY='pub_prod_fixture', WOMPI_PRIVATE_KEY='prv_prod_fixture',
                   WOMPI_INTEGRITY_SECRET='fixture-integrity-secret', WOMPI_EVENTS_SECRET='fixture-events-secret',
                   WOMPI_REDIRECT_URL='https://store.example.test/pago',
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class WompiTests(TestCase):
    def setUp(self):
        self.agencia, self.proveedor, self.turista, self.otro, self.producto, self.paquete = fixtures()
        self.client = APIClient()
        self.client.force_authenticate(self.turista)
        response = self.client.post('/api/venta/procesar/', payload(self.producto), format='json')
        self.assertEqual(response.status_code, 201)
        self.venta = Venta.objects.get()
        self.checkout = response.data['checkout_url']
        self.client.force_authenticate(None)

    def transaction(self, estado='APPROVED', **changes):
        data = {'id': 'fixture-transaction-001', 'status': estado, 'reference': str(self.venta.referencia_pago),
                'amount_in_cents': int(self.venta.total * 100), 'currency': 'COP',
                'finalized_at': timezone.now().isoformat()}
        data.update(changes)
        return data

    def event(self, data=None, environment='prod', properties=None):
        from django.conf import settings
        import hashlib
        data = data or self.transaction()
        props = properties or ['transaction.id', 'transaction.status', 'transaction.amount_in_cents']
        timestamp = int(timezone.now().timestamp())
        values = ''.join(str(data[p.split('.')[1]]) for p in props)
        checksum = hashlib.sha256((values + str(timestamp) + settings.WOMPI_EVENTS_SECRET).encode()).hexdigest()
        return {'event': 'transaction.updated', 'environment': environment, 'data': {'transaction': data},
                'timestamp': timestamp, 'signature': {'properties': props, 'checksum': checksum}}

    def webhook(self, event=None, transaction_data=None):
        with patch('autenticacion.wompi.consultar_transaccion', return_value=transaction_data or self.transaction()) as api:
            response = self.client.post('/api/pagos/wompi/webhook/', event or self.event(), format='json')
        return response, api

    def test_checkout_amount_signature_and_expiration(self):
        from urllib.parse import urlsplit, parse_qs
        import hashlib
        values = parse_qs(urlsplit(self.checkout).query)
        self.assertEqual(values['amount-in-cents'], ['10025'])
        self.assertEqual(values['public-key'], ['pub_prod_fixture'])
        self.assertNotIn('prv_', self.checkout)
        signature = hashlib.sha256((str(self.venta.referencia_pago) + '10025COP' + values['expiration-time'][0] + 'fixture-integrity-secret').encode()).hexdigest()
        self.assertEqual(values['signature:integrity'], [signature])
        self.assertIn(f'venta_id={self.venta.pk}', values['redirect-url'][0])

    def test_invalid_checksum_cannot_modify_or_call_provider(self):
        event = self.event()
        event['signature']['checksum'] = '0' * 64
        response, api = self.webhook(event)
        self.assertEqual(response.status_code, 400)
        api.assert_not_called()
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Pendiente')

    def test_approved_notification_and_retry_only_one_effect(self):
        from .models import EventoPago
        event = self.event()
        self.assertEqual(self.webhook(event)[0].status_code, 200)
        response, api = self.webhook(event)
        self.assertEqual(response.status_code, 200)
        api.assert_not_called()
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Pagado')
        self.assertEqual(self.venta.detalles_venta.get().estado, 'Pendiente de Empaque')
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)
        self.assertEqual(EventoPago.objects.count(), 1)

    def test_wrong_amount_currency_reference_or_environment_rejected(self):
        cases = [{'amount_in_cents': 1}, {'currency': 'USD'}, {'reference': str(uuid4())}, {'reference': 'not-a-uuid'}]
        for changes in cases:
            with self.subTest(changes=changes):
                self.assertEqual(self.webhook(transaction_data=self.transaction(**changes))[0].status_code, 400)
        response, api = self.webhook(self.event(environment='test'))
        self.assertEqual(response.status_code, 400)
        api.assert_not_called()
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Pendiente')

    def test_reference_from_api_prevents_unsigned_reference_tampering(self):
        # Reference is not among the default signed properties, so use the API value.
        event = self.event()
        event['data']['transaction']['reference'] = str(uuid4())
        self.assertEqual(self.webhook(event)[0].status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Pagado')

    def test_signature_supports_dynamic_property_order(self):
        event = self.event(properties=['transaction.amount_in_cents', 'transaction.currency', 'transaction.id', 'transaction.status'])
        event['signature']['checksum'] = event['signature']['checksum'].upper()
        self.assertEqual(self.webhook(event)[0].status_code, 200)

    def test_declined_payment_releases_stock_once(self):
        data = self.transaction('DECLINED')
        event = self.event(data)
        for _ in range(2):
            self.assertEqual(self.webhook(event, data)[0].status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Fallido')

    def test_expired_then_approved_requires_review_without_consuming_stock(self):
        liberar_pedido(self.venta.pk)
        self.assertEqual(self.webhook()[0].status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Revision')
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], 0)

    def test_late_approval_releases_reservation_and_requires_review(self):
        data = self.transaction(finalized_at=(self.venta.vence_en + timedelta(minutes=1)).isoformat())
        self.assertEqual(self.webhook(self.event(data), data)[0].status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Revision')
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

    def test_voided_payment_excluded_from_liquidation(self):
        self.webhook()
        detalle = self.venta.detalles_venta.get()
        detalle.estado = 'Entregado'
        detalle.save()
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], Decimal('92.23'))
        data = self.transaction('VOIDED')
        self.assertEqual(self.webhook(self.event(data), data)[0].status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Reembolsado')
        self.assertEqual(_calcular_saldos(self.proveedor)['saldo_disponible'], 0)

    @override_settings(WOMPI_ENVIRONMENT='test', WOMPI_PUBLIC_KEY='pub_test_fixture', WOMPI_PRIVATE_KEY='prv_test_fixture')
    def test_sandbox_payment_not_real_or_liquidable(self):
        self.venta.ambiente_pago = 'test'
        self.venta.save()
        self.assertEqual(self.webhook(self.event(environment='test'))[0].status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Simulado')

    def test_missing_or_invalid_finalization_rejected(self):
        for value in ['', 'not-a-date', '2026-01-01T00:00:00']:
            data = self.transaction(finalized_at=value)
            self.assertEqual(self.webhook(self.event(data), data)[0].status_code, 400)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Pendiente')

    def test_status_requires_purchaser(self):
        path = f'/api/venta/{self.venta.pk}/estado/'
        self.assertEqual(self.client.get(path).status_code, 401)
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.client.get(path).status_code, 404)
        self.client.force_authenticate(self.turista)
        self.assertEqual(self.client.get(path).data['estado_pago'], 'Pendiente')

    def test_pending_order_cancellation_releases_and_late_payment_needs_review(self):
        self.client.force_authenticate(self.turista)
        path = f'/api/venta/{self.venta.pk}/cancelar/'
        self.assertEqual(self.client.post(path).status_code, 200)
        self.assertEqual(self.client.post(path).status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.client.force_authenticate(None)
        self.assertEqual(self.webhook()[0].status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Revision')

    def test_other_user_cannot_cancel_pending_order(self):
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.client.post(f'/api/venta/{self.venta.pk}/cancelar/').status_code, 404)

    def test_provider_outage_does_not_modify_sale(self):
        from .wompi import WompiUnavailable
        with patch('autenticacion.wompi.consultar_transaccion', side_effect=WompiUnavailable()):
            response = self.client.post('/api/pagos/wompi/webhook/', self.event(), format='json')
        self.assertEqual(response.status_code, 503)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado_pago, 'Pendiente')

    def test_private_api_headers_timeout_and_no_redirect(self):
        from .wompi import consultar_transaccion
        with patch('autenticacion.wompi.requests.get') as get:
            get.return_value.status_code = 200
            get.return_value.json.return_value = {'data': self.transaction()}
            self.assertEqual(consultar_transaccion('fixture-transaction-001')['status'], 'APPROVED')
            args, kwargs = get.call_args
            self.assertEqual(args[0], 'https://production.wompi.co/v1/transactions/fixture-transaction-001')
            self.assertEqual(kwargs['headers']['Authorization'], 'Bearer prv_prod_fixture')
            self.assertFalse(kwargs['allow_redirects'])
            self.assertEqual(kwargs['timeout'], (3, 10))

    @override_settings(WOMPI_PRIVATE_KEY='')
    def test_missing_credentials_blocks_new_checkout_before_reserving(self):
        self.client.force_authenticate(self.turista)
        response = self.client.post('/api/venta/procesar/', payload(self.producto), format='json')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(Venta.objects.count(), 1)
