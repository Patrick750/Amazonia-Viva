import os
import django
import io
import zipfile
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazonia_viva.settings')
django.setup()

from autenticacion.models import Detalles_Venta

def test_zip(pk):
    detalle = Detalles_Venta.objects.get(pk=pk)
    evidencias = detalle.evidencias.all()
    print(f"Encontradas {len(evidencias)} evidencias para el detalle {pk}")
    
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, ev in enumerate(evidencias):
            print(f"Procesando {ev.imagen.url}...")
            try:
                # Usar un User-Agent para evitar problemas
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(ev.imagen.url, headers=headers, timeout=10)
                print(f"Status: {response.status_code}, Tamaño: {len(response.content)}")
                if response.status_code == 200 and len(response.content) > 0:
                    ext = ev.imagen.name.split('.')[-1] if '.' in ev.imagen.name else 'jpg'
                    filename = f"evidencia_{i+1}.{ext}"
                    zip_file.writestr(filename, response.content)
                    print(f"Archivo {filename} añadido.")
                else:
                  print(f"Error: Status {response.status_code} o contenido vacío.")
            except Exception as e:
                print(f"Error descargando imagen {ev.id}: {e}")

    buffer.seek(0)
    zip_data = buffer.getvalue()
    print(f"Tamaño total del ZIP: {len(zip_data)} bytes")
    
    # Verificar contenido del zip
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
        print(f"Archivos en el ZIP: {zf.namelist()}")

if __name__ == "__main__":
    test_zip(22)
