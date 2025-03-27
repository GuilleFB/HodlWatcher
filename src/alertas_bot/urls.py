from django.urls import path

from .views import (
    BuscadorView,
    ConfiguracionUpdateView,
    ContactView,
    ProfileUpdateView,
    ProjectsView,
    ResumeView,
    delete_account,
)

urlpatterns = [
    path("configurar-rate-fee/", ConfiguracionUpdateView.as_view(), name="modificar_rate_fee"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("projects/", ProjectsView.as_view(), name="projects"),
    path("resume/", ResumeView.as_view(), name="resume"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("delete-account/", delete_account, name="delete_account"),
    path("buscador/", BuscadorView.as_view(), name="buscador"),
]
