
PYHTONPATH=$(PWD)/src
SRC=./src
DOCKER=./.docker
DJANGO_SETTINGS_MODULE=config.settings.local


TEST_API=$(SRC)/apps/tests/locust
API_HOST=127.0.0.1
API_PORT=8000


UWSGI_CONFIG_PATH=$(PWD)/src/uwsgi.ini


run.local:
	ulimit -n 4096 &&  python $(SRC)/manage.py runserver 0.0.0.0:8000 --noreload --settings=$(DJANGO_SETTINGS_MODULE)

run.deploy:
	export PYTHONPATH=$(PWD)/src && ulimit -n 4096 && uwsgi --ini $(UWSGI_CONFIG_PATH)


run.db:
	cd $(DOCKER) && sudo docker-compose up -d


migrations:
	python $(PYHTONPATH)/manage.py makemigrations --settings=$(DJANGO_SETTINGS_MODULE)

migrate:
	python $(SRC)/manage.py migrate --settings=$(DJANGO_SETTINGS_MODULE)



# Load Test


api.v1.test.point_earn:
	locust -f $(TEST_API)/v1/test_point_earn_api.py -H http://$(API_HOST):$(API_PORT)

api.v2.test.point_earn:
	locust -f $(TEST_API)/v2/test_point_earn_api.py -H http://$(API_HOST):$(API_PORT)