#!/usr/bin/env bash
# Render runs this script on every deploy
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Make sure the required superuser exists (admin / admin123)
python manage.py shell -c "
from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username='admin')
u.is_superuser = u.is_staff = u.is_active = True
u.set_password('admin123')
u.save()
"
