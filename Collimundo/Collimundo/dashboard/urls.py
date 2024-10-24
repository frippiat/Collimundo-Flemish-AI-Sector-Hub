from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("search/", views.search_engine, name="search_engine"),
    path("edit/", views.dashboard_editor, name="dashboard_editor"),
]
