from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.db import transaction
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class Command(BaseCommand):
    help = 'Invalida sesiones y refresh tokens tras rotar la clave comprometida.'

    @transaction.atomic
    def handle(self, *args, **options):
        Session.objects.all().delete()
        for token in OutstandingToken.objects.all().iterator():
            BlacklistedToken.objects.get_or_create(token=token)
        self.stdout.write('Sesiones y tokens de renovación invalidados.')
