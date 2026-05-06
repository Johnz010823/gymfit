from django.urls import path
from . import views

urlpatterns = [
    path('',                           views.workout_plan,          name='workout_plan'),
    path('suggest/',                   views.suggest_workout,       name='suggest_workout'),
    path('toggle/<int:exercise_id>/',  views.toggle_exercise,       name='toggle_exercise'),
    path('add/<str:day>/',             views.add_exercise,          name='add_exercise'),
    path('edit/<int:exercise_id>/',    views.edit_exercise,         name='edit_exercise'),
    path('delete/<int:exercise_id>/',  views.delete_exercise,       name='delete_exercise'),
    path('rest/<str:day>/',            views.toggle_rest_day,       name='toggle_rest_day'),
    path('library/<str:day>/',         views.exercise_library_view, name='exercise_library'),
    path('library/<str:day>/add/',     views.add_from_library,      name='add_from_library'),
    path('library/add/<str:day>/<int:ex_id>/', views.add_exercise_from_library, name='add_exercise_from_library'),

]