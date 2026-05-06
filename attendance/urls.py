from django.urls import path
from . import views

urlpatterns = [
    path('',          views.attendance_list, name='attendance'),
    path('checkout/', views.mark_checkout,   name='mark_checkout'),
]