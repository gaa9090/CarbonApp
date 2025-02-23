from django.urls import path
from .views import (profile_view, authenticate_view, the_logout_view)

app_name = 'profile'

urlpatterns = [
    path("profile", profile_view, name="profile"),
    path("login/<int:state>", authenticate_view, name="login"),
    path('logout',the_logout_view, name="logout")

]




