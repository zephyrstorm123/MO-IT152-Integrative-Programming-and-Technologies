from django.urls import path
from . import views
from .views import UserLogin, UserLogout

urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
]