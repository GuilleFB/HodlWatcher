from django.views.generic import ListView, DetailView
from .models import FAQ


class FAQListView(ListView):
    model = FAQ
    template_name = "faq_list.html"
    context_object_name = "faqs"

    def get_queryset(self):
        return FAQ.objects.filter(is_active=True).order_by("order")


class FAQDetailView(DetailView):
    model = FAQ
    template_name = "faq_detail.html"
    context_object_name = "faq"

    def get_queryset(self):
        return FAQ.objects.filter(is_active=True)
