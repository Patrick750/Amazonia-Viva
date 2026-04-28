import random
import re
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
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

class Command(BaseCommand):
    help = 'Crea agencias y turistas de prueba'

    def handle(self, *args, **options):
        password = "pac131pap"
        
        # Obtener o crear los grupos (Roles)
        grupo_agencia, _ = Group.objects.get_or_create(name='agencia')
        grupo_turista, _ = Group.objects.get_or_create(name='turista')

        self.stdout.write(self.style.SUCCESS(f"Iniciando creacion de {len(AGENCY_NAMES)} agencias..."))
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
                agencia.groups.add(grupo_agencia) # Asignar rol
                self.stdout.write(f"  - Creada Agencia: {name}")
            else:
                u = Usuario.objects.get(email=email)
                u.set_password(password)
                u.groups.add(grupo_agencia) # Asegurar rol en actualización
                u.save()
                self.stdout.write(self.style.WARNING(f"  - Actualizada Agencia (Rol + Password): {name}"))

        self.stdout.write(self.style.SUCCESS(f"\nIniciando creacion de {len(TOURIST_NAMES)} turistas..."))
        for name in TOURIST_NAMES:
            parts = name.split()
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
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
                turista.groups.add(grupo_turista) # Asignar rol
                self.stdout.write(f"  - Creado Turista: {name}")
            else:
                u = Usuario.objects.get(email=email)
                u.set_password(password)
                u.groups.add(grupo_turista) # Asegurar rol en actualización
                u.save()
                self.stdout.write(self.style.WARNING(f"  - Actualizado Turista (Rol + Password): {name}"))

        self.stdout.write(self.style.SUCCESS("\nSembrado de usuarios completado con exito!"))
