import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Créer un superuser
u, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@obidon.com',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'Admin',
        'last_name': 'Obidon'
    }
)
u.set_password('admin123')
u.save()

print('✓ Superuser créé' if created else '✓ Superuser existe déjà')
print('📧 Email: admin@obidon.com')
print('🔐 Mot de passe: admin123')
print('🌐 Dashboard: http://localhost:8000/admin-dashboard/')
print('🛠️  Admin Django: http://localhost:8000/admin/')
