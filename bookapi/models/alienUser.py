from django.db import models
from django.contrib.auth.models import User


class AlienUser(models.Model):
    """Database model for tracking events"""

    bio = models.CharField(max_length=3000)
    profile_image_url = models.URLField()
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="alien_user"
    )
