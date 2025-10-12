from datetime import datetime
import json
from time import timezone

import requests
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Station
from django.shortcuts import render
from .services import get_weather
from django.views.decorators.http import require_GET, require_POST


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


def rates_page(request):
    """
    Рендерить вашу сторінку з шаблоном курсів валют.
    У шаблоні JS звернеться до нашого локального API /additional/api/pb-rates/
    """
    return render(request, "rates.html", {
        "now": datetime.now(),
    })


def _normalize_hist_rows(data):
    """
    Нормалізує відповідь історичного API:
    [{"ccy":"USD","base_ccy":"UAH","buy":..., "sale":...}, ...]
    """
    rows = []
    for x in data.get("exchangeRate", []):
        ccy  = x.get("currency")
        base = x.get("baseCurrency")
        if not ccy or not base:
            continue
        buy  = x.get("purchaseRate") or x.get("purchaseRateNB")
        sale = x.get("saleRate")     or x.get("saleRateNB")
        rows.append({"ccy": ccy, "base_ccy": base, "buy": buy, "sale": sale})
    return rows


def _parse_date_param(request):
    """Приймає date у форматі YYYY-MM-DD | YYYYMMDD | DD.MM.YYYY -> повертає dd.mm.yyyy або None."""
    raw = (request.GET.get("date") or "").strip()
    if not raw:
        return None
    try:
        if "-" in raw:
            return datetime.strptime(raw, "%Y-%m-%d").strftime("%d.%m.%Y")
        elif len(raw) == 8 and raw.isdigit():
            return datetime.strptime(raw, "%Y%m%d").strftime("%d.%m.%Y")
        else:
            # вже dd.mm.yyyy
            datetime.strptime(raw, "%d.%m.%Y")
            return raw
    except ValueError:
        return None


def _parse_curr_list(request):
    raw = (request.GET.get("curr") or request.GET.get("symbols") or "").strip()
    if not raw:
        return ["USD", "EUR", "PLN"]
    parts = raw.replace(";", ",").split(",")
    return [p.strip().upper() for p in parts if p.strip()]


@require_GET
def pb_currencies_api(request):
    """
    Повертає відсортований список доступних валют, наприклад ["USD","EUR","PLN",...].
    Якщо передано ?date=..., беремо історичне джерело; інакше — поточне.
    """
    target_date = _parse_date_param(request)

    if target_date:
        # Історичні
        url = "https://api.privatbank.ua/p24api/exchange_rates"
        params = {"json": "", "date": target_date}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        codes = sorted({(x.get("currency") or "").upper() for x in data.get("exchangeRate", []) if x.get("currency")})
        return JsonResponse(codes, safe=False)

    # Поточні
    url = "https://api.privatbank.ua/p24api/pubinfo"
    params = {"json": "", "exchange": "", "coursid": 5}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    codes = sorted({(x.get("ccy") or "").upper() for x in data if x.get("ccy")})
    return JsonResponse(codes, safe=False)


@require_GET
def pb_rates_api(request):
    """
    Повертає курси. Параметри:
      - date: YYYY-MM-DD | YYYYMMDD | DD.MM.YYYY (опційно)
      - curr: CSV-список валют (напр. USD,EUR,PLN) — фільтр (опційно)
    """
    target_date = _parse_date_param(request)
    allowed = _parse_curr_list(request)

    if target_date:
        url = "https://api.privatbank.ua/p24api/exchange_rates"
        params = {"json": "", "date": target_date}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        rows = _normalize_hist_rows(r.json())
    else:
        url = "https://api.privatbank.ua/p24api/pubinfo"
        params = {"json": "", "exchange": "", "coursid": 5}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        rows = r.json()

    if allowed:
        allowed = set(allowed)
        rows = [x for x in rows if (x.get("ccy") or "").upper() in allowed]

    return JsonResponse(rows, safe=False)

