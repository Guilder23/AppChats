from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	display_name = models.CharField(max_length=80, blank=True)
	bio = models.CharField(max_length=160, blank=True)
	avatar = models.FileField(upload_to='avatars/', blank=True, null=True)
	last_seen = models.DateTimeField(null=True, blank=True)

	@property
	def name(self):
		return self.display_name or self.user.get_full_name() or self.user.username
