from django.urls import path
from .views import (
    UserLoginView,
    UserProfileUpdateView,
    CustomTokenRefreshView,
    UserLists,
    PasswordChange,
    DeleteAccount,
    LogoutView,
    UserSignupView
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("users/", UserLists.as_view(), name="lists"),
    path("password_change/", PasswordChange.as_view(), name="passwordchange"),
    path("profile_update/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("delete_account/", DeleteAccount.as_view(), name="delete"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
