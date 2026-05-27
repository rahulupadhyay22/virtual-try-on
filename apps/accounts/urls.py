from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="accounts_register"),
    path("login/", views.login_view, name="accounts_login"),
    path("logout/", views.logout_view, name="accounts_logout"),
    path("profile/", views.profile, name="accounts_profile"),
    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("password-reset/done/", views.password_reset_done, name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("reset/done/", views.password_reset_complete, name="password_reset_complete"),
]
