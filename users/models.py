from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='user1.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    job_details = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
