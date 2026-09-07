from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ('id', 'updated_at')
	filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ('sender', 'conversation', 'created_at', 'read_at')
	search_fields = ('body', 'sender__username')
