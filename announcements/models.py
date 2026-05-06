from django.db import models
from django.contrib.auth.models import User


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low',    '🟢 Low'),
        ('normal', '🔵 Normal'),
        ('high',   '🟠 High'),
        ('urgent', '🔴 Urgent'),
    ]

    title      = models.CharField(max_length=200)
    body       = models.TextField()
    priority   = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_active  = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title