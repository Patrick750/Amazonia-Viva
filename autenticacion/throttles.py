import hashlib
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework.throttling import BaseThrottle
from .models import IntentosCredenciales


class CredentialsThrottle(BaseThrottle):
    """Contador compartido entre workers, serializado en la base de datos."""
    def allow_request(self, request, view):
        identities = ['ip:' + self.get_ident(request)]
        if request.user.is_authenticated:
            identities.append('user:' + str(request.user.pk))
        elif request.data.get('email'):
            identities.append('email:' + str(request.data['email']).strip().lower())
        allowed = True
        for identity in identities:
            key = hashlib.sha256(identity.encode()).hexdigest()
            with transaction.atomic():
                IntentosCredenciales.objects.get_or_create(clave=key)
                bucket = IntentosCredenciales.objects.select_for_update().get(clave=key)
                now = timezone.now()
                if bucket.inicio <= now - timedelta(minutes=1):
                    bucket.inicio, bucket.intentos = now, 0
                if bucket.intentos >= 5:
                    allowed = False
                else:
                    bucket.intentos += 1
                bucket.save(update_fields=['inicio', 'intentos'])
        return allowed

    def get_ident(self, request):
        # El proxy debe preservar REMOTE_ADDR o aplicar su propio límite por IP real.
        return request.META.get('REMOTE_ADDR', '')

    def wait(self):
        return 60
