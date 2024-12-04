from django.urls import path
from . import views

urlpatterns = [
    path('', views.users, name="users"),
    path('profile/<str:pk>/', views.user_profile, name="user-profile"),
    path('edit-account/', views.edit_account, name="edit-account"),

]