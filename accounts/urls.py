from django.urls import path
from . import views
from .views import exercise_viewer

urlpatterns = [
    path('',                views.home,                  name='home'),
    path('dashboard/',      views.dashboard,             name='dashboard'),
    path('logout/',         views.custom_logout,         name='logout'),
    path('profile/',        views.profile_view,          name='profile'),
    path('exercises/',      exercise_viewer,             name='exercise_viewer'),
    path('owner-login/',    views.owner_login,           name='owner_login'),
    # Face
    path('face/register/',         views.face_register,        name='face_register'),
    path('face/register/submit/',  views.face_register_submit, name='face_register_submit'),
    path('face/login/',            views.face_login,           name='face_login'),
    path('face/login/verify/',     views.face_login_verify,    name='face_login_verify'),
    path('exercises/', views.exercise_viewer, name='exercise_viewer'),
    path('exercises/<str:day>/', views.exercise_viewer, name='exercise_viewer_day'),
]
