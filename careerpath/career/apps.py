from django.apps import AppConfig


class CareerConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'career'

    def ready(self):
        import career.signals  # noqa
