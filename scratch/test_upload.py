import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazoniaviva.settings")
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from autenticacion.models import Detalles_Venta, ExperienciaEvidencia, Venta, Usuario, PaqueteTuristico, Agencia

# Get or create necessary objects to test
user = Usuario.objects.first()
agencia = Agencia.objects.first()
if not agencia:
    agencia = Agencia.objects.create(nombre="Test", usuario=user)
paquete = PaqueteTuristico.objects.first()
if not paquete:
    paquete = PaqueteTuristico.objects.create(nombre="Test Tour", agencia=agencia, precio=10, cupo_maximo=10)

venta = Venta.objects.first()
if not venta:
    venta = Venta.objects.create(usuario=user, total=10, metodo_pago="tarjeta", comprobante_pago="test")

detalle = Detalles_Venta.objects.first()
if not detalle:
    detalle = Detalles_Venta.objects.create(venta=venta, paquete=paquete, cantidad=1, precio_unitario=10, subtotal=10)

file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

try:
    evidencia = ExperienciaEvidencia.objects.create(
        detalle_venta=detalle,
        imagen=file
    )
    print("Success:", evidencia.imagen.url)
except Exception as e:
    print("Error:", type(e).__name__, str(e))
