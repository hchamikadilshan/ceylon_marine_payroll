from django.urls import path
from .views import LoginUserView, MainView, LogoutUserView,MyAccountDetailsView,EditUserAccountDetails,CreateNewUserView


urlpatterns = [
    path('login', LoginUserView.as_view(), name="login_user_url"),
    path('logout', LogoutUserView.as_view(), name="logout_user_url"),
    path('my_account', MyAccountDetailsView.as_view(), name="my_account_view"),
    path('edit_acount_details', EditUserAccountDetails.as_view(), name="edit_acount_details"),
    path('create_new_user', CreateNewUserView.as_view(), name="create_new_user_view"),
    path('', MainView.as_view(), name="main_page_url")
]