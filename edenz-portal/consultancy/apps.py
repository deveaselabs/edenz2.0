from django.apps import AppConfig


class ConsultancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consultancy'
    
    def ready(self):
        import consultancy.signals
