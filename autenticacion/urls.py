from django.urls import path
from .views import RegistroAgencia, RegistroProveedor, VerificarEmail, login


urlpatterns = [
    path('signup/agencia/', RegistroAgencia.as_view(), name='signup_agencia'),
    path('signup/agencia/', RegistroAgencia.as_view(), name='signup_agencia'),
    path('verificaremail/', VerificarEmail.as_view(), name='verificar_email')
]