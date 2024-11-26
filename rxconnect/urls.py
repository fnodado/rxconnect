
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include

from users import views

def dashboard(request):
    return render(request, 'dashboard.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name="dashboard"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('register/', views.register_user, name="register_user"),


    path('users/', include('users.urls')), ##includes the users app
]
