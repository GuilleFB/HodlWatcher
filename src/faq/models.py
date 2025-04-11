from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Pregunta")
    answer = RichTextField(verbose_name="Respuesta")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    related_questions = models.ManyToManyField(
        "self", blank=True, symmetrical=False, verbose_name="Preguntas relacionadas", related_name="related_to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Pregunta Frecuente"
        verbose_name_plural = "Preguntas Frecuentes"

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.question)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("faq_detail", kwargs={"slug": self.slug})


class FAQCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["order"]
        verbose_name = "Categoría de FAQ"
        verbose_name_plural = "Categorías de FAQ"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
