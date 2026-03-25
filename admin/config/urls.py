from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

from api.views import health_check

urlpatterns = [
    path("api/", include("api.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("django-rq/", include("django_rq.urls")),
    path("health/", health_check),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
