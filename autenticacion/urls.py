from django.urls import path
from .views import RegistroAgencia, RegistroProveedor, VerificarEmail, RegistroTurista, Login, Logout


urlpatterns = [
    path('signup/agencia/', RegistroAgencia.as_view(), name='signup_agencia'),
    path('signup/proveedor/', RegistroProveedor.as_view(), name='signup_proveedor'),
    path('signup/turista/', RegistroTurista.as_view(), name='signup_turista'),
    path('verificaremail/', VerificarEmail.as_view(), name='verificar_email'),
    path('login/', Login.as_view(), name='auth_login'),
    path("logout/", Logout.as_view(), name="logout")
]