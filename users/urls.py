from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('user-login', views.loginUser, name="login"),
    path('user-logout', views.logoutUser, name="logout"),
    path('create-account', views.registerUser, name="register"),
    path('your-profile', views.showProfile, name="yourProfile"),
    path('verify-otp', views.verify_otp, name="verify_otp"),
    path('resend-otp', views.resend_otp, name="resend_otp"),
    path('firebase/start-verify', views.firebase_start_verify, name="firebase_start_verify"),
    path('firebase/verify-email', views.firebase_verify_email_page, name="firebase_verify_email_page"),
    path('auth/firebase/email-verified/', views.firebase_email_verified, name="firebase_email_verified"),
]