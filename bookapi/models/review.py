from django.db import models


class Review(models.Model):
    """Database model for tracking events"""

    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="reviews")
    alien_user = models.ForeignKey(
        "AlienUser", on_delete=models.CASCADE, related_name="reviews"
    )
    content = models.CharField(max_length=3000)
    created_on = models.DateField(auto_now_add=True)
