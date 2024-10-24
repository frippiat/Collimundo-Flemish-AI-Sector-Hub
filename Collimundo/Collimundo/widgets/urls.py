from django.urls import path

from . import views

urlpatterns = [
    path("", views.widget_controller, name="widgets"),
]
