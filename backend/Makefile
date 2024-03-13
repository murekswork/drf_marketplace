.PHONY: start stop start-local

cfehome=cfehome

start:
	sed -i "s/'HOST': 'localhost',/'HOST': 'postgres',/g" $(cfehome)/settings.py
	docker-compose up -d --build

stop:
	docker-compose down

start-local:
	sed -i "s/'HOST': 'postgres',/'HOST': 'localhost',/g" $(cfehome)/settings.py
	docker-compose up -d db redis
	python manage.py runserver

go-web:
	docker-compose exec web /bin/bash

test:
	docker compose exec web python manage.py test --pattern="test_*.py"

go-db:
	docker-compose exec db /bin/bash
