import pytest


@pytest.fixture
def django_db_setup():
    """Avoid creating/setting up the test database"""

    from django.conf import settings
    settings.DATABASES['default']['NAME'] = 'points_db'

    settings.DEBUG = True
