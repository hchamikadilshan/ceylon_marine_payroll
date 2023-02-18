from django.urls import path
from .views import LoginUserView, MainView, LogoutUserView


urlpatterns = [
    path('login', LoginUserView.as_view(), name="login_user_url"),
    path('logout', LogoutUserView.as_view(), name="logout_user_url"),
    path('', MainView.as_view(), name="main_page_url")
]