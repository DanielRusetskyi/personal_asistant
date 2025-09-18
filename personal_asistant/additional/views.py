import json
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Station
from django.shortcuts import render
from .services import get_weather


def weather_view(request):
    city = request.GET.get("city", "Kyiv")  # Місто за замовчуванням
    weather_data = get_weather(city)
    return render(request, "weather.html", {"weather": weather_data,
                                            "active_menu": "main"})


class PlayerView(TemplateView):
    template_name = "player.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["use_proxy"] = getattr(settings, "RADIO_USE_STREAM_PROXY", False)
        return ctx


def stations_json(request):
    qs = Station.objects.filter(is_active=True)
    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(tags__icontains=q) | qs.filter(country__icontains=q)
    data = [
        {
        "name": s.name,
        "slug": s.slug,
        "stream": s.stream_url,
        "website": s.website_url,
        "icon": s.icon_url,
        "country": s.country,
        "tags": [t.strip() for t in s.tags.split(",") if t.strip()],
        }
        for s in qs
    ]
    return JsonResponse({"stations": data})


def play_redirect(request, slug: str):
    station = get_object_or_404(Station, slug=slug, is_active=True)
    use_proxy = getattr(settings, "RADIO_USE_STREAM_PROXY", False)
    if use_proxy:
        return redirect("additional:proxy", slug=slug)
    return redirect(station.stream_url)


