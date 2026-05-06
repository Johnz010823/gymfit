from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

PLAN_CHOICES = [
    ('daily',     'Daily'),
    ('monthly',   'Monthly'),
    ('quarterly', 'Quarterly'),
    ('annual',    'Annual'),
]

STATUS_CHOICES = [
    ('paid',    'Paid'),
    ('pending', 'Pending'),
    ('expired', 'Expired'),
]

class Payment(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    plan         = models.CharField(max_length=20, choices=PLAN_CHOICES, default='monthly')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(default=datetime.date.today)
    expiry_date  = models.DateField(default=datetime.date.today)
    created_at   = models.DateTimeField(default=timezone.now)

    def __str__(self):
        username = self.user.username if self.user else "No User"
        return f"{username} - {self.plan} ({self.status})"