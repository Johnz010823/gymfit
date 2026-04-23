from django.urls import path
from . import views
from .views import exercise_viewer

urlpatterns = [
    # ── General ───────────────────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('exercises/', exercise_viewer, name='exercise_viewer'),


    # ── Face ──────────────────────────────────────────────────────────────────
    path('face/register/', views.face_register, name='face_register'),
    path('face/register/submit/', views.face_register_submit, name='face_register_submit'),
    path('face/login/', views.face_login, name='face_login'),
    path('face/login/verify/', views.face_login_verify, name='face_login_verify'),

    # ── Attendance ────────────────────────────────────────────────────────────
    path('attendance/', views.attendance_list, name='attendance'),
    path('attendance/checkout/', views.mark_checkout, name='mark_checkout'),

    # ── Workouts ──────────────────────────────────────────────────────────────
    path('workouts/', views.workout_plan, name='workout_plan'),
    path('workouts/suggest/', views.suggest_workout, name='suggest_workout'),
    path('workouts/toggle/<int:exercise_id>/', views.toggle_exercise, name='toggle_exercise'),
    path('workouts/add/<str:day>/', views.add_exercise, name='add_exercise'),
    path('workouts/edit/<int:exercise_id>/', views.edit_exercise, name='edit_exercise'),
    path('workouts/delete/<int:exercise_id>/', views.delete_exercise, name='delete_exercise'),  # ← was missing

    # ── Workout Library (new) ─────────────────────────────────────────────────
    path('workouts/rest/<str:day>/', views.toggle_rest_day, name='toggle_rest_day'),
    path('workouts/library/<str:day>/', views.exercise_library_view, name='exercise_library'),
    path('workouts/library/<str:day>/add/', views.add_from_library, name='add_from_library'),

    # ── Owner ─────────────────────────────────────────────────────────────────
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/member/<int:user_id>/', views.member_detail, name='member_detail'),
    path('owner/payment/<int:user_id>/', views.update_payment, name='update_payment'),
    path('owner/attendance/', views.owner_attendance, name='owner_attendance'),
    path('owner-login/', views.owner_login, name='owner_login'),



]