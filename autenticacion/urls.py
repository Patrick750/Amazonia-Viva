from django.urls import path
from . import views, vistas_reportes, vistas_liquidacion
from .views import (
    RegistroAgencia, RegistroProveedor, VerificarEmail, RegistroTurista, 
    Login, Logout, Actividades, NewPack, UpdatePack, PaquetesTuristicos, 
    DeletePack, CatalogoTours, CatalogoProductos, CategoriaPaqueteListView,
    CategoriaProductoListView, FavoritoView, CarritoView, DetalleTourPublico,
    DetalleProductoPublico, UserStatsView, PerfilView, PerfilFotoView,
    VerificarCredenciales, ConfirmarPasswordView, PerfilPublicoView, ProcesarPagoView,
    CuposDisponiblesView, MisReservasView, CancelarReservaView, DashboardKPIsView, CargaMasivaPaquetesAPIView
)
from .views_productos import ProductosAPIView, ProductoDetalleAPIView, CargaMasivaProductosAPIView
from .vistas_experiencias import (
    ExperienciasDashboardView, SubirEvidenciaView, DetalleFeedbackView,
    MisExperienciasTuristaView, DescargarEvidenciasZipView
)

urlpatterns = [
    path("turista/experiencias/", MisExperienciasTuristaView.as_view(), name='mis_experiencias_turista'),
    path('signup/agencia/', RegistroAgencia.as_view(), name='signup_agencia'),
    path('signup/proveedor/', RegistroProveedor.as_view(), name='signup_proveedor'),
    path('signup/turista/', RegistroTurista.as_view(), name='signup_turista'),
    path('verificaremail/', VerificarEmail.as_view(), name='verificar_email'),
    path('login/', Login.as_view(), name='auth_login'),
    path("logout/", Logout.as_view(), name="logout"),
    path("actividades/", Actividades.as_view(), name="actividades"),
    path("createnewpack/", NewPack.as_view(), name="createnewpack"),
    path("updatepack/<int:pk>/", UpdatePack.as_view(), name="updatepack"),
    path("deletepack/<int:pk>/", DeletePack.as_view(), name="deletepack"),
    path("pack/", PaquetesTuristicos.as_view(), name="packs"),
    path("pack/carga-masiva/", CargaMasivaPaquetesAPIView.as_view(), name="paquetes_carga_masiva"),
    path("productos/", ProductosAPIView.as_view(), name="productos_list_create"),
    path("productos/carga-masiva/", CargaMasivaProductosAPIView.as_view(), name="productos_carga_masiva"),
    path("productos/<int:pk>/", ProductoDetalleAPIView.as_view(), name="productos_detail"),
    path("catalogo/tours/", CatalogoTours.as_view(), name="catalogo_tours"),
    path("catalogo/productos/", CatalogoProductos.as_view(), name="catalogo_productos"),
    path("categorias-paquetes/", CategoriaPaqueteListView.as_view(), name="categorias_paquetes"),
    path("categorias-productos/", CategoriaProductoListView.as_view(), name="categorias_productos"),
    path("favoritos/", FavoritoView.as_view(), name="favoritos"),
    path("favoritos/<int:pk>/", FavoritoView.as_view(), name="favorito_detail"),
    path("carrito/", CarritoView.as_view(), name="carrito"),
    path("carrito/<int:pk>/", CarritoView.as_view(), name="carrito_detail"),

    path("catalogo/tours/<int:pk>/", DetalleTourPublico.as_view(), name="detalle_tour_publico"),
    path("catalogo/productos/<int:pk>/", DetalleProductoPublico.as_view(), name="detalle_producto_publico"),
    path("user/stats/", UserStatsView.as_view(), name="user_stats"),
    path("dashboard/stats/", DashboardKPIsView.as_view(), name="dashboard_stats"),
    path("perfil/", PerfilView.as_view(), name="perfil_usuario"),
    path("perfil/foto/", PerfilFotoView.as_view(), name="perfil_foto"),
    path("perfil/publico/<int:id>/", PerfilPublicoView.as_view(), name="perfil_publico_api"),
    path("verificar-credenciales/", VerificarCredenciales.as_view(), name="verificar_credenciales"),
    path("confirmar-password/", ConfirmarPasswordView.as_view(), name="confirmar_password"),
    path("venta/procesar/", ProcesarPagoView.as_view(), name="procesar_pago"),
    path("cupos/<int:pk>/", CuposDisponiblesView.as_view(), name="cupos_disponibles"),
    path("mis-reservas/", MisReservasView.as_view(), name="mis_reservas"),
    path("mis-reservas/<int:pk>/cancelar/", CancelarReservaView.as_view(), name='cancelar_reserva'),
    path("mis-productos/", views.MisProductosTuristaView.as_view(), name='mis_productos_turista'),
    path("mis-productos/devolucion/", views.SolicitarDevolucionAPIView.as_view(), name='solicitar_devolucion'),
    path("mis-productos/cancelar/", views.CancelarPedidoTuristaAPIView.as_view(), name='cancelar_pedido_turista'),
    # --- GESTIÓN LOGÍSTICA (AGENCIAS) ---
    path("agencia/gestion-logistica/", views.GestionLogisticaAgenciaAPIView.as_view(), name='gestion_agencia_logistica'),
    path("agencia/gestion-logistica/anular/", views.GestionAnularReservaAgenciaAPIView.as_view(), name='gestion_agencia_anular'),
    path("agencia/gestion-logistica/anular-salida/", views.GestionAnularSalidaAgenciaAPIView.as_view(), name='gestion_agencia_anular_salida'),
    path("agencia/gestion-logistica/exportar/", vistas_reportes.ExportarManifiestoAgenciaAPIView.as_view(), name='exportar_manifiesto_agencia'),

    # --- GESTIÓN LOGÍSTICA (PROVEEDORES) ---
    path("proveedor/gestion-logistica/", views.GestionLogisticaProveedorAPIView.as_view(), name='gestion_proveedor_logistica'),
    path("proveedor/gestion-logistica/anular/", views.GestionAnularReservaProveedorAPIView.as_view(), name='gestion_proveedor_anular'),
    path("proveedor/gestion-logistica/actualizar-estado/", views.GestionActualizarEstadoPedidoAPIView.as_view(), name='gestion_proveedor_actualizar_estado'),
    path("proveedor/gestion-logistica/exportar/", vistas_reportes.ExportarDespachoProveedorAPIView.as_view(), name='exportar_despacho_proveedor'),
    path("proveedor/gestion-logistica/exportar-global/", vistas_reportes.ExportarVentasGlobalesMensualAPIView.as_view(), name='exportar_ventas_globales_mensual'),

    # Endpoints de Experiencias y Feedback
    path("experiencias/dashboard/", ExperienciasDashboardView.as_view(), name='experiencias_dashboard'),
    path("experiencias/<int:pk>/evidencia/", SubirEvidenciaView.as_view(), name='subir_evidencia'),
    path("experiencias/<int:pk>/feedback/", DetalleFeedbackView.as_view(), name='detalle_feedback'),
    path("experiencias/<int:pk>/zip/", DescargarEvidenciasZipView.as_view(), name='descargar_evidencias_zip'),

    # ── Módulo Liquidación / Billetera Virtual ────────────────────────────────
    path("liquidacion/saldos/", vistas_liquidacion.LiquidacionSaldosView.as_view(), name='liquidacion_saldos'),
    path("liquidacion/solicitar-retiro/", vistas_liquidacion.SolicitarRetiroView.as_view(), name='liquidacion_retiro'),
    path("liquidacion/movimientos/", vistas_liquidacion.MovimientosView.as_view(), name='liquidacion_movimientos'),
    path("liquidacion/exportar/", vistas_liquidacion.ExportarMovimientosView.as_view(), name='liquidacion_exportar'),
]