from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegistrationView,
    LoginView,
    VerifyEmail,
    PasswordResetRequest,
    PasswordResetConfirm,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("verify-email/", VerifyEmail.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "password-reset-request/",
        PasswordResetRequest.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirm.as_view(),
        name="password-reset-confirm",
    ),
]