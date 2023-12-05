from django.db import models


class Genre(models.Model):
    """Database model for tracking events"""

    label = models.CharField(max_length=200)
