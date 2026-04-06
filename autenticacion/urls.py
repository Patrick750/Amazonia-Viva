from django.urls import path
from .views import (
    RegistroAgencia, RegistroProveedor, VerificarEmail, RegistroTurista, 
    Login, Logout, Actividades, NewPack, UpdatePack, PaquetesTuristicos, 
    DeletePack, CatalogoTours, CatalogoProductos, CategoriaPaqueteListView,
    CategoriaProductoListView, FavoritoView, CarritoView, DetalleTourPublico,
    DetalleProductoPublico, UserStatsView, PerfilView, PerfilFotoView,
    VerificarCredenciales, ConfirmarPasswordView
)
from .views_productos import ProductosAPIView, ProductoDetalleAPIView

urlpatterns = [
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
    path("verificar-credenciales/", VerificarCredenciales.as_view(), name="verificar_credenciales"),
    path("confirmar-password/", ConfirmarPasswordView.as_view(), name="confirmar_password"),
]