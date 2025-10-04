from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = 'E-commerce API'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        import api.signals
