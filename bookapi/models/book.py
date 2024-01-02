from django.db import models


class Book(models.Model):
    """Database model for tracking events"""

    alien_user = models.ForeignKey(
        "AlienUser", on_delete=models.CASCADE, related_name="books"
    )
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    page_count = models.CharField(max_length=200)
    image_url = models.URLField()
    content = models.CharField(max_length=3000)
    publication_date = models.CharField(max_length=200, default="default_value")
    created_on = models.DateField(auto_now_add=True)
