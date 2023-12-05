from django.db import models


class Book(models.Model):
    """Database model for tracking events"""

    alien_user = models.ForeignKey(
        "AlienUser", on_delete=models.CASCADE, related_name="books"
    )
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publication_date = models.DateField(auto_now_add=True)
    image_url = models.URLField()
    content = models.CharField(max_length=200)
