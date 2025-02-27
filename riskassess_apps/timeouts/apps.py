from django.apps import AppConfig


class TimeoutsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'riskassess_apps.timeouts'

    def ready(self):
        import riskassess_apps.timeouts.signals