from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json



class UserProfile(models.Model):
    MEMBERSHIP_STATUS = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_photo_url = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    face_registered = models.BooleanField(default=False)
    face_encoding_path = models.CharField(max_length=500, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.membership_status}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('overdue', 'Overdue'),
    ]
    PLAN_CHOICES = [
        ('monthly', 'Monthly - ₱500'),
        ('quarterly', 'Quarterly - ₱1,400'),
        ('annual', 'Annual - ₱5,000'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='monthly')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    payment_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.plan}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    class Meta:
        ordering = ['-created_at']


class WorkoutDay(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_days')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    muscle_group = models.CharField(max_length=100)
    is_rest_day = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.day} - {self.muscle_group}"

    class Meta:
        unique_together = ['user', 'day']


class Exercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=200)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=12)
    weight_kg = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.sets}x{self.reps}"


class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_logs')
    date = models.DateField(default=timezone.now)
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    exercise_name = models.CharField(max_length=200)
    sets_completed = models.IntegerField(default=0)
    reps_completed = models.IntegerField(default=0)
    weight_kg = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise_name} - {self.date}"

    class Meta:
        ordering = ['-date']


class Attendance(models.Model):
    LOGIN_METHOD = [
        ('face', 'Face Recognition'),
        ('manual', 'Manual'),
        ('google', 'Google Login'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(default=timezone.now)
    time_out = models.TimeField(null=True, blank=True)
    login_method = models.CharField(max_length=20, choices=LOGIN_METHOD, default='face')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        ordering = ['-date', '-time_in']

    @property
    def duration(self):
        if self.time_out:
            from datetime import datetime, date
            dt_in = datetime.combine(date.today(), self.time_in)
            dt_out = datetime.combine(date.today(), self.time_out)
            diff = dt_out - dt_in
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "Still in"
