from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'riskassess_apps.users'

    def ready(self):
        import riskassess_apps.users.signals