from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.utils.translation import gettext as _
from django.views.i18n import JavaScriptCatalog

from main import views as main_views

from .sitemaps import StaticViewSitemap, UserViewSitemap, WatchdogViewSitemap
from django.conf.urls.i18n import i18n_patterns

admin.site.site_header = _("HodlWatcher Administration")
admin.site.site_title = _("HodlWatcher Admin")

sitemaps = {
    "static": StaticViewSitemap,
    "user": UserViewSitemap,
    "watchdog": WatchdogViewSitemap,
}

urlpatterns = [
    path("", include("django_prometheus.urls")),
    path("jsi18/", JavaScriptCatalog.as_view(), name="jsi18n"),
    path("health/", include("health_check.urls")),
    path("yubin/", include("django_yubin.urls")),
    path("robots.txt", include("robots.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

urlpatterns += i18n_patterns(
    path("", main_views.IndexView.as_view(), name="home"),
    path("faq/", include("faq.urls")),
    path("admin/", admin.site.urls),
    path("", include("alertas_bot.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("allauth.urls")),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
