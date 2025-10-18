"""
URL configuration for personal_asistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import FileResponse, HttpResponseNotFound
from django.contrib.staticfiles.storage import staticfiles_storage

from . import settings


def service_worker(request):
    try:
        p = staticfiles_storage.path("sw.js")
        return FileResponse(open(p, "rb"), content_type="application/javascript", headers={"Cache-Control":"no-cache"})
    except Exception:
        return HttpResponseNotFound("sw.js not found")


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "sw.js",
        TemplateView.as_view(
            template_name="sw.js",
            content_type="application/javascript",
        ),
        name="service_worker",
    ),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="main.html",
                                  extra_context={'active_menu': 'main', 'active_page': 'main'}), name='main'),
    path('noteapp/', include('noteapp.urls', namespace='noteapp')),
    path('account/', include('accounts.urls', namespace='account')),
    path('accounts/', include('allauth.urls')),
    path('additional/', include('additional.urls')),
    path("settings/", include("preferences.urls", namespace="preferences")),
    path("chat/", include("chat.urls", namespace="chat")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

