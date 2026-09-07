from django.conf import settings
from django.db import models


class Conversation(models.Model):
	participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-updated_at',)


class Message(models.Model):
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
	sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
	body = models.TextField(max_length=4000)
	attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	read_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ('created_at',)
