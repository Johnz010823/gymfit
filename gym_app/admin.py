from django.contrib import admin
from .models import UserProfile, Payment, WorkoutDay, Exercise, WorkoutLog, Attendance


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'membership_status', 'face_registered', 'is_owner', 'date_joined']
    list_filter = ['membership_status', 'face_registered', 'is_owner']
    search_fields = ['user__username', 'user__email', 'user__first_name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'plan', 'payment_date', 'expiry_date']
    list_filter = ['status', 'plan']
    search_fields = ['user__username']


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ['user', 'day', 'muscle_group', 'is_rest_day']
    list_filter = ['day', 'is_rest_day']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'workout_day', 'sets', 'reps', 'is_completed']
    list_filter = ['is_completed']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time_in', 'time_out', 'login_method']
    list_filter = ['date', 'login_method']
    search_fields = ['user__username']


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'exercise_name', 'sets_completed', 'reps_completed']
    list_filter = ['date']
