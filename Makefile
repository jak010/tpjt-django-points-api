
PYHTONPATH=$(PWD)/src
SRC=./src
DOCKER=./.docker
DJANGO_SETTINGS_MODULE=config.settings.local

TEST_API=$(SRC)/apps/tests/locust
API_HOST=127.0.0.1
API_PORT=8000

run.local:
	python $(SRC)/manage.py runserver 0.0.0.0:8000 --settings=$(DJANGO_SETTINGS_MODULE)

run.db:
	cd $(DOCKER) && sudo docker-compose up -d


migrations:
	python $(PYHTONPATH)/manage.py makemigrations --settings=$(DJANGO_SETTINGS_MODULE)

migrate:
	python $(SRC)/manage.py migrate --settings=$(DJANGO_SETTINGS_MODULE)



# Load Test

api.test.point_earn:
	locust -f $(TEST_API)/test_point_earn_api.py -H http://$(API_HOST):$(API_PORT)