from django.urls import path
from . import views

urlpatterns = [
    path("",views.base_art,name="base_art"),
    path('log_reg_art/', views.log_reg_art, name='log_reg_art'),
    path('superuser_art/', views.superuser_art, name='superuser_art'),
    path('user_art/', views.user_art, name='user_art'),
    path('chat/<str:username>/', views.chat_art, name='chat_room'),
    path('logout/', views.logout_art, name='logout'),

]
