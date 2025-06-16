from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps'

    def ready(self):
        super().ready()
        from src.apps.batch.scheduler import on_start
        on_start()
