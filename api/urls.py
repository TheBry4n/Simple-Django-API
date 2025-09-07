from django.urls import path
from .views import *

urlpatterns = [
    path("users", user_list, name="user-list"),
    path("user/create", account_create, name="account-create"),
    path("user/login", login, name="login"),
    path("user/refresh", refresh_token, name="refresh-token"),
    path("user/logout", logout, name="logout"),
]