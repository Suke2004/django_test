from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'short_message', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message',)
    readonly_fields = ('sender', 'message', 'timestamp')

    def short_message(self, obj):
        return (obj.message[:60] + '...') if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Message'
