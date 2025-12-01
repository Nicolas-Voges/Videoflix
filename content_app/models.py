from django.db import models

class StatusType(models.TextChoices):   
    """ Enumeration of possible processing statuses for videos. """
    
    pending = 'pending', 'pending'
    processing = 'processing', 'processing'
    ready = 'ready', 'ready'
    failed = 'failed', 'failed'

class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.FileField(upload_to='video/thumbnails/')
    category = models.CharField(max_length=100)
    original_file = models.FileField(upload_to='video/originals/')
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.pending)

    def __str__(self):
        return f"Title:{self.title}, ID:{self.id}, status:{self.status}"