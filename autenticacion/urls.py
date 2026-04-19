from django.urls import path
from . import views, vistas_reportes
from .views import (
    RegistroAgencia, RegistroProveedor, VerificarEmail, RegistroTurista, 
    Login, Logout, Actividades, NewPack, UpdatePack, PaquetesTuristicos, 
    DeletePack, CatalogoTours, CatalogoProductos, CategoriaPaqueteListView,
    CategoriaProductoListView, FavoritoView, CarritoView, DetalleTourPublico,
    DetalleProductoPublico, UserStatsView, PerfilView, PerfilFotoView,
    VerificarCredenciales, ConfirmarPasswordView, PerfilPublicoView, ProcesarPagoView,
    CuposDisponiblesView, MisReservasView, CancelarReservaView
)
from .views_productos import ProductosAPIView, ProductoDetalleAPIView
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
    path("productos/", ProductosAPIView.as_view(), name="productos_list_create"),
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
    # --- GESTIÓN LOGÍSTICA (AGENCIAS) ---
    path("gestion-agencia/logistica/", views.GestionAgenciaLogisticaAPIView.as_view(), name='gestion_agencia_logistica'),
    path("gestion-agencia/logistica/anular/", views.GestionAnularAgenciaAPIView.as_view(), name='gestion_agencia_anular'),
    path("gestion-agencia/logistica/anular-salida/", views.GestionAnularSalidaAgenciaAPIView.as_view(), name='gestion_agencia_anular_salida'),
    path("gestion-agencia/logistica/exportar/", vistas_reportes.ExportarManifiestoAgenciaAPIView.as_view(), name='exportar_manifiesto_agencia'),

    # --- GESTIÓN LOGÍSTICA (PROVEEDORES) ---
    path("gestion-proveedor/logistica/", views.GestionProveedorLogisticaAPIView.as_view(), name='gestion_proveedor_logistica'),
    path("gestion-proveedor/logistica/anular/", views.GestionAnularProveedorAPIView.as_view(), name='gestion_proveedor_anular'),
    path("gestion-proveedor/logistica/actualizar-estado/", views.GestionActualizarEstadoPedidoAPIView.as_view(), name='gestion_proveedor_actualizar_estado'),
    path("gestion-proveedor/logistica/exportar/", vistas_reportes.ExportarDespachoProveedorAPIView.as_view(), name='exportar_despacho_proveedor'),

    # Endpoints de Experiencias y Feedback
    path("experiencias/dashboard/", ExperienciasDashboardView.as_view(), name='experiencias_dashboard'),
    path("experiencias/<int:pk>/evidencia/", SubirEvidenciaView.as_view(), name='subir_evidencia'),
    path("experiencias/<int:pk>/feedback/", DetalleFeedbackView.as_view(), name='detalle_feedback'),
    path("experiencias/<int:pk>/zip/", DescargarEvidenciasZipView.as_view(), name='descargar_evidencias_zip'),
]