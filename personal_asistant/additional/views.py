
from django.shortcuts import render
from .services import get_weather


def weather_view(request):
    city = request.GET.get("city", "Kyiv")  # Місто за замовчуванням
    weather_data = get_weather(city)
    return render(request, "weather.html", {"weather": weather_data,
                                            "active_menu": "main"})

