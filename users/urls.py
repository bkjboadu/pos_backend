from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import (
    UserLoginView,
    UserProfileUpdateView,
    CustomTokenRefreshView,
    UserListView,
    PasswordChange,
    DeleteAccount,
    LogoutView,
    UserSignupView,
    AdminUserUpdateView
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="lists"),
    path("password_change/", PasswordChange.as_view(), name="passwordchange"),
    path("profile_update/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("delete_account/<uuid:pk>/", DeleteAccount.as_view(), name="delete"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("admin/<uuid:pk>/", AdminUserUpdateView.as_view(), name="admin-user-update"),
]
