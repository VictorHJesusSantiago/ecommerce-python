.PHONY: install test lint format run migrate shell

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=apps

lint:
	flake8 apps/ tests/
	isort --check-only apps/ tests/

format:
	black apps/ tests/
	isort apps/ tests/

run:
	python manage.py runserver

migrate:
	python manage.py migrate

shell:
	python manage.py shell

createsuperuser:
	python manage.py createsuperuser

seed:
	python scripts/seed_data.py

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-test:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run web pytest
