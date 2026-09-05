#!/bin/bash
set -e

echo "Deploying E-Commerce project..."

docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d

docker-compose -f docker/docker-compose.yml exec web python manage.py migrate
docker-compose -f docker/docker-compose.yml exec web python manage.py collectstatic --noinput

echo "Deployment complete!"
