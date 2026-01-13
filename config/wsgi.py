import os
import sys

# ajuste <seuuser> pro seu username
path = "/home/<seuuser>/saas/shiatsu-booking-saas"
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# variáveis de ambiente (substitua pelos valores reais)
os.environ["DJANGO_SECRET_KEY"] = "GERE-UMA-CHAVE-FORTE-AQUI"
os.environ["DJANGO_ALLOWED_HOST"] = "<seuuser>.pythonanywhere.com"
os.environ["DJANGO_DEBUG"] = "0"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()