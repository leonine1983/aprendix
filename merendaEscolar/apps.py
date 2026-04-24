from django.apps import AppConfig


class MerendaescolarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'merendaEscolar'

    def ready(self):
        import merendaEscolar.notifications
