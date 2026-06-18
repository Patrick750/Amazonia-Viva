import os

path = '/home/patrickortiz/Documentos/Amazonia-Viva/autenticacion/views.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports and logger
old_import = "from .serializers import calcular_cupos_disponibles\n"
new_import = "from .serializers import calcular_cupos_disponibles\nimport logging\nfrom django.utils.decorators import method_decorator\nfrom ratelimit.decorators import ratelimit\n\nlogger = logging.getLogger('autenticacion')\n"
content = content.replace(old_import, new_import)

# 2. VerificarEmail ratelimit
old_def = "class VerificarEmail(APIView):\n    def post(self, request):"
new_def = "class VerificarEmail(APIView):\n    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))\n    def post(self, request):"
content = content.replace(old_def, new_def)

# 3. Exact print replacements
content = content.replace("print('Logout exitoso')", "logger.info('Logout exitoso')")
content = content.replace("print('Error en los serializers: ', serializer.errors)", "logger.error('Error en los serializers: %s', serializer.errors)")
content = content.replace("print('Error en update serializers: ', serializer.errors)", "logger.error('Error en update serializers: %s', serializer.errors)")

# 4. Regex print replacements for formatted strings
import re

content = re.sub(r'print\((f["\']ERROR[^)]+)\)', r'logger.error(\1)', content)
content = re.sub(r'print\((f["\']CRITICAL ERROR[^)]+)\)', r'logger.critical(\1)', content)
content = re.sub(r'print\((f["\']DEBUG[^)]+)\)', r'logger.debug(\1)', content)
content = re.sub(r'print\((f["\']Error en Gestion[^)]+)\)', r'logger.error(\1)', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactoring done.")
