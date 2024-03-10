.PHONY: start stop start-local

cfehome=cfehome
start:
	sed -i "s/'HOST': 'localhost',/'HOST': 'postgres',/g" $(cfehome)/settings.py
	docker-compose up --build

stop:
	docker-compose down

start-local:
	sed -i "s/'HOST': 'postgres',/'HOST': 'localhost',/g" $(cfehome)/settings.py
	docker-compose up db redis
	python manage.py runserver