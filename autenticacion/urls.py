from django.urls import path
from .views import (
    RegistroAgencia, RegistroProveedor, VerificarEmail, RegistroTurista, 
    Login, Logout, Actividades, NewPack, UpdatePack, PaquetesTuristicos, 
    DeletePack, CatalogoTours, CatalogoProductos, CategoriaPaqueteListView,
    CategoriaProductoListView
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
]