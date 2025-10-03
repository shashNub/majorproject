from django.urls import path
from . import views

urlpatterns = [
    path('', views.first, name='index'),
    path('home', views.index, name='home'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle_wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
]