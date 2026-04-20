import os
import django
import random
from datetime import date, timedelta
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazoniaviva.settings')
django.setup()

from autenticacion.models import Agencia, Turista, Usuario

AGENCY_NAMES = [
    "Amazonia Expeditions", "Selva Sagrada", "Rio Amazonas Tours", "Verde Infinito",
    "EcoTravesía Amazónica", "Jungla Viva", "Delfín Gris Viajes", "Cultura Verde",
    "Aventura Kayak Amazon", "Paraíso Selvático", "Guardianes del Amazonas",
    "EcoSenda", "Amazon Sun", "Selva Colorida", "Rutas del Yari", "Viento y Selva",
    "Corazón del Amazonas", "Amazon Star", "Tierra Ancestral", "Amazon Escape"
]

TOURIST_NAMES = [
    "Juan Perez", "Maria Garcia", "Carlos Lopez", "Ana Martinez", "Luis Rodriguez",
    "Elena Sanchez", "Diego Ramirez", "Sofia Torres", "Javier Hernandez", "Lucia Gomez",
    "Ricardo Diaz", "Paola Morales", "Fernando Castro", "Valentina Ortiz", "Oscar Silva",
    "Patricia Nuñez", "Gabriel Mendoza", "Isabella Rios", "Andres Vega", "Camila Lara",
    "Mateo Salazar", "Valeria Pineda", "Sebastián Rivas", "Daniela Montes", "Nicolas Peña",
    "Mariana Soto", "Alejandro Leon", "Ximena Luna", "Hugo Duarte", "Natalia Mejia",
    "Eduardo Bravo", "Catalina Vera", "Felipe Marin", "Sara Cabrera", "Emilio Pinto",
    "Renata Cordero", "Ivan Gallardo", "Jimena Campos", "Raul Fuentes", "Adriana Rojas",
    "Jorge Navarro", "Gloria Tapia", "Humberto Saavedra", "Beatriz Pacheco", "Esteban Guerra",
    "Monica Delgado", "Arturo Cisneros", "Victoria Espinoza", "Angel Paredes", "Lorena Valdés"
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def create_agencies():
    print(f"Creating {len(AGENCY_NAMES)} agencies...", flush=True)
    password = "pac131pap"
    for name in AGENCY_NAMES:
        username = slugify(name)
        email = f"{username}@test.com"
        if not Usuario.objects.filter(email=email).exists():
            agencia = Agencia.objects.create(
                email=email,
                username=username,
                nombre_agencia=name,
                numero_telefonico=f"300{random.randint(1000000, 9999999)}",
                descripcion=f"Especialistas en {name}.",
                nit=f"900{random.randint(100000, 999999)}-{random.randint(0,9)}"
            )
            agencia.set_password(password)
            agencia.save()
            print(f"  Created Agency: {name} ({email})", flush=True)
        else:
            # Update password for existing ones
            u = Usuario.objects.get(email=email)
            u.set_password(password)
            u.save()
            print(f"  Updated Password for Agency: {name}", flush=True)

def create_tourists():
    print(f"Creating {len(TOURIST_NAMES)} tourists...", flush=True)
    password = "pac131pap"
    for name in TOURIST_NAMES:
        parts = name.split()
        first_name = parts[0]
        last_name = parts[1]
        username = slugify(name)
        email = f"{username}@test.com"
        
        if not Usuario.objects.filter(email=email).exists():
            turista = Turista.objects.create(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                fecha_nacimiento=date(1980, 1, 1) + timedelta(days=random.randint(0, 12000)),
                numero_identidad=f"1{random.randint(0, 999999999):09d}",
                numero_telefonico=f"310{random.randint(1000000, 9999999)}"
            )
            turista.set_password(password)
            turista.save()
            print(f"  Created Tourist: {name} ({email})", flush=True)
        else:
            # Update password for existing ones
            u = Usuario.objects.get(email=email)
            u.set_password(password)
            u.save()
            print(f"  Updated Password for Tourist: {name}", flush=True)

if __name__ == "__main__":
    create_agencies()
    create_tourists()
    print("Done!", flush=True)
