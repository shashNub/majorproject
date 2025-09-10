from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_details = models.JSONField()  # Store job details as JSON
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_details.get('Name', 'Unknown Job')}"
