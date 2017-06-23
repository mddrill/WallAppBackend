from django.db import models

class Post(models.Model):

    """
    Each post will have an author, a date and time it was posted at, and text which it contains
    """
    posted_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    author = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE)

    class Meta:
        ordering = ('posted_at',)