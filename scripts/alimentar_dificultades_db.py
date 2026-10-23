"""Alimenta el catálogo completo del estándar de paquetes mediante Django.

Uso:
    python scripts/alimentar_dificultades_db.py
"""

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazoniaviva.settings")

import django
from django.core.management import call_command


if __name__ == "__main__":
    django.setup()
    call_command("seed_estandar_paquetes")
