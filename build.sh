#!/usr/bin/env bash
# Build script for Render.com deployment

# Exit on any error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --settings=root.settings_production

# Run database migrations
python manage.py migrate --settings=root.settings_production

# Create superuser if it doesn't exist (optional)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell --settings=root.settings_production
