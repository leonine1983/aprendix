from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'  # ⚠️ IMPORTANTE: Se a pasta do seu app tiver outro nome, mude 'core' aqui.

    def ready(self):
        # Importa os signals para que sejam registrados ao iniciar o app
        import core.signals  # ⚠️ IMPORTANTE: Mude 'core' se o nome da pasta for diferente.