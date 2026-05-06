from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.owner_dashboard,   name='owner_dashboard'),
    path('member/<int:user_id>/',  views.member_detail,     name='member_detail'),
    path('payment/<int:user_id>/', views.update_payment,    name='update_payment'),
    path('attendance/',            views.owner_attendance,  name='owner_attendance'),
    path('announcements/create/',  views.owner_create_announcement, name='owner_create_announcement'),
]