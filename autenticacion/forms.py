from django.forms import forms
from .models import Agencia, Proveedor, Usuario

class signup_agencia(forms.ModelForm):
    class Meta:
        model = Agencia
        fields = 'nombre_agencia,email,numero_telefonico,password'
