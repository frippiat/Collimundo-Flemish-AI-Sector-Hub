from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.sign_up, name="sign_up"),
    path(
        "password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
]
