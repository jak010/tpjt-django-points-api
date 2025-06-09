
PYHTONPATH=$(PWD)/src
SRC=./src
DOCKER=./.docker
DJANGO_SETTINGS_MODULE=config.settings.local

run.local:
	python $(SRC)/manage.py runserver 0.0.0.0:8000 --settings=$(DJANGO_SETTINGS_MODULE)

run.db:
	cd $(DOCKER) && sudo docker-compose up -d


migrations:
	python $(PYHTONPATH)/manage.py makemigrations --settings=$(DJANGO_SETTINGS_MODULE)

migrate:
	python $(SRC)/manage.py migrate --settings=$(DJANGO_SETTINGS_MODULE)