from django.contrib import admin

from .models import (
    EstandarPaquete,
    FuenteEstandarPaquete,
    ModalidadTurismo,
    PrincipioEstandarPaquete,
)


admin.site.register(EstandarPaquete)
admin.site.register(ModalidadTurismo)
admin.site.register(PrincipioEstandarPaquete)
admin.site.register(FuenteEstandarPaquete)
