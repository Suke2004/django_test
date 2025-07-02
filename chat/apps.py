from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Ensures auto-incrementing primary keys use BigAutoField
    name = 'chat'  # This must match your app directory name
