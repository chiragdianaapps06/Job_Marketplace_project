from django.apps import AppConfig



class JobassignmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobassignment'


    def ready(self):
        import jobassignment.signals