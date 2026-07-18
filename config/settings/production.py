echo "from .base import *" > config/settings/production.py
echo "" >> config/settings/production.py
echo "DEBUG = False" >> config/settings/production.py
echo "ALLOWED_HOSTS = ['yourdomain.com']" >> config/settings/production.py