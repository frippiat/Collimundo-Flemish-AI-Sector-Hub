from django.urls import path

from . import views

urlpatterns = [
    path("", views.follow, name="follow"),
    path("company", views.company_page, name="company_page"),
    path("company/edit", views.company_page_edit, name="company_page_edit"),
]
