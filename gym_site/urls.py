from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/',          admin.site.urls),
    path('',                include('accounts.urls')),
    path('workouts/',       include('workouts.urls')),
    path('attendance/',     include('attendance.urls')),
    path('announcements/',  include('announcements.urls')),
    path('owner/',          include('owner.urls')),
    path('accounts/',       include('allauth.urls')),

]