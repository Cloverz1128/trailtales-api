# create_superuser.py
from django.contrib.auth.models import User

username = 'admin'
password = 'admin'
email = 'admin@twitter.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('Superuser created.')
else:
    print('Superuser creation skipped.')
