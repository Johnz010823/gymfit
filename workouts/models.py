from django.db import models
from django.contrib.auth.models import User


class ExerciseLibrary(models.Model):
    CATEGORY_CHOICES = [
        ('Chest', 'Chest'),
        ('Shoulder', 'Shoulder'),
        ('Back', 'Back'),
        ('Biceps', 'Biceps & Forearms'),
        ('Triceps', 'Triceps'),
        ('Legs', 'Legs'),
        ('Core', 'Core & Cardio'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name


class WorkoutDay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    is_rest_day = models.BooleanField(default=False)
    muscle_group = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'day')

    def __str__(self):
        return f"{self.user.username} - {self.day}"


class Exercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, blank=True, null=True)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    weight_kg = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name