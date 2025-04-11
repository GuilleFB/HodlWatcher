from django.urls import path

from .views import FAQDetailView, FAQListView

urlpatterns = [
    path("", FAQListView.as_view(), name="faq_list"),
    path("<slug:slug>/", FAQDetailView.as_view(), name="faq_detail"),
]
