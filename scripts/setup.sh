#!/bin/bash
set -e

echo "Setting up E-Commerce project..."

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

echo "Setup complete! Run: python manage.py runserver"
